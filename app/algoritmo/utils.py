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
    def __init__(self, uri, user, password):
        """
        Inicializa la conexión a Neo4j.
        
        Args:
            uri (str): URI de la base de datos Neo4j
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
            # Validar la conexión
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.is_connected = True
            logger.info("Conexión a Neo4j establecida correctamente")
        except Exception as e:
            logger.warning(f"No se pudo conectar a Neo4j: {str(e)}")
            logger.warning("Funcionando en modo de respaldo (datos simulados)")
        
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.driver:
            self.driver.close()
        
    def get_user_data(self):
        """
        Obtiene datos de usuarios desde Neo4j.
        
        Returns:
            pandas.DataFrame: Datos de usuarios
        """
        if not self.is_connected:
            # Datos simulados si no hay conexión
            return self._get_simulated_user_data()
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User)
                RETURN u.id AS user_id, u.experiencia AS experiencia, 
                       u.uso_previsto AS uso_previsto, u.presupuesto AS presupuesto,
                       u.edad AS edad
            """)
            
            # Convertir a DataFrame
            users = []
            for record in result:
                users.append({
                    'user_id': record['user_id'],
                    'experiencia': record['experiencia'],
                    'uso_previsto': record['uso_previsto'],
                    'presupuesto': record['presupuesto'],
                    'edad': record['edad']
                })
                
            return pd.DataFrame(users)
            
    def get_moto_data(self):
        """
        Obtiene datos de motos desde Neo4j.
        
        Returns:
            pandas.DataFrame: Datos de motos
        """
        if not self.is_connected:
            # Datos simulados si no hay conexión
            return self._get_simulated_moto_data()
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Moto)
                RETURN m.id AS moto_id, m.potencia AS potencia, 
                       m.peso AS peso, m.cilindrada AS cilindrada,
                       m.tipo AS tipo, m.precio AS precio,
                       m.marca AS marca, m.modelo AS modelo
            """)
            
            # Convertir a DataFrame
            motos = []
            for record in result:
                motos.append({
                    'moto_id': record['moto_id'],
                    'potencia': record['potencia'],
                    'peso': record['peso'],
                    'cilindrada': record['cilindrada'],
                    'tipo': record['tipo'],
                    'precio': record['precio'],
                    'marca': record.get('marca', 'Desconocida'),
                    'modelo': record.get('modelo', f"Moto {record['moto_id']}")
                })
                
            return pd.DataFrame(motos)
            
    def get_ratings_data(self):
        """
        Obtiene datos de valoraciones desde Neo4j.
        
        Returns:
            pandas.DataFrame: Datos de valoraciones
        """
        if not self.is_connected:
            # Datos simulados si no hay conexión
            return self._get_simulated_ratings_data()
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User)-[r:RATED]->(m:Moto)
                RETURN u.id AS user_id, m.id AS moto_id, r.rating AS rating
            """)
            
            # Convertir a DataFrame
            ratings = []
            for record in result:
                ratings.append({
                    'user_id': record['user_id'],
                    'moto_id': record['moto_id'],
                    'rating': record['rating']
                })
                
            return pd.DataFrame(ratings)
            
    def get_friendship_data(self):
        """
        Obtiene datos de amistades desde Neo4j.
        
        Returns:
            pandas.DataFrame: Datos de amistades
        """
        if not self.is_connected:
            # Datos simulados si no hay conexión
            return self._get_simulated_friendship_data()
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u1:User)-[f:FRIEND]->(u2:User)
                RETURN u1.id AS user_id, u2.id AS friend_id
            """)
            
            # Convertir a DataFrame
            friendships = []
            for record in result:
                friendships.append({
                    'user_id': record['user_id'],
                    'friend_id': record['friend_id']
                })
                
            return pd.DataFrame(friendships)
            
    def get_interaction_data(self):
        """
        Obtiene datos de interacciones desde Neo4j.
        
        Returns:
            pandas.DataFrame: Datos de interacciones
        """
        if not self.is_connected:
            # Datos simulados si no hay conexión
            return self._get_simulated_interaction_data()
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User)-[i:INTERACTED]->(m:Moto)
                RETURN u.id AS user_id, m.id AS moto_id, 
                       i.type AS interaction_type, i.weight AS weight
            """)
            
            # Convertir a DataFrame
            interactions = []
            for record in result:
                interactions.append({
                    'user_id': record['user_id'],
                    'moto_id': record['moto_id'],
                    'interaction_type': record['interaction_type'],
                    'weight': record['weight']
                })
                
            return pd.DataFrame(interactions)
            
    def store_user_preferences(self, user_id, preferences):
        """
        Almacena las preferencias del usuario en Neo4j.
        
        Args:
            user_id (str): ID del usuario
            preferences (dict): Preferencias del usuario (estilos, marcas, experiencia, etc.)
            
        Returns:
            bool: True si se guardaron correctamente, False en caso contrario
        """
        if not self.is_connected:
            logger.warning("No se pueden guardar preferencias: sin conexión a Neo4j")
            return False
            
        try:
            with self.driver.session() as session:
                # Verificar si el usuario existe
                check_user = session.run(
                    "MATCH (u:User {id: $user_id}) RETURN u",
                    user_id=user_id
                )
                
                if not check_user.single():
                    # Crear el usuario si no existe
                    session.run(
                        """
                        CREATE (u:User {id: $user_id, experiencia: $experiencia})
                        """,
                        user_id=user_id,
                        experiencia=preferences.get('experiencia', 'Intermedio')
                    )
                else:
                    # Actualizar experiencia si existe
                    session.run(
                        """
                        MATCH (u:User {id: $user_id})
                        SET u.experiencia = $experiencia
                        """,
                        user_id=user_id,
                        experiencia=preferences.get('experiencia', 'Intermedio')
                    )
                
                # Almacenar preferencias de estilos
                for estilo, valor in preferences.get('estilos', {}).items():
                    session.run(
                        """
                        MATCH (u:User {id: $user_id})
                        MERGE (e:Estilo {nombre: $estilo})
                        MERGE (u)-[p:PREFIERE]->(e)
                        SET p.valor = $valor
                        """,
                        user_id=user_id,
                        estilo=estilo,
                        valor=float(valor)
                    )
                
                # Almacenar preferencias de marcas
                for marca, valor in preferences.get('marcas', {}).items():
                    session.run(
                        """
                        MATCH (u:User {id: $user_id})
                        MERGE (m:Marca {nombre: $marca})
                        MERGE (u)-[p:PREFIERE]->(m)
                        SET p.valor = $valor
                        """,
                        user_id=user_id,
                        marca=marca,
                        valor=float(valor)
                    )
                
                return True
        except Exception as e:
            logger.error(f"Error al guardar preferencias: {str(e)}")
            return False
            
    def _get_simulated_user_data(self):
        """
        Genera datos simulados de usuarios.
        
        Returns:
            pandas.DataFrame: Datos simulados de usuarios
        """
        users = [
            {'user_id': 'admin', 'experiencia': 'Intermedio', 'uso_previsto': 'Paseo', 'presupuesto': 80000, 'edad': 35},
            {'user_id': 'maria', 'experiencia': 'Principiante', 'uso_previsto': 'Ciudad', 'presupuesto': 50000, 'edad': 28},
            {'user_id': 'pedro', 'experiencia': 'Avanzado', 'uso_previsto': 'Deportivo', 'presupuesto': 120000, 'edad': 42}
        ]
        return pd.DataFrame(users)
        
    def _get_simulated_moto_data(self):
        """
        Genera datos simulados de motos.
        
        Returns:
            pandas.DataFrame: Datos simulados de motos
        """
        motos = [
            {'moto_id': 'moto1', 'potencia': 190, 'peso': 200, 'cilindrada': 1000, 'tipo': 'Deportiva', 'precio': 92000, 
             'marca': 'Kawasaki', 'modelo': 'Ninja ZX-10R'},
            {'moto_id': 'moto2', 'potencia': 120, 'peso': 170, 'cilindrada': 600, 'tipo': 'Deportiva', 'precio': 75000, 
             'marca': 'Honda', 'modelo': 'CBR 600RR'},
            {'moto_id': 'moto3', 'potencia': 43, 'peso': 160, 'cilindrada': 390, 'tipo': 'Naked', 'precio': 46000, 
             'marca': 'KTM', 'modelo': 'Duke 390'},
            {'moto_id': 'moto4', 'potencia': 70, 'peso': 220, 'cilindrada': 650, 'tipo': 'Adventure', 'precio': 68000, 
             'marca': 'Suzuki', 'modelo': 'V-Strom 650'},
            {'moto_id': 'moto5', 'potencia': 110, 'peso': 220, 'cilindrada': 1170, 'tipo': 'Clásica', 'precio': 115000, 
             'marca': 'BMW', 'modelo': 'R nineT'},
            {'moto_id': 'moto6', 'potencia': 42, 'peso': 170, 'cilindrada': 310, 'tipo': 'Deportiva', 'precio': 48000, 
             'marca': 'Yamaha', 'modelo': 'R3'},
            {'moto_id': 'moto7', 'potencia': 111, 'peso': 190, 'cilindrada': 937, 'tipo': 'Naked', 'precio': 89000, 
             'marca': 'Ducati', 'modelo': 'Monster'},
            {'moto_id': 'moto8', 'potencia': 150, 'peso': 190, 'cilindrada': 750, 'tipo': 'Deportiva', 'precio': 80000, 
             'marca': 'Suzuki', 'modelo': 'GSX-R750'}
        ]
        return pd.DataFrame(motos)
        
    def _get_simulated_ratings_data(self):
        """
        Genera datos simulados de valoraciones.
        
        Returns:
            pandas.DataFrame: Datos simulados de valoraciones
        """
        ratings = [
            {'user_id': 'admin', 'moto_id': 'moto8', 'rating': 4.5},
            {'user_id': 'admin', 'moto_id': 'moto1', 'rating': 5.0},
            {'user_id': 'maria', 'moto_id': 'moto6', 'rating': 4.0},
            {'user_id': 'maria', 'moto_id': 'moto3', 'rating': 3.5},
            {'user_id': 'pedro', 'moto_id': 'moto7', 'rating': 4.8},
            {'user_id': 'pedro', 'moto_id': 'moto1', 'rating': 4.2}
        ]
        return pd.DataFrame(ratings)
        
    def _get_simulated_friendship_data(self):
        """
        Genera datos simulados de amistades.
        
        Returns:
            pandas.DataFrame: Datos simulados de amistades
        """
        friendships = [
            {'user_id': 'admin', 'friend_id': 'maria'},
            {'user_id': 'maria', 'friend_id': 'admin'},
            {'user_id': 'pedro', 'friend_id': 'admin'},
            {'user_id': 'admin', 'friend_id': 'pedro'}
        ]
        return pd.DataFrame(friendships)
        
    def _get_simulated_interaction_data(self):
        """
        Genera datos simulados de interacciones.
        
        Returns:
            pandas.DataFrame: Datos simulados de interacciones
        """
        interactions = [
            {'user_id': 'admin', 'moto_id': 'moto1', 'interaction_type': 'view', 'weight': 1.0},
            {'user_id': 'admin', 'moto_id': 'moto8', 'interaction_type': 'like', 'weight': 3.0},
            {'user_id': 'admin', 'moto_id': 'moto5', 'interaction_type': 'view', 'weight': 1.0},
            {'user_id': 'maria', 'moto_id': 'moto6', 'interaction_type': 'like', 'weight': 3.0},
            {'user_id': 'maria', 'moto_id': 'moto3', 'interaction_type': 'view', 'weight': 1.0},
            {'user_id': 'pedro', 'moto_id': 'moto7', 'interaction_type': 'like', 'weight': 3.0},
            {'user_id': 'pedro', 'moto_id': 'moto1', 'interaction_type': 'view', 'weight': 1.0},
            {'user_id': 'pedro', 'moto_id': 'moto4', 'interaction_type': 'view', 'weight': 1.0}
        ]
        return pd.DataFrame(interactions)


