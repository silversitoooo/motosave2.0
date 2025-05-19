import logging
import pandas as pd
import numpy as np
import os
import time
import traceback
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
    
    def __init__(self, neo4j_config=None, use_mock_data=False):
        """
        Inicializa el adaptador con la configuración proporcionada.
        
        Args:
            neo4j_config (dict): Configuración para la conexión a Neo4j
            use_mock_data (bool): Ignorado - siempre se usa Neo4j
        """
        logger.info("Inicializando MotoRecommenderAdapter para uso exclusivo con Neo4j")
        
        # Forzar uso exclusivo de Neo4j
        self.use_mock_data = False
        
        # Configuración Neo4j
        if neo4j_config:
            self.neo4j_uri = neo4j_config.get('uri', "bolt://localhost:7687")
            self.neo4j_user = neo4j_config.get('user', "neo4j")
            self.neo4j_password = neo4j_config.get('password', "22446688")
        else:
            self.neo4j_uri = "bolt://localhost:7687"
            self.neo4j_user = "neo4j"
            self.neo4j_password = "22446688"
            
        self.driver = None
        
        # Datos
        self.users_df = None
        self.motos_df = None
        self.ratings_df = None
        self.friendships_df = None
        
        # Inicializar algoritmos de recomendación correctamente
        self.pagerank = MotoPageRank()
        self.label_propagation = MotoLabelPropagation() 
        self.moto_ideal = MotoIdealRecommender()
        
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
                # Usar propagación de etiquetas
                return self.label_propagation.get_recommendations(user_id, top_n)
            elif algorithm == 'hybrid' or algorithm == 'moto_ideal':
                # Si tenemos preferencias específicas del test, usarlas
                if user_preferences:
                    return self._get_recommendations_with_preferences(user_id, user_preferences, top_n)
                # De lo contrario, usar el método normal
                return self.moto_ideal.get_moto_ideal(user_id, top_n)
            else:
                logger.warning(f"Algoritmo desconocido: {algorithm}, usando moto_ideal")
                return self.moto_ideal.get_moto_ideal(user_id, top_n)
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {str(e)}")
            return []
    
    def _get_recommendations_with_preferences(self, user_id, preferences, top_n=5):
        """Genera recomendaciones personalizadas basadas en preferencias específicas del test."""
        logger.info(f"Calculando recomendaciones para {user_id} con preferencias: {preferences}")
        
        # Extraer parámetros de preferencias
        experiencia = preferences.get('experiencia', 'inexperto')
        presupuesto = float(preferences.get('presupuesto', 8000))
        uso = preferences.get('uso', 'mixto')
        marcas_preferidas = preferences.get('marcas', {})
        estilos_preferidos = preferences.get('estilos', {})
        
        # MODIFICAR: Filtrar motos según presupuesto con mayor margen (30% en lugar de 20%)
        presupuesto_max = presupuesto * 1.3
        filtered_motos = self.motos_df[self.motos_df['precio'] <= presupuesto_max].copy()
        
        if filtered_motos.empty:
            logger.warning(f"No hay motos dentro del presupuesto {presupuesto}. Usando todas las motos.")
            filtered_motos = self.motos_df.copy()
        
        # Calcular score para cada moto
        results = []
        for _, moto in filtered_motos.iterrows():
            score = 0.5  # CAMBIO: Empezar con score base positivo
            reasons = []
            
            # SIMPLIFICAR evaluación por tipo/estilo
            if 'tipo' in moto:
                tipo = str(moto['tipo']).lower()
                if estilos_preferidos and tipo in estilos_preferidos:
                    nivel = estilos_preferidos[tipo]
                    score += nivel * 0.25
                    reasons.append(f"Estilo {tipo} entre tus preferidos")
                elif uso == 'paseo' and tipo in ['naked', 'touring', 'sport']:
                    score += 0.25
                    reasons.append(f"Estilo {tipo} adecuado para paseo")
                elif uso == 'ciudad' and tipo in ['naked', 'scooter']:
                    score += 0.25
                    reasons.append(f"Estilo {tipo} adecuado para ciudad")
            
            # SIMPLIFICAR evaluación por marca
            if 'marca' in moto:
                marca = str(moto['marca']).lower()
                if marcas_preferidas and marca in marcas_preferidas:
                    nivel = marcas_preferidas[marca]
                    score += nivel * 0.25
                    reasons.append(f"Marca {marca} entre tus preferidas")
            
            # Evaluar presupuesto
            precio = moto.get('precio', 0)
            if precio <= presupuesto:
                score += 0.5
                reasons.append(f"Precio ({precio}€) dentro de tu presupuesto ({presupuesto}€)")
            
            # Si no hay razones, agregar razón genérica
            if not reasons:
                reasons.append("Recomendación basada en tus criterios generales")
            
            # Obtener ID de la moto
            moto_id = str(moto.get('moto_id', moto.get('id', '')))
            results.append((moto_id, score, reasons))
        
        # Ordenar por score y obtener top_n
        results.sort(key=lambda x: x[1], reverse=True)
        
        # AÑADIR log para confirmar resultados
        logger.info(f"Generadas {len(results[:top_n])} recomendaciones para {user_id}")
        return results[:top_n]
        
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
                # Actualizar o crear la relación de IDEAL
                result = session.run("""
                MATCH (u:User {id: $user_id})
                MATCH (m:Moto {id: $moto_id})
                MERGE (u)-[r:IDEAL]->(m)
                SET r.score = 100.0,
                    r.reasons = $reasons,
                    r.timestamp = timestamp()
                RETURN r
                """, user_id=user_id, moto_id=moto_id, reasons=reasons)
                
                return True
        except Exception as e:
            logger.error(f"Error al guardar moto ideal: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def get_moto_by_id(self, moto_id):
        """
        Obtiene los detalles de una moto por su ID.
        
        Args:
            moto_id (str): ID de la moto a buscar
            
        Returns:
            dict: Diccionario con los detalles de la moto, o None si no se encuentra
        """
        logger.info(f"Buscando detalles de la moto con ID: {moto_id}")
        
        # Verificar que los datos estén cargados
        if self.motos_df is None:
            logger.warning("No hay datos de motos cargados")
            return None
            
        try:
            # Primero buscar en el dataframe local por eficiencia
            moto_rows = self.motos_df[self.motos_df['moto_id'] == moto_id]
            
            if not moto_rows.empty:
                # Convertir la fila a diccionario
                return moto_rows.iloc[0].to_dict()
            
            # Si no se encuentra en el dataframe, intentar buscar en Neo4j directamente
            if self._ensure_neo4j_connection():
                with self.driver.session() as session:
                    result = session.run("""
                    MATCH (m:Moto {id: $moto_id})
                    RETURN m
                    """, moto_id=moto_id)
                    
                    record = result.single()
                    if record:
                        # Extraer propiedades del nodo
                        moto_data = dict(record['m'])
                        # Asegurar consistencia con el nombre del campo ID
                        if 'id' in moto_data and 'moto_id' not in moto_data:
                            moto_data['moto_id'] = moto_data['id']
                        return moto_data
            
            logger.warning(f"No se encontró la moto con ID: {moto_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error al buscar la moto {moto_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return None