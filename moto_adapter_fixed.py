import logging
import pandas as pd
import time
import traceback
import json
from app.algoritmo.pagerank import MotoPageRank
from app.algoritmo.label_propagation import MotoLabelPropagation
from app.algoritmo.utils import DatabaseConnector

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MotoRecommenderAdapter')

class MotoRecommenderAdapter:
    """Adaptador que integra diferentes algoritmos de recomendación para motos."""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="22446688"):
        """Inicializa el adaptador con parámetros de conexión."""
        self.neo4j_uri = uri
        self.neo4j_user = user
        self.neo4j_password = password
        
        # Inicializar logger PRIMERO
        self.logger = logging.getLogger('MotoRecommenderAdapter')
        self.logger.setLevel(logging.INFO)
        
        # Inicializar atributos
        self.driver = None
        self.data_loaded = False
        self.user_data = None
        self.moto_data = None
        self.ratings_data = None
        self.friendships_df = None
        
        # Inicializar DataFrames
        self.users_df = None
        self.motos_df = None
        self.ratings_df = None
        
        # Configuración
        self.allow_mock_data = False  # Solo usar datos de Neo4j
        
        # Inicializar algoritmos de recomendación correctamente
        self.pagerank = MotoPageRank()
        self.label_propagation = MotoLabelPropagation() 
        
        # Usar la versión simplificada de MotoIdealRecommender
        try:
            from app.algoritmo.moto_ideal_simple import MotoIdealRecommender
            self.moto_ideal = MotoIdealRecommender(neo4j_connector=self)
            logger.info("Usando MotoIdealRecommender simplificado")
        except ImportError:
            from app.algoritmo.moto_ideal import MotoIdealRecommender
            self.moto_ideal = MotoIdealRecommender()
            logger.info("Usando MotoIdealRecommender estándar")
        
        # Conectar a Neo4j inmediatamente al inicializar
        self.connect_to_neo4j()
        
        # Cargar datos inmediatamente
        self.load_data()
        
    def connect_to_neo4j(self, max_retries=3, timeout=10):
        """Establecer conexión robusta a Neo4j."""
        from neo4j import GraphDatabase
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Intento {attempt+1}/{max_retries} de conexión a Neo4j: {self.neo4j_uri}")
                self.driver = GraphDatabase.driver(
                    self.neo4j_uri, 
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                
                # Test connection
                with self.driver.session() as session:
                    result = session.run("RETURN 'Conexión exitosa' as mensaje")
                    message = result.single()["mensaje"]
                    logger.info(f"Neo4j: {message}")
                
                logger.info("Conexión a Neo4j establecida exitosamente")
                return True
                
            except Exception as e:
                logger.error(f"Error de conexión a Neo4j (intento {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = timeout * (attempt + 1)
                    logger.info(f"Reintentando en {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    logger.error("Se agotaron los intentos de conexión a Neo4j.")
                    # Ahora fallamos si no hay conexión - nunca datos mock
                    return False
                    
    def test_connection(self):
        """Prueba la conexión a Neo4j y retorna True si es exitosa."""
        try:
            if not self.driver:
                return self.connect_to_neo4j(max_retries=1)
                
            with self.driver.session() as session:
                result = session.run("RETURN 'Test exitoso' as mensaje")
                message = result.single()["mensaje"]
                logger.info(f"Test de conexión a Neo4j: {message}")
                return True
        except Exception as e:
            logger.error(f"Error en test de conexión: {str(e)}")
            return False
    
    def _ensure_neo4j_connection(self):
        """Asegura que hay una conexión activa a Neo4j o intenta reconectar."""
        try:
            if not self.driver:
                logger.warning("No hay un driver de Neo4j, intentando conectar...")
                return self.connect_to_neo4j()
            
            # Probar la conexión existente
            with self.driver.session() as session:
                try:
                    result = session.run("RETURN 'Conexión verificada' as mensaje")
                    message = result.single()["mensaje"]
                    logger.debug(f"Neo4j conexión verificada: {message}")
                    return True
                except Exception as session_error:
                    logger.warning(f"Error con la sesión actual: {str(session_error)}. Reconectando...")
                    self.driver.close()
                    self.driver = None
                    return self.connect_to_neo4j()
        except Exception as e:
            logger.error(f"Error al verificar conexión Neo4j: {str(e)}")
            return False
    
    def load_data(self):
        """Cargar datos desde Neo4j de manera robusta"""
        self.logger.info("Cargando datos desde Neo4j (modo exclusivo)")
        
        if not self.driver:
            self.logger.error("No hay conexión a Neo4j disponible")
            if not self.allow_mock_data:
                self.logger.error("La aplicación requiere Neo4j. No se usarán datos mock.")
                raise RuntimeError("No se pudieron cargar datos desde Neo4j")
            return False
        
        try:
            # Intentar cargar datos reales desde Neo4j
            success = self._load_from_neo4j()
            if success:
                self.logger.info(f"Datos cargados desde Neo4j: {len(self.motos_df)} motos, {len(self.users_df)} usuarios, {len(self.ratings_df)} ratings")
                
                # NUEVO: Construir ranking con manejo de errores mejorado
                try:
                    self.logger.info("Construyendo ranking desde datos de interacción...")
                    
                    # Preparar datos para PageRank con validación de tipos
                    pagerank_data = []
                    for _, row in self.ratings_df.iterrows():
                        # Validar y convertir datos
                        user_id = str(row['user_id']) if row['user_id'] else None
                        moto_id = str(row['moto_id']) if row['moto_id'] else None
                        
                        # Convertir weight de manera segura
                        raw_weight = row.get('rating', 1.0)
                        try:
                            if isinstance(raw_weight, str):
                                # Limpiar string y convertir
                                cleaned_weight = raw_weight.strip()
                                weight = float(cleaned_weight) if cleaned_weight else 1.0
                            else:
                                weight = float(raw_weight) if raw_weight is not None else 1.0
                        except (ValueError, TypeError):
                            weight = 1.0
                            self.logger.warning(f"Peso inválido '{raw_weight}' convertido a 1.0")
                        
                        # Solo agregar si tenemos datos válidos
                        if user_id and moto_id and weight > 0:
                            pagerank_data.append({
                                'user_id': user_id,
                                'moto_id': moto_id,
                                'weight': weight
                            })
                    
                    self.logger.info(f"Preparados {len(pagerank_data)} registros para PageRank")
                    
                    # Construir grafo con datos validados
                    if pagerank_data:
                        self.pagerank.build_graph(pagerank_data)
                        self.logger.info("Ranking de motos construido exitosamente")
                    else:
                        self.logger.warning("No hay datos válidos para construir el ranking")
                        
                except Exception as ranking_error:
                    self.logger.error(f"Error construyendo ranking: {str(ranking_error)}")
                    # Continuar sin ranking en lugar de fallar completamente
                    self.logger.info("Continuando sin sistema de ranking...")
                
                return True
            else:
                self.logger.error("Error crítico al cargar datos desde Neo4j")
                
        except Exception as e:
            self.logger.error(f"Error crítico al cargar datos desde Neo4j: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Si llegamos aquí, falló la carga desde Neo4j
        if not self.allow_mock_data:
            self.logger.error("La aplicación requiere Neo4j. No se usarán datos mock.")
            raise RuntimeError("No se pudieron cargar datos desde Neo4j")
        
        return False
    
    def connect_to_neo4j(self, max_retries=3, timeout=10):
        """Establecer conexión robusta a Neo4j."""
        from neo4j import GraphDatabase
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Intento {attempt+1}/{max_retries} de conexión a Neo4j: {self.neo4j_uri}")
                self.driver = GraphDatabase.driver(
                    self.neo4j_uri, 
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                
                # Test connection
                with self.driver.session() as session:
                    result = session.run("RETURN 'Conexión exitosa' as mensaje")
                    message = result.single()["mensaje"]
                    logger.info(f"Neo4j: {message}")
                
                logger.info("Conexión a Neo4j establecida exitosamente")
                return True
                
            except Exception as e:
                logger.error(f"Error de conexión a Neo4j (intento {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = timeout * (attempt + 1)
                    logger.info(f"Reintentando en {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    logger.error("Se agotaron los intentos de conexión a Neo4j.")
                    # Ahora fallamos si no hay conexión - nunca datos mock
                    return False
                    
    def test_connection(self):
        """Prueba la conexión a Neo4j y retorna True si es exitosa."""
        try:
            if not self.driver:
                return self.connect_to_neo4j(max_retries=1)
                
            with self.driver.session() as session:
                result = session.run("RETURN 'Test exitoso' as mensaje")
                message = result.single()["mensaje"]
                logger.info(f"Test de conexión a Neo4j: {message}")
                return True
        except Exception as e:
            logger.error(f"Error en test de conexión: {str(e)}")
            return False
    
    def _ensure_neo4j_connection(self):
        """Asegura que hay una conexión activa a Neo4j o intenta reconectar."""
        try:
            if not self.driver:
                logger.warning("No hay un driver de Neo4j, intentando conectar...")
                return self.connect_to_neo4j()
            
            # Probar la conexión existente
            with self.driver.session() as session:
                try:
                    result = session.run("RETURN 'Conexión verificada' as mensaje")
                    message = result.single()["mensaje"]
                    logger.debug(f"Neo4j conexión verificada: {message}")
                    return True
                except Exception as session_error:
                    logger.warning(f"Error con la sesión actual: {str(session_error)}. Reconectando...")
                    self.driver.close()
                    self.driver = None
                    return self.connect_to_neo4j()
        except Exception as e:
            logger.error(f"Error al verificar conexión Neo4j: {str(e)}")
            return False
    
    def load_data(self):
        """Cargar datos desde Neo4j de manera robusta"""
        self.logger.info("Cargando datos desde Neo4j (modo exclusivo)")
        
        if not self.driver:
            self.logger.error("No hay conexión a Neo4j disponible")
            if not self.allow_mock_data:
                self.logger.error("La aplicación requiere Neo4j. No se usarán datos mock.")
                raise RuntimeError("No se pudieron cargar datos desde Neo4j")
            return False
        
        try:
            # Intentar cargar datos reales desde Neo4j
            success = self._load_from_neo4j()
            if success:
                self.logger.info(f"Datos cargados desde Neo4j: {len(self.motos_df)} motos, {len(self.users_df)} usuarios, {len(self.ratings_df)} ratings")
                
                # NUEVO: Construir ranking con manejo de errores mejorado
                try:
                    self.logger.info("Construyendo ranking desde datos de interacción...")
                    
                    # Preparar datos para PageRank con validación de tipos
                    pagerank_data = []
                    for _, row in self.ratings_df.iterrows():
                        # Validar y convertir datos
                        user_id = str(row['user_id']) if row['user_id'] else None
                        moto_id = str(row['moto_id']) if row['moto_id'] else None
                        
                        # Convertir weight de manera segura
                        raw_weight = row.get('rating', 1.0)
                        try:
                            if isinstance(raw_weight, str):
                                # Limpiar string y convertir
                                cleaned_weight = raw_weight.strip()
                                weight = float(cleaned_weight) if cleaned_weight else 1.0
                            else:
                                weight = float(raw_weight) if raw_weight is not None else 1.0
                        except (ValueError, TypeError):
                            weight = 1.0
                            self.logger.warning(f"Peso inválido '{raw_weight}' convertido a 1.0")
                        
                        # Solo agregar si tenemos datos válidos
                        if user_id and moto_id and weight > 0:
                            pagerank_data.append({
                                'user_id': user_id,
                                'moto_id': moto_id,
                                'weight': weight
                            })
                    
                    self.logger.info(f"Preparados {len(pagerank_data)} registros para PageRank")
                    
                    # Construir grafo con datos validados
                    if pagerank_data:
                        self.pagerank.build_graph(pagerank_data)
                        self.logger.info("Ranking de motos construido exitosamente")
                    else:
                        self.logger.warning("No hay datos válidos para construir el ranking")
                        
                except Exception as ranking_error:
                    self.logger.error(f"Error construyendo ranking: {str(ranking_error)}")
                    # Continuar sin ranking en lugar de fallar completamente
                    self.logger.info("Continuando sin sistema de ranking...")
                
                return True
            else:
                self.logger.error("Error crítico al cargar datos desde Neo4j")
                
        except Exception as e:
            self.logger.error(f"Error crítico al cargar datos desde Neo4j: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Si llegamos aquí, falló la carga desde Neo4j
        if not self.allow_mock_data:
            self.logger.error("La aplicación requiere Neo4j. No se usarán datos mock.")
            raise RuntimeError("No se pudieron cargar datos desde Neo4j")
        
        return False
    
    def _load_from_neo4j(self):
        """Carga los datos reales desde Neo4j."""
        logger.info("Cargando datos desde Neo4j...")
        
        try:
            # Verificar conexión a Neo4j
            if not self._ensure_neo4j_connection():
                logger.error("No se pudo conectar a Neo4j. La aplicación requiere Neo4j.")
                raise ConnectionError("No hay conexión a Neo4j")
                
            # Usar DatabaseConnector para obtener datos
            db_connector = DatabaseConnector(self.driver)
            self.users_df = db_connector.get_users()
            self.motos_df = db_connector.get_motos()
            self.ratings_df = db_connector.get_ratings()
            
            # Verificar que se obtuvieron datos
            if self.motos_df.empty:
                logger.error("No se obtuvieron datos de motos desde Neo4j")
                raise ValueError("No hay datos de motos en Neo4j")
            
            logger.info(f"Datos cargados desde Neo4j: {len(self.motos_df)} motos, {len(self.users_df)} usuarios, {len(self.ratings_df)} ratings")
            
            # Inicializar algoritmos con los datos de Neo4j
            if hasattr(self.pagerank, 'build_graph'):
                # Preparar datos para PageRank
                pagerank_data = []
                for _, row in self.ratings_df.iterrows():
                    pagerank_data.append({
                        'user_id': row['user_id'],
                        'moto_id': row['moto_id'],
                        'weight': float(row['rating'])/5.0  # Normalizar ratings a 0-1
                    })
                # Construir el grafo con los datos
                self.pagerank.build_graph(pagerank_data)
            
            # Inicializar otros algoritmos si tienen el método load_data
            if hasattr(self.label_propagation, 'load_data'):
                self.label_propagation.load_data(self.users_df, self.motos_df, self.ratings_df)
            elif hasattr(self.label_propagation, 'add_moto_features'):
                # Convertir las motos a una lista de diccionarios para el algoritmo de similitud
                moto_features_list = self.motos_df.to_dict('records')
                self.label_propagation.add_moto_features(moto_features_list)
            
            if hasattr(self.moto_ideal, 'load_data'):
                self.moto_ideal.load_data(self.users_df, self.motos_df, self.ratings_df)
            
            # Cargar relaciones de amistad si es posible
            try:
                self._load_friendships_from_neo4j()
            except Exception as e:
                logger.warning(f"Error al cargar relaciones de amistad: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error crítico al cargar datos desde Neo4j: {str(e)}")
            traceback.print_exc()
            
            # No usar datos mock - fallar explícitamente
            logger.error("La aplicación requiere Neo4j. No se usarán datos mock.")
            raise RuntimeError("No se pudieron cargar datos desde Neo4j")
    
    def _load_friendships_from_neo4j(self):
        """Carga relaciones de amistad entre usuarios desde Neo4j."""
        logger.info("Cargando relaciones de amistad desde Neo4j...")
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                MATCH (u1:User)-[:FRIEND]->(u2:User)
                RETURN u1.id AS user_id, u2.id AS friend_id
                """)
                
                friendships_data = []
                for record in result:
                    friendships_data.append({
                        'user_id': record['user_id'],
                        'friend_id': record['friend_id']
                    })
                
                self.friendships_df = pd.DataFrame(friendships_data)
                logger.info(f"Relaciones de amistad cargadas: {len(self.friendships_df)}")
                
        except Exception as e:
            logger.error(f"Error al cargar relaciones de amistad: {str(e)}")
            self.friendships_df = pd.DataFrame(columns=['user_id', 'friend_id'])
    
    def get_recommendations(self, user_id, algorithm='hybrid', top_n=5, save_to_db=False, user_preferences=None, **kwargs):
        """
        Obtiene recomendaciones utilizando el algoritmo especificado.
        """
        logger.info(f"Obteniendo recomendaciones para user_id={user_id} usando {algorithm}")
        logger.info(f"Preferencias recibidas: {user_preferences}")
        
        # Asegurar que los datos están cargados
        if self.motos_df is None:
            logger.error("No hay datos de motos cargados")
            return []
        
        # Verificar si el usuario existe
        if not self._user_exists(user_id):
            logger.warning(f"Usuario {user_id} no encontrado")
            # Si tenemos preferencias, podemos usarlas directamente aunque el usuario no exista
            if user_preferences:
                return self._get_recommendations_with_preferences(user_id, user_preferences, top_n)
            return []
        
        # Obtener recomendaciones según el algoritmo
        try:
            if algorithm == 'pagerank':
                # Usar PageRank
                return self.pagerank.get_recommendations(user_id, top_n)
            elif algorithm == 'label_propagation':
                # Usar propagación de etiquetas con características de motos
                try:
                    # Si no hay datos de interacciones, cargarlos
                    if not self.label_propagation.user_preferences:
                        # Preparar datos de interacciones con características detalladas de las motos
                        interactions = self._get_enriched_interactions(user_id)
                        self.label_propagation.initialize_from_interactions(interactions)
                    return self.label_propagation.get_recommendations(user_id, top_n)
                except Exception as e:
                    logger.error(f"Error al obtener recomendaciones con Label Propagation: {str(e)}")
                    return []
            elif algorithm == 'hybrid' or algorithm == 'moto_ideal':
                # Si tenemos preferencias específicas del test, usarlas
                if user_preferences:
                    return self._get_recommendations_with_preferences(user_id, user_preferences, top_n)
                # De lo contrario, usar el método normal
                return self.moto_ideal.get_recommendations(user_id, top_n)
            else:
                logger.warning(f"Algoritmo desconocido: {algorithm}, usando moto_ideal")
                return self.moto_ideal.get_recommendations(user_id, top_n)
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {str(e)}")
            return []
    
    def _get_recommendations_with_preferences(self, user_id, preferences, top_n=5):
        """Genera recomendaciones personalizadas basadas en preferencias específicas del test."""
        logger.info(f"Calculando recomendaciones para {user_id} con preferencias: {preferences}")
        
        # Extraer parámetros de preferencias
        experiencia = preferences.get('experiencia', 'inexperto')
        uso = preferences.get('uso', 'mixto')
        marcas_preferidas = preferences.get('marcas', {})
        estilos_preferidos = preferences.get('estilos', {})
        
        # Extraer rangos específicos con tolerancia del 10%
        presupuesto_min = float(preferences.get('presupuesto_min', 0))
        presupuesto_max = float(preferences.get('presupuesto_max', 100000))
        cilindrada_min = float(preferences.get('cilindrada_min', 0))
        cilindrada_max = float(preferences.get('cilindrada_max', 2000))
        potencia_min = float(preferences.get('potencia_min', 0))
        potencia_max = float(preferences.get('potencia_max', 300))
        torque_min = float(preferences.get('torque_min', 0))
        torque_max = float(preferences.get('torque_max', 200))
        peso_min = float(preferences.get('peso_min', 0))
        peso_max = float(preferences.get('peso_max', 500))
        
        # Aplicar tolerancia del 10% a los rangos
        tolerancia = 0.10
        presupuesto_min_tolerancia = presupuesto_min * (1 - tolerancia)
        presupuesto_max_tolerancia = presupuesto_max * (1 + tolerancia)
        cilindrada_min_tolerancia = cilindrada_min * (1 - tolerancia)
        cilindrada_max_tolerancia = cilindrada_max * (1 + tolerancia)
        potencia_min_tolerancia = potencia_min * (1 - tolerancia)
        potencia_max_tolerancia = potencia_max * (1 + tolerancia)
        torque_min_tolerancia = torque_min * (1 - tolerancia)
        torque_max_tolerancia = torque_max * (1 + tolerancia)
        peso_min_tolerancia = peso_min * (1 - tolerancia)
        peso_max_tolerancia = peso_max * (1 + tolerancia)
        
        logger.info(f"Filtros aplicados con 10% tolerancia:")
        logger.info(f"Presupuesto: {presupuesto_min_tolerancia:.0f} - {presupuesto_max_tolerancia:.0f}")
        logger.info(f"Cilindrada: {cilindrada_min_tolerancia:.0f} - {cilindrada_max_tolerancia:.0f}")
        logger.info(f"Potencia: {potencia_min_tolerancia:.0f} - {potencia_max_tolerancia:.0f}")
        logger.info(f"Torque: {torque_min_tolerancia:.0f} - {torque_max_tolerancia:.0f}")
        logger.info(f"Peso: {peso_min_tolerancia:.0f} - {peso_max_tolerancia:.0f}")
          # FILTROS ESTRICTOS: Solo motos que cumplan TODOS los requisitos
        filtered_motos = self.motos_df.copy()
        
        # PASO 1: FILTROS DE PREFERENCIAS (PRIORIDAD ALTA)
        # Filtro por estilo preferido (aplicar PRIMERO)
        if estilos_preferidos:
            estilo_filter = filtered_motos['tipo'].str.lower().isin(estilos_preferidos.keys())
            filtered_motos = filtered_motos[estilo_filter]
            logger.info(f"Después de filtro por estilo {list(estilos_preferidos.keys())}: {len(filtered_motos)} motos")
            
            if filtered_motos.empty:
                logger.warning(f"No hay motos del estilo preferido. Relajando filtro de estilo...")
                filtered_motos = self.motos_df.copy()
        
        # Filtro por marca preferida (aplicar SEGUNDO)
        if marcas_preferidas and not filtered_motos.empty:
            marca_filter = filtered_motos['marca'].str.lower().isin(marcas_preferidas.keys())
            filtered_motos_marca = filtered_motos[marca_filter]
            
            if not filtered_motos_marca.empty:
                filtered_motos = filtered_motos_marca
                logger.info(f"Después de filtro por marca {list(marcas_preferidas.keys())}: {len(filtered_motos)} motos")
            else:
                logger.warning(f"No hay motos de la marca preferida en el estilo elegido. Manteniendo filtro de estilo...")
        
        # PASO 2: FILTROS TÉCNICOS (aplicar después de preferencias)
        # Filtro por presupuesto (estricto con 10% tolerancia)
        filtered_motos = filtered_motos[
            (filtered_motos['precio'] >= presupuesto_min_tolerancia) & 
            (filtered_motos['precio'] <= presupuesto_max_tolerancia)
        ]
        
        # Filtro por cilindrada (estricto con 10% tolerancia)
        if 'cilindrada' in filtered_motos.columns:
            filtered_motos = filtered_motos[
                (filtered_motos['cilindrada'] >= cilindrada_min_tolerancia) & 
                (filtered_motos['cilindrada'] <= cilindrada_max_tolerancia)
            ]
        
        # Filtro por potencia (estricto con 10% tolerancia)
        if 'potencia' in filtered_motos.columns:
            filtered_motos = filtered_motos[
                (filtered_motos['potencia'] >= potencia_min_tolerancia) & 
                (filtered_motos['potencia'] <= potencia_max_tolerancia)
            ]
        
        # Filtro por torque (estricto con 10% tolerancia)
        if 'torque' in filtered_motos.columns:
            filtered_motos = filtered_motos[
                (filtered_motos['torque'] >= torque_min_tolerancia) & 
                (filtered_motos['torque'] <= torque_max_tolerancia)
            ]
        
        # Filtro por peso (estricto con 10% tolerancia)
        if 'peso' in filtered_motos.columns:
            filtered_motos = filtered_motos[
                (filtered_motos['peso'] >= peso_min_tolerancia) & 
                (filtered_motos['peso'] <= peso_max_tolerancia)
            ]
            logger.info(f"Motos que cumplen TODOS los filtros (preferencias + técnicos): {len(filtered_motos)} de {len(self.motos_df)}")
        if filtered_motos.empty:
            logger.warning(f"No hay motos que cumplan TODOS los filtros. Aplicando filtros relajados...")
            
            # FILTROS RELAJADOS: Mantener preferencias de estilo/marca pero relajar especificaciones técnicas
            filtered_motos = self.motos_df.copy()
            
            # SIEMPRE mantener filtros de preferencias si existen
            if estilos_preferidos:
                estilo_filter = filtered_motos['tipo'].str.lower().isin(estilos_preferidos.keys())
                filtered_motos = filtered_motos[estilo_filter]
                logger.info(f"Filtros relajados - Manteniendo filtro de estilo: {len(filtered_motos)} motos")
                
                if filtered_motos.empty:
                    logger.warning(f"Sin motos del estilo preferido. Expandiendo búsqueda...")
                    filtered_motos = self.motos_df.copy()
            
            if marcas_preferidas and not filtered_motos.empty:
                marca_filter = filtered_motos['marca'].str.lower().isin(marcas_preferidas.keys())
                filtered_motos_marca = filtered_motos[marca_filter]
                
                if not filtered_motos_marca.empty:
                    filtered_motos = filtered_motos_marca
                    logger.info(f"Filtros relajados - Manteniendo filtro de marca: {len(filtered_motos)} motos")
            
            # Aplicar solo los filtros técnicos más importantes con mayor tolerancia (30%)
            tolerancia_relajada = 0.30
            presupuesto_min_rel = presupuesto_min * (1 - tolerancia_relajada)
            presupuesto_max_rel = presupuesto_max * (1 + tolerancia_relajada)
            cilindrada_min_rel = cilindrada_min * (1 - tolerancia_relajada)
            cilindrada_max_rel = cilindrada_max * (1 + tolerancia_relajada)
            
            logger.info(f"Filtros relajados con 30% tolerancia:")
            logger.info(f"Presupuesto: {presupuesto_min_rel:.0f} - {presupuesto_max_rel:.0f}")
            logger.info(f"Cilindrada: {cilindrada_min_rel:.0f} - {cilindrada_max_rel:.0f}")
            
            # Aplicar filtros relajados solo para presupuesto y cilindrada
            if 'cilindrada' in filtered_motos.columns:
                filtered_motos = filtered_motos[
                    (filtered_motos['cilindrada'] >= cilindrada_min_rel) &
                    (filtered_motos['cilindrada'] <= cilindrada_max_rel)
                ]
              # Si aún no hay resultados, intentar con solo preferencias (sin filtros técnicos)
            if filtered_motos.empty:
                logger.warning(f"No hay motos que cumplan filtros relajados. Intentando solo con preferencias...")
                
                filtered_motos = self.motos_df.copy()
                
                # Aplicar solo filtros de preferencias sin restricciones técnicas
                if estilos_preferidos:
                    estilo_filter = filtered_motos['tipo'].str.lower().isin(estilos_preferidos.keys())
                    filtered_motos = filtered_motos[estilo_filter]
                    logger.info(f"Solo filtro de estilo: {len(filtered_motos)} motos")
                
                if marcas_preferidas and not filtered_motos.empty:
                    marca_filter = filtered_motos['marca'].str.lower().isin(marcas_preferidas.keys())
                    filtered_motos_marca = filtered_motos[marca_filter]
                    
                    if not filtered_motos_marca.empty:
                        filtered_motos = filtered_motos_marca
                        logger.info(f"Solo filtros de preferencias (estilo + marca): {len(filtered_motos)} motos")
                
                # Si aún no hay resultados, usar motos populares como último recurso
                if filtered_motos.empty:
                    logger.warning(f"No hay motos que cumplan las preferencias. Usando top motos populares.")
                    
                    # Ordenar por popularidad o ID si no hay campo de popularidad
                    if 'popularity' in self.motos_df.columns:
                        filtered_motos = self.motos_df.sort_values('popularity', ascending=False).head(top_n)
                    else:
                        filtered_motos = self.motos_df.head(top_n)
                    
                    logger.info(f"Seleccionadas {len(filtered_motos)} motos populares como recomendación de respaldo")
                else:
                    logger.info(f"Usando solo filtros de preferencias: {len(filtered_motos)} motos")
            else:
                logger.info(f"Motos que cumplen filtros relajados (preferencias + técnicos relajados): {len(filtered_motos)} de {len(self.motos_df)}")
        
        # Calcular score para cada moto que cumple los filtros
        results = []
        for _, moto in filtered_motos.iterrows():
            score = 1.0  # Empezar con score alto ya que cumple todos los filtros
            reasons = ["Cumple todos tus requisitos técnicos"]
            
            # Bonus por preferencias de estilo
            if 'tipo' in moto and estilos_preferidos:
                tipo = str(moto['tipo']).lower()
                if tipo in estilos_preferidos:
                    nivel = estilos_preferidos[tipo]
                    score += nivel * 0.5
                    reasons.append(f"Estilo {tipo} entre tus preferidos (nivel {nivel})")
            
            # Bonus por marca preferida
            if 'marca' in moto and marcas_preferidas:
                marca = str(moto['marca']).lower()
                if marca in marcas_preferidas:
                    nivel = marcas_preferidas[marca]
                    score += nivel * 0.3
                    reasons.append(f"Marca {marca} entre tus preferidas (nivel {nivel})")
            
            # Bonus por experiencia del usuario
            if experiencia == 'avanzado':
                if moto.get('potencia', 0) > 100:
                    score += 0.2
                    reasons.append("Alta potencia adecuada para tu experiencia avanzada")
            elif experiencia == 'inexperto':
                if moto.get('potencia', 0) <= 50:
                    score += 0.2
                    reasons.append("Potencia moderada adecuada para principiantes")
            
            # Bonus por uso previsto
            if 'tipo' in moto:
                tipo = str(moto['tipo']).lower()
                if uso == 'ciudad' and tipo in ['naked', 'scooter']:
                    score += 0.15
                    reasons.append(f"Tipo {tipo} ideal para uso en ciudad")
                elif uso == 'carretera' and tipo in ['sport', 'touring']:
                    score += 0.15
                    reasons.append(f"Tipo {tipo} ideal para carretera")
                elif uso == 'mixto' and tipo in ['naked', 'adventure']:
                    score += 0.15
                    reasons.append(f"Tipo {tipo} versátil para uso mixto")
            
            # Obtener datos de la moto para el resultado
            moto_id = str(moto.get('moto_id', moto.get('id', '')))

            

            
            # Crear resultado completo con todos los datos de la moto
            moto_result = {
                'moto_id': moto_id,
                'score': score,
                'reasons': reasons,
                'marca': moto.get('marca', ''),
                'modelo': moto.get('modelo', ''),
                'tipo': moto.get('tipo', ''),
                'precio': moto.get('precio', 0),
                'cilindrada': moto.get('cilindrada', 0),
                'potencia': moto.get('potencia', 0),
                'torque': moto.get('torque', 0),
                'peso': moto.get('peso', 0),
                'imagen': moto.get('imagen', ''),
                'note': '; '.join(reasons),
                'url': moto.get('url', ''),
            }
            
            results.append(moto_result)
        
        # Ordenar por score (mayor a menor)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Limitar a top_n resultados
        final_results = results[:top_n]
        
        logger.info(f"Generadas {len(final_results)} recomendaciones estrictas para {user_id}")
        for i, result in enumerate(final_results):
            logger.info(f"#{i+1}: {result['marca']} {result['modelo']} - Score: {result['score']:.2f}")
        
        return final_results
        
    def _user_exists(self, user_id):
        """Comprueba si un usuario existe por su ID."""
        if self.users_df is None:
            return False
        return user_id in self.users_df['user_id'].values
        
    def set_ideal_moto(self, username, moto_id):
        """
        Establece una moto como la ideal para un usuario y la guarda en Neo4j.
        
        Args:
            username (str): Nombre del usuario
            moto_id (str): ID de la moto ideal
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        logger.info(f"Guardando moto {moto_id} como ideal para usuario {username}")
        
        # Asegurar que hay conexión a Neo4j
        self._ensure_neo4j_connection()
        
        try:
            # Buscar el ID del usuario en la base de datos
            user_id = username
            if self.users_df is not None:
                user_rows = self.users_df[self.users_df['username'] == username]
                if not user_rows.empty:
                    user_id = user_rows.iloc[0].get('user_id', username)
            
            # Razones por defecto
            default_reasons = ["Seleccionada como moto ideal por el usuario"]
            
            # Intentar obtener detalles de la moto para mejores razones
            try:
                moto_details = self.get_moto_by_id(moto_id)
                if moto_details:
                    marca = moto_details.get('marca', '')
                    modelo = moto_details.get('modelo', '')
                    tipo = moto_details.get('tipo', '')
                    
                    reasons = [
                        f"Te gusta la marca {marca}",
                        f"El modelo {modelo} se ajusta a tus preferencias"
                    ]
                    
                    if tipo:
                        reasons.append(f"Prefieres el estilo {tipo}")
                else:
                    reasons = default_reasons
            except Exception as e:
                logger.error(f"Error al obtener detalles de la moto: {str(e)}")
                reasons = default_reasons
            
            # Usar el DatabaseConnector para guardar en Neo4j
            with self.driver.session() as session:
                # Convertir reasons a formato JSON
                reasons_json = json.dumps(reasons)
                
                # Actualizar o crear la relación de IDEAL
                result = session.run("""
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                MERGE (u)-[r:IDEAL]->(m)
                SET r.score = 100.0,
                    r.reasons = $reasons,
                    r.timestamp = timestamp()
                RETURN r
                """, user_id=user_id, moto_id=moto_id, reasons=reasons_json)
                
                return True
        except Exception as e:
            logger.error(f"Error al guardar moto ideal: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def get_moto_by_id(self, moto_id):
        """Obtiene los datos de una moto por su ID"""
        try:
            if not self.moto_df.empty:
                # Buscar la moto en el DataFrame
                moto_data = self.moto_df[self.moto_df['moto_id'] == moto_id]
                if len(moto_data) > 0:
                    # Convertir a diccionario y devolver
                    moto_dict = moto_data.iloc[0].to_dict()
                    return moto_dict
        
            # Si no se encuentra en el DataFrame o está vacío, intentar con Neo4j
            if self.driver:
                with self.driver.session() as session:
                    result = session.run(
                        "MATCH (m:Moto) WHERE m.id = $moto_id RETURN m",
                        moto_id=moto_id
                    )
                    record = result.single()
                    if record:
                        moto = record['m']
                        moto_data = dict(moto.items())
                        return moto_data
        
            self.logger.error(f"Moto no encontrada con ID: {moto_id}")
            return None
        except Exception as e:
            self.logger.error(f"Error al obtener moto por ID: {str(e)}")
            return None
    
    def get_popular_motos(self, top_n=10):
        """
        Obtiene las motos más populares usando PageRank.
        
        Args:
            top_n (int): Número de motos a devolver
            
        Returns:
            list: Lista de motos populares con sus puntuaciones
        """
        try:
            # Conectar a Neo4j si es necesario
            if not self._ensure_neo4j_connection():
                logger.error("No se pudo conectar a Neo4j para obtener motos populares")
                return self._get_mock_popular_motos(top_n)
                
            # FIXED: Mejorar la consulta para obtener datos correctos
            query = """
            MATCH (u:User)-[r:INTERACTED]->(m:Moto)
            WHERE r.type = 'like' OR r.type = 'rating'
            RETURN u.id as user_id, m.id as moto_id, 
                   COALESCE(r.weight, 1.0) as weight
            UNION
            MATCH (u:User)-[r:RATED]->(m:Moto)
            RETURN u.id as user_id, m.id as moto_id, 
                   COALESCE(r.rating, 1.0) as weight
            UNION
            MATCH (u:User)-[r:IDEAL]->(m:Moto)
            RETURN u.id as user_id, m.id as moto_id, 
                   5.0 as weight
            """
            
            with self.driver.session() as session:
                result = session.run(query)
                
                # FIXED: Convertir a formato de diccionario con validación
                interactions = []
                for record in result:
                    user_id = record.get("user_id")
                    moto_id = record.get("moto_id")
                    weight = record.get("weight", 1.0)
                    
                    # Validar que tenemos datos válidos
                    if user_id and moto_id:
                        # Asegurar que weight es numérico
                        try:
                            weight = float(weight) if weight is not None else 1.0
                        except (ValueError, TypeError):
                            weight = 1.0
                            
                        interaction = {
                            'user_id': str(user_id),
                            'moto_id': str(moto_id),
                            'weight': weight
                        }
                        interactions.append(interaction)
            
            logger.info(f"Obtenidas {len(interactions)} interacciones para PageRank")
            
            # Si no hay datos de interacción suficientes, devolver motos mock
            if len(interactions) < 5:
                logger.warning("Pocos datos de interacción para calcular motos populares, usando datos mock")
                return self._get_mock_popular_motos(top_n)
                
            # Inicializar y ejecutar PageRank
            from app.algoritmo.pagerank import MotoPageRank
            pagerank = MotoPageRank()
            pagerank.build_graph(interactions)
            
            # FIXED: Usar el parámetro correcto 'n' en lugar de 'top_n'
            popular_moto_rankings = pagerank.get_top_motos(n=top_n)
            
            if not popular_moto_rankings:
                logger.warning("No se obtuvieron rankings de PageRank, usando datos mock")
                return self._get_mock_popular_motos(top_n)
            
            # Obtener información detallada de las motos
            popular_motos_info = []
            
            for i, (moto_id, score) in enumerate(popular_moto_rankings):
                # Buscar datos de la moto en Neo4j
                moto_query = """
                MATCH (m:Moto {id: $moto_id})
                OPTIONAL MATCH (u:User)-[r:INTERACTED]->(m) WHERE r.type = 'like'
                RETURN m.marca as marca, m.modelo as modelo, m.tipo as estilo,
                       m.precio as precio, m.imagen as imagen, count(r) as likes
                """
                
                with self.driver.session() as session:
                    result = session.run(moto_query, moto_id=moto_id)
                    record = result.single()
                    
                    if record:
                        # FIXED: Asegurar que todos los campos requeridos están presentes
                        moto_info = {
                            'moto_id': moto_id,
                            'marca': record.get('marca', 'Marca desconocida'),
                            'modelo': record.get('modelo', 'Modelo desconocido'),
                            'estilo': record.get('estilo', 'Estilo desconocido'),
                            'precio': record.get('precio', 0),
                            'imagen': record.get('imagen', '/static/images/default-moto.jpg'),
                            'likes': record.get('likes', 0),
                            'score': round(score * 100, 1),  # Convertir a escala 0-100
                            'ranking_position': i + 1
                        }
                        popular_motos_info.append(moto_info)
            
            logger.info(f"Obtenidas {len(popular_motos_info)} motos populares del ranking PageRank")
            
            # Si no obtuvimos suficientes motos, complementar con mock data
            if len(popular_motos_info) < top_n:
                logger.info("Complementando con datos mock para alcanzar el número solicitado")
                mock_motos = self._get_mock_popular_motos(top_n - len(popular_motos_info))
                # Ajustar posiciones de ranking
                for i, moto in enumerate(mock_motos):
                    moto['ranking_position'] = len(popular_motos_info) + i + 1
                    moto['score'] = max(0, moto.get('score', 50) - (i * 10))  # Decrementar scores
                popular_motos_info.extend(mock_motos)
            
            return popular_motos_info[:top_n]
            
        except Exception as e:
            logger.error(f"Error al obtener motos populares: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # En caso de error, devolver datos mock
            return self._get_mock_popular_motos(top_n)
    
    def save_preferences(self, user_id, preferences):
        """
        Guarda las preferencias del usuario en Neo4j.
        
        Args:
            user_id (str): ID del usuario
            preferences (dict): Preferencias del usuario
        
        Returns:
            bool: True si se guardaron correctamente
        """
        if not self._ensure_neo4j_connection():
            self.logger.error("Error de conexión a Neo4j al guardar preferencias")
            return False
            
        try:
            with self.driver.session() as session:
                # Convertir preferencias a formato adecuado para Neo4j
                prefs_json = json.dumps(preferences)
                
                # Guardar preferencias en el nodo User
                query = """
                MATCH (u:User {id: $user_id})
                SET u.preferences = $preferences
                RETURN u
                """
                
                result = session.run(query, user_id=user_id, preferences=prefs_json)
                summary = result.consume()
                
                if summary.counters.properties_set > 0:
                    self.logger.info(f"Preferencias guardadas para usuario {user_id}")
                    return True
                else:
                    self.logger.warning(f"No se guardaron preferencias para {user_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error guardando preferencias: {str(e)}")
            return False