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
            # Para PageRank que no tiene método load_data
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
            else:
                logger.warning("PageRank no tiene método build_graph, no se inicializará correctamente")
                
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
    
    def _user_exists(self, user_id):
        """Comprueba si un usuario existe por su ID."""
        if self.users_df is None:
            return False
        return user_id in self.users_df['user_id'].values
