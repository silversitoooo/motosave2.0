import logging
import pandas as pd
import numpy as np
import os
import time
import traceback
import json
from neo4j import GraphDatabase
from app.algoritmo.pagerank import MotoPageRank
from app.algoritmo.label_propagation import MotoLabelPropagation
from app.algoritmo.moto_ideal import MotoIdealRecommender
from app.algoritmo.utils import DatabaseConnector, DataPreprocessor

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
        
        # Inicializar atributos
        self.driver = None
        self.data_loaded = False
        self.user_data = None
        self.moto_data = None
        self.ratings_data = None
        self.friendships_df = None
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
    
    def load_data(self, users_df=None, motos_df=None, ratings_df=None):
        """
        Carga los datos exclusivamente desde Neo4j.
        """
        logger.info("Cargando datos desde Neo4j (modo exclusivo)")
        
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
            logger.info(f"Motos que cumplen filtros estrictos: {len(filtered_motos)} de {len(self.motos_df)}")
        
        if filtered_motos.empty:
            logger.warning(f"No hay motos que cumplan los filtros estrictos. Usando filtros relajados.")
            
            # FILTROS RELAJADOS: Motos que cumplan al menos algunos requisitos importantes
            filtered_motos = self.motos_df.copy()
            
            # Aplicar solo los filtros más importantes con mayor tolerancia (30%)
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
            
            # Si aún no hay resultados, obtener las top N motos más populares
            if filtered_motos.empty:
                logger.warning(f"No hay motos que cumplan los filtros relajados. Usando top motos populares.")
                
                # Ordenar por popularidad o ID si no hay campo de popularidad
                if 'popularity' in self.motos_df.columns:
                    filtered_motos = self.motos_df.sort_values('popularity', ascending=False).head(top_n)
                else:
                    filtered_motos = self.motos_df.head(top_n)
                
                logger.info(f"Seleccionadas {len(filtered_motos)} motos populares como recomendación de respaldo")
            else:
                logger.info(f"Motos que cumplen filtros relajados: {len(filtered_motos)} de {len(self.motos_df)}")
        
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
                'note': '; '.join(reasons)
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
                return []
                
            # Obtener datos de interacción
            query = """
            MATCH (u:User)-[r:INTERACTED]->(m:Moto)
            WHERE r.type = 'like' OR r.type = 'rating'
            RETURN u.id as user_id, m.id as moto_id, r.weight as weight
            """
            
            with self.driver.session() as session:
                result = session.run(query)
                interactions = [(record["user_id"], record["moto_id"], 
                               record.get("weight", 1.0)) for record in result]
            
            # Si no hay datos de interacción, devolver lista vacía
            if not interactions:
                logger.warning("No hay datos de interacción para calcular motos populares")
                return []
                
            # Inicializar y ejecutar PageRank
            from app.algoritmo.pagerank import MotoPageRank
            pagerank = MotoPageRank()
            pagerank.build_graph(interactions)
            pagerank.run()
            
            # Obtener las motos más populares
            popular_moto_ids = pagerank.get_popular_motos(top_n=top_n)
            
            # Obtener información detallada de las motos
            popular_motos_info = []
            
            if not self.motos_df is None and not self.motos_df.empty:
                # Usar DataFrame en memoria si está disponible
                for moto_id, score in popular_moto_ids:
                    # Buscar la moto en el DataFrame
                    moto_info = self.motos_df[self.motos_df['moto_id'] == moto_id]
                    if not moto_info.empty:
                        # Convertir la primera fila a diccionario
                        moto_dict = moto_info.iloc[0].to_dict()
                        # Agregar puntuación
                        moto_dict['score'] = score
                        popular_motos_info.append(moto_dict)
            else:
                # Buscar datos en Neo4j
                moto_ids = [moto_id for moto_id, _ in popular_moto_ids]
                moto_query = """
                MATCH (m:Moto)
                WHERE m.id IN $moto_ids
                RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                       m.tipo as tipo, m.precio as precio, m.imagen as imagen
                """
                
                with self.driver.session() as session:
                    result = session.run(moto_query, moto_ids=moto_ids)
                    
                    for record in result:
                        # Buscar la puntuación
                        score = 0.0
                        for moto_id, s in popular_moto_ids:
                            if moto_id == record["id"]:
                                score = s
                                break
                                
                        popular_motos_info.append({
                            "id": record["id"],
                            "marca": record["marca"],
                            "modelo": record["modelo"],
                            "tipo": record["tipo"],
                            "precio": record["precio"],
                            "imagen": record["imagen"],
                            "score": score
                        })
            
            return popular_motos_info
            
        except Exception as e:
            logger.error(f"Error al obtener motos populares: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _get_popular_motos(self, top_n=10):
        """
        Método de compatibilidad para código antiguo que llama a _get_popular_motos.
        
        Args:
            top_n (int): Número de motos a devolver
            
        Returns:
            list: Lista de motos populares con sus puntuaciones
        """
        return self.get_popular_motos(top_n)
    
    def _get_enriched_interactions(self, user_id):
        """
        Obtiene interacciones enriquecidas con detalles de motos para el algoritmo de Label Propagation.
        
        Args:
            user_id (str): ID del usuario
            
        Returns:
            list: Lista de interacciones enriquecidas
        """
        try:
            # Verificar conexión a Neo4j
            if not self._ensure_neo4j_connection():
                logger.warning("No hay conexión a Neo4j para obtener interacciones")
                return []
                
            with self.driver.session() as session:
                # Obtener interacciones del usuario y sus amigos
                result = session.run("""
                MATCH (u:User)-[:FRIEND_OF|FRIEND]-(f:User)
                MATCH (u_or_f:User)-[r:INTERACTED|IDEAL|RATED]->(m:Moto)
                WHERE u.id = $user_id AND (u_or_f.id = u.id OR u_or_f.id = f.id)
                RETURN 
                    u_or_f.id as user_id,
                    m.id as moto_id,
                    m.marca as marca,
                    m.modelo as modelo,
                    m.tipo as tipo,
                    m.cilindrada as cilindrada,
                    m.potencia as potencia,
                    m.precio as precio,
                    CASE type(r)
                        WHEN 'INTERACTED' THEN r.weight
                        WHEN 'IDEAL' THEN 1.0
                        WHEN 'RATED' THEN r.rating / 5.0
                        ELSE 0.5
                    END as weight
                """, user_id=user_id)
                
                interactions = [dict(record) for record in result]
                
                # Si no tenemos suficientes interacciones, obtener las motos más populares
                if len(interactions) < 10:
                    popular_result = session.run("""
                    MATCH (u:User)-[r:INTERACTED|IDEAL|RATED]->(m:Moto)
                    WITH m, count(r) as popularity
                    ORDER BY popularity DESC
                    LIMIT 20
                    RETURN 
                        'synthetic_user' as user_id,
                        m.id as moto_id,
                        m.marca as marca,
                        m.modelo as modelo,
                        m.tipo as tipo,
                        m.cilindrada as cilindrada,
                        m.potencia as potencia,
                        m.precio as precio,
                        0.5 as weight
                    """)
                    
                    popular_interactions = [dict(record) for record in popular_result]
                    interactions.extend(popular_interactions)
                
                return interactions
                
        except Exception as e:
            logger.error(f"Error al obtener interacciones enriquecidas: {str(e)}")
            return []
    
    def save_preferences(self, user_id, preferences):
        """
        Guarda las preferencias de usuario en Neo4j.
        
        Args:
            user_id: ID del usuario
            preferences: Diccionario con preferencias
            
        Returns:
            bool: True si se guardaron correctamente, False en caso contrario
        """
        try:
            self._ensure_neo4j_connection()
            if not self.driver:
                self.logger.error("No hay conexión a Neo4j para guardar preferencias")
                return False
                
            with self.driver.session() as session:
                # Verificar si existe el usuario
                result = session.run("MATCH (u:User {id: $user_id}) RETURN count(u) as count", user_id=user_id)
                user_exists = result.single()["count"] > 0
                
                if not user_exists:
                    # Crear el usuario si no existe
                    username = preferences.get('username', f"user_{user_id[-3:]}")
                    session.run("""
                        CREATE (u:User {id: $user_id, username: $username, created_at: timestamp()})
                    """, user_id=user_id, username=username)
                    self.logger.info(f"Usuario creado: {user_id}")
                    
                # MEJORADO: Manejar valores cuantitativos correctamente
                quantitative_props = {}
                for key, value in preferences.items():
                    # Procesar solo valores numéricos
                    if key in ['presupuesto', 'presupuesto_min', 'presupuesto_max', 
                               'cilindrada', 'cilindrada_min', 'cilindrada_max',
                               'potencia', 'potencia_min', 'potencia_max']:
                        try:
                            # Asegurar que son números
                            quantitative_props[key] = int(value)
                        except (ValueError, TypeError):
                            self.logger.warning(f"Valor no numérico para {key}: {value}")
                
                # Guardar propiedades cuantitativas directamente en el nodo
                if quantitative_props:
                    query_parts = []
                    for key in quantitative_props:
                        query_parts.append(f"u.{key} = ${key}")
                    
                    query = f"""
                        MATCH (u:User {{id: $user_id}})
                        SET {', '.join(query_parts)}
                    """
                    session.run(query, user_id=user_id, **quantitative_props)
                    self.logger.info(f"Propiedades cuantitativas guardadas: {list(quantitative_props.keys())}")
                    
                # Guardar preferencias de estilo
                if 'estilos' in preferences and isinstance(preferences['estilos'], dict):
                    # Eliminar relaciones anteriores
                    session.run("""
                        MATCH (u:User {id: $user_id})-[r:PREFERS_STYLE]->()
                        DELETE r
                    """, user_id=user_id)
                    
                    # Crear nuevas relaciones
                    for estilo, peso in preferences['estilos'].items():
                        session.run("""
                            MATCH (u:User {id: $user_id})
                            MERGE (s:Style {name: $estilo})
                            MERGE (u)-[r:PREFERS_STYLE]->(s)
                            SET r.weight = $peso
                        """, user_id=user_id, estilo=estilo, peso=float(peso))
                    
                    self.logger.info(f"Preferencias de estilo guardadas: {list(preferences['estilos'].keys())}")
                    
                # Guardar preferencias de marca
                if 'marcas' in preferences and isinstance(preferences['marcas'], dict):
                    # Eliminar relaciones anteriores
                    session.run("""
                        MATCH (u:User {id: $user_id})-[r:PREFERS_BRAND]->()
                        DELETE r
                    """, user_id=user_id)
                    
                    # Crear nuevas relaciones
                    for marca, peso in preferences['marcas'].items():
                        session.run("""
                            MATCH (u:User {id: $user_id})
                            MERGE (b:Brand {name: $marca})
                            MERGE (u)-[r:PREFERS_BRAND]->(b)
                            SET r.weight = $peso
                        """, user_id=user_id, marca=marca, peso=float(peso))
                    
                    self.logger.info(f"Preferencias de marca guardadas: {list(preferences['marcas'].keys())}")
                    
                # Guardar otras preferencias como nodo PreferenceSet
                other_prefs = {k: v for k, v in preferences.items() if k not in ['estilos', 'marcas'] 
                              and not k.startswith('presupuesto') and not k.startswith('cilindrada')
                              and not k.startswith('potencia')}
                
                if other_prefs:
                    # Convertir a formato JSON para guardar
                    prefs_json = json.dumps(other_prefs)
                    
                    # Guardar en nodo de preferencias
                    session.run("""
                        MATCH (u:User {id: $user_id})
                        MERGE (p:PreferenceSet {user_id: $user_id})
                        SET p.preferences = $prefs,
                            p.updated_at = timestamp()
                        MERGE (u)-[:HAS_PREFERENCES]->(p)
                    """, user_id=user_id, prefs=prefs_json)
                    
                    self.logger.info(f"Otras preferencias guardadas como JSON")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error al guardar preferencias: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False