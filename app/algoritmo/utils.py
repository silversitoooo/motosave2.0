"""
Utilidades para los algoritmos de recomendación de motos.
Incluye funciones para conectar con la base de datos y preprocesar datos.
"""
import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConnector:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="22446688"):
        """
        Inicializa el conector a Neo4j.
        
        Args:
            uri (str): URI de Neo4j
            user (str): Nombre de usuario
            password (str): Contraseña
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.is_connected = False
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Probar la conexión
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.is_connected = True
            logger.info("Conexión a Neo4j establecida correctamente")
        except Exception as e:
            logger.error(f"No se pudo conectar a Neo4j: {str(e)}")
    
    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta en Neo4j.
        
        Args:
            query (str): Consulta Cypher a ejecutar
            params (dict, optional): Parámetros para la consulta
            
        Returns:
            list: Resultados de la consulta
        """
        if not self.is_connected:
            logger.error("No hay conexión a Neo4j")
            return None
            
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error al ejecutar consulta: {str(e)}")
            return None
    
    def get_user_data(self):
        """
        Obtiene datos de usuarios.
        
        Returns:
            pandas.DataFrame: DataFrame con datos de usuarios
        """
        if not self.is_connected:
            return pd.DataFrame()
            
        try:
            query = """
            MATCH (u:User)
            RETURN u.user_id as user_id, 
                   u.experiencia as experiencia,
                   u.uso_previsto as uso_previsto,
                   u.presupuesto as presupuesto,
                   u.nombre as nombre
            """
            with self.driver.session() as session:
                result = session.run(query)
                data = [record.data() for record in result]
                return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error al obtener datos de usuarios: {str(e)}")
            return pd.DataFrame()
    
    def get_moto_data(self):
        """
        Obtiene datos de motos.
        
        Returns:
            pandas.DataFrame: DataFrame con datos de motos
        """
        if not self.is_connected:
            return pd.DataFrame()
            
        try:
            query = """
            MATCH (m:Moto)
            RETURN m.moto_id as moto_id,
                   m.modelo as modelo,
                   m.marca as marca,
                   m.tipo as tipo,
                   m.potencia as potencia,
                   m.cilindrada as cilindrada,
                   m.peso as peso,
                   m.precio as precio,
                   m.imagen as imagen
            """
            with self.driver.session() as session:
                result = session.run(query)
                data = [record.data() for record in result]
                return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error al obtener datos de motos: {str(e)}")
            return pd.DataFrame()
    
    def get_ratings_data(self):
        """
        Obtiene datos de valoraciones.
        
        Returns:
            pandas.DataFrame: DataFrame con valoraciones
        """
        if not self.is_connected:
            return pd.DataFrame()
            
        try:
            query = """
            MATCH (u:User)-[r:RATED]->(m:Moto)
            RETURN u.user_id as user_id,
                   m.moto_id as moto_id,
                   r.rating as rating
            """
            with self.driver.session() as session:
                result = session.run(query)
                data = [record.data() for record in result]
                return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error al obtener valoraciones: {str(e)}")
            return pd.DataFrame()
    
    def store_user_preferences(self, user_id, test_data):
        """
        Almacena preferencias del usuario en Neo4j.
        
        Args:
            user_id (str): ID del usuario
            test_data (dict): Datos del test
            
        Returns:
            bool: True si fue exitoso
        """
        if not self.is_connected:
            logger.error("No hay conexión a Neo4j para almacenar preferencias")
            return False
            
        try:
            # Verificar si el usuario existe
            query_check = """
            MATCH (u:User {user_id: $user_id})
            RETURN count(u) as count
            """
            result = self.execute_query(query_check, {'user_id': user_id})
            user_exists = result[0]['count'] > 0 if result else False
            
            if user_exists:
                # Actualizar usuario existente
                query = """
                MATCH (u:User {user_id: $user_id})
                SET u.experiencia = $experiencia,
                    u.uso_previsto = $uso_previsto,
                    u.presupuesto = $presupuesto
                RETURN u
                """
            else:
                # Crear nuevo usuario
                query = """
                CREATE (u:User {
                    user_id: $user_id,
                    experiencia: $experiencia,
                    uso_previsto: $uso_previsto,
                    presupuesto: $presupuesto
                })
                RETURN u
                """
                
            # Ejecutar query con parámetros
            params = {
                'user_id': user_id,
                'experiencia': test_data.get('experiencia', 'principiante'),
                'uso_previsto': test_data.get('uso', 'urbano'),
                'presupuesto': float(test_data.get('presupuesto', 8000))
            }
            
            result = self.execute_query(query, params)
            logger.info(f"Preferencias de {user_id} actualizadas en Neo4j: {params}")
            return True
        except Exception as e:
            logger.error(f"Error al almacenar preferencias de usuario: {str(e)}")
            return False
    
    def close(self):
        """Cierra la conexión a Neo4j."""
        if self.driver:
            self.driver.close()
            self.is_connected = False

class DataPreprocessor:
    """Utilidades para preprocesar datos antes de usarlos con algoritmos de ML."""
    
    @staticmethod
    def encode_categorical(df):
        """
        Codifica variables categóricas usando one-hot encoding.
        
        Args:
            df (pandas.DataFrame): DataFrame con columnas categóricas
            
        Returns:
            pandas.DataFrame: DataFrame con columnas codificadas
        """
        if df is None or df.empty:
            return df
            
        result = df.copy()
        
        # Identificar columnas categóricas (excluyendo user_id y moto_id)
        categorical_cols = [col for col in result.columns 
                          if col not in ['user_id', 'moto_id'] 
                          and result[col].dtype == 'object']
        
        # Aplicar one-hot encoding
        for col in categorical_cols:
            # Crear columnas binarias para cada valor único
            for value in result[col].unique():
                if pd.notna(value):  # Ignorar valores NaN
                    col_name = f"{col}_{value}".lower()
                    result[col_name] = (result[col] == value).astype(int)
            
            # Eliminar columna original
            result = result.drop(col, axis=1)
            
        return result
    
    @staticmethod
    def normalize_features(df, columns=None):
        """
        Normaliza características numéricas a escala 0-1.
        
        Args:
            df (pandas.DataFrame): DataFrame con columnas numéricas
            columns (list, optional): Lista de columnas a normalizar
            
        Returns:
            pandas.DataFrame: DataFrame con columnas normalizadas
        """
        if df is None or df.empty:
            return df
            
        result = df.copy()
        
        # Si no se especifican columnas, detectar automáticamente
        if columns is None:
            columns = [col for col in result.columns 
                     if col not in ['user_id', 'moto_id'] 
                     and pd.api.types.is_numeric_dtype(result[col])]
        
        # Normalizar cada columna
        for col in columns:
            if col in result.columns:
                min_val = result[col].min()
                max_val = result[col].max()
                
                if max_val > min_val:  # Evitar división por cero
                    result[col] = (result[col] - min_val) / (max_val - min_val)
                    
        return result