class DataPreprocessor:
    @staticmethod
    def normalize_features(df, columns=None):
        """
        Normaliza características numéricas.
        
        Args:
            df (pandas.DataFrame): DataFrame a normalizar
            columns (list): Columnas a normalizar (si es None, normaliza todas las numéricas)
            
        Returns:
            pandas.DataFrame: DataFrame normalizado
        """
        df_norm = df.copy()
        
        if columns is None:
            # Seleccionar columnas numéricas
            columns = df.select_dtypes(include=['int64', 'float64']).columns
            
        for col in columns:
            if col in df.columns:
                min_val = df[col].min()
                max_val = df[col].max()
                
                if max_val > min_val:  # Evitar división por cero
                    df_norm[col] = (df[col] - min_val) / (max_val - min_val)
                    
        return df_norm
    
    @staticmethod
    def encode_categorical(df, columns=None):
        """
        Codifica variables categóricas con one-hot encoding.
        
        Args:
            df (pandas.DataFrame): DataFrame con variables categóricas
            columns (list): Columnas a codificar (si es None, codifica todas las categóricas)
            
        Returns:
            pandas.DataFrame: DataFrame con variables codificadas
        """
        if columns is None:
            # Seleccionar columnas categóricas
            columns = df.select_dtypes(include=['object', 'category']).columns
            
        # Excluir columnas de ID
        columns = [col for col in columns if 'id' not in col.lower()]
            
        # Aplicar one-hot encoding
        df_encoded = pd.get_dummies(df, columns=columns, drop_first=False)
        
        return df_encoded
        
    @staticmethod
    def prepare_interaction_data(df):
        """
        Prepara datos de interacción para el algoritmo PageRank.
        
        Args:
            df (pandas.DataFrame): DataFrame con datos de interacción
            
        Returns:
            list: Lista de tuplas (user_id, moto_id, weight)
        """
        # Asegurarse de que hay una columna de peso
        if 'weight' not in df.columns:
            df['weight'] = 1.0
            
        # Convertir a lista de tuplas
        interaction_tuples = list(df[['user_id', 'moto_id', 'weight']].itertuples(index=False, name=None))
        
        return interaction_tuples
