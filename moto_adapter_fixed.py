"""
Adaptador para el sistema de recomendación de motos.
Conecta los algoritmos de recomendación y proporciona una interfaz unificada.
"""
import pandas as pd
import numpy as np
import logging
from app.algoritmo.pagerank import MotoPageRank
from app.algoritmo.label_propagation import MotoLabelPropagation
from app.algoritmo.moto_ideal import MotoIdealRecommender
from app.algoritmo.utils import DatabaseConnector, DataPreprocessor

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MotoRecommenderIntegration')

class MotoRecommenderAdapter:
    """Adaptador que integra diferentes algoritmos de recomendación para motos."""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", use_mock_data=False):
        """
        Inicializa el adaptador con conexión a Neo4j o datos simulados.
        
        Args:
            uri: URI de Neo4j
            user: Usuario de Neo4j
            password: Contraseña de Neo4j
            use_mock_data: Si es True, usa datos simulados
        """
        self.db_connected = False
        self.data_loaded = False
        
        if not use_mock_data:
            try:
                self.connector = DatabaseConnector(uri, user, password)
                self.db_connected = self.connector.is_connected
                logger.info(f"Conexión establecida con Neo4j en {uri}")
            except Exception as e:
                logger.error(f"Error al conectar con Neo4j: {str(e)}")
                logger.info("Cambiando a modo de datos simulados")
                self.connector = None
        else:
            logger.info("Usando datos simulados")
            self.connector = None
        
        # Inicialización de atributos
        self.users = None
        self.motos = None
        self.ratings = None
        self.friendships = None
        self.interactions = None
        
        # Inicialización de recomendadores
        self.pagerank = MotoPageRank()
        self.label_propagation = MotoLabelPropagation()
        self.moto_ideal = MotoIdealRecommender()
    
    def load_data(self, users_df=None, motos_df=None, ratings_df=None):
        """
        Carga datos desde Neo4j o desde DataFrames proporcionados.
        """
        # Si se proporcionan DataFrames, usarlos directamente
        if users_df is not None and motos_df is not None:
            logger.info("Cargando datos desde DataFrames proporcionados")
            self.users = users_df
            self.motos = motos_df
            self.ratings = ratings_df if ratings_df is not None else pd.DataFrame()
            
            # Generar datos simulados si no hay conexión a Neo4j
            if not self.db_connected:
                # Crear amistades simuladas
                if self.users is not None and len(self.users) > 1:
                    friendships = []
                    user_ids = self.users['user_id'].tolist()
                    for i in range(len(user_ids)):
                        for j in range(i+1, min(i+3, len(user_ids))):
                            friendships.append({'user_id': user_ids[i], 'friend_id': user_ids[j]})
                            friendships.append({'friend_id': user_ids[i], 'user_id': user_ids[j]})
                    self.friendships = pd.DataFrame(friendships)
                else:
                    self.friendships = pd.DataFrame()
                
                # Crear interacciones simuladas
                if self.ratings is not None and not self.ratings.empty:
                    interactions = []
                    for _, row in self.ratings.iterrows():
                        interactions.append({
                            'user_id': row['user_id'],
                            'moto_id': row['moto_id'],
                            'interaction_type': 'rating',
                            'weight': row['rating']
                        })
                    self.interactions = pd.DataFrame(interactions)
                else:
                    self.interactions = pd.DataFrame()
            
            self.data_loaded = True
            return True
        
        # Si no hay DataFrames, intentar cargar desde Neo4j
        if self.db_connected:
            try:
                self.users = self.connector.get_user_data()
                self.motos = self.connector.get_moto_data()
                self.ratings = self.connector.get_ratings_data()
                self.friendships = self.connector.get_friendship_data()
                self.interactions = self.connector.get_interaction_data()
                self.data_loaded = True
                return True
            except Exception as e:
                logger.error(f"Error al cargar datos desde Neo4j: {str(e)}")
                logger.info("Cambiando a datos simulados")
                self._load_mock_data()
                return self.data_loaded
        else:
            logger.info("Usando datos simulados predeterminados")
            self._load_mock_data()
            return self.data_loaded
    
    def _load_mock_data(self):
        """Carga datos simulados predeterminados."""
        try:
            # Datos simulados de usuarios
            users = [
                {'user_id': 'admin', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000},
                {'user_id': 'test_user', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
                {'user_id': 'maria', 'experiencia': 'experto', 'uso_previsto': 'offroad', 'presupuesto': 15000},
                {'user_id': 'ariel1234', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 8000}
            ]
            
            self.users = pd.DataFrame(users)
            
            # Datos de motos más descriptivos y con imágenes reales
            motos = [
                {'moto_id': 'moto1', 'modelo': 'CB125R', 'marca': 'Honda', 'tipo': 'naked', 
                 'potencia': 15, 'cilindrada': 125, 'peso': 130, 'precio': 4500,
                 'imagen': 'https://www.motofichas.com/images/phocagallery/Honda/cb125r-2021/01-honda-cb125r-2021-estudio-negro.jpg'},
                {'moto_id': 'moto2', 'modelo': 'Z900', 'marca': 'Kawasaki', 'tipo': 'naked', 
                 'potencia': 125, 'cilindrada': 900, 'peso': 210, 'precio': 9500,
                 'imagen': 'https://www.motofichas.com/images/phocagallery/Kawasaki/z900-2023/01-kawasaki-z900-2023-estudio-verde.jpg'},
                {'moto_id': 'moto3', 'modelo': 'R1250GS', 'marca': 'BMW', 'tipo': 'adventure', 
                 'potencia': 136, 'cilindrada': 1250, 'peso': 249, 'precio': 18000,
                 'imagen': 'https://www.motofichas.com/images/phocagallery/BMW_Motorrad/r-1250-gs-2021/01-bmw-r-1250-gs-2021-estudio-amarillo.jpg'},
                {'moto_id': 'moto4', 'modelo': 'MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 
                 'potencia': 75, 'cilindrada': 700, 'peso': 184, 'precio': 7500,
                 'imagen': 'https://www.motofichas.com/images/phocagallery/Yamaha/mt-07-2021/01-yamaha-mt-07-2021-estudio-gris.jpg'},
                {'moto_id': 'moto5', 'modelo': 'Duke 390', 'marca': 'KTM', 'tipo': 'naked', 
                 'potencia': 43, 'cilindrada': 390, 'peso': 149, 'precio': 5800,
                 'imagen': 'https://www.motofichas.com/images/phocagallery/KTM/390-duke-2022/01-ktm-390-duke-2022-estudio-naranja.jpg'},
                {'moto_id': 'moto6', 'modelo': 'Panigale V4', 'marca': 'Ducati', 'tipo': 'sport', 
                 'potencia': 214, 'cilindrada': 1103, 'peso': 175, 'precio': 24000,
                 'imagen': 'https://www.motofichas.com/images/phocagallery/Ducati/panigale-v4-2022/01-ducati-panigale-v4-2022-estudio-rojo.jpg'},
                {'moto_id': 'moto7', 'modelo': 'PCX 125', 'marca': 'Honda', 'tipo': 'scooter', 
                 'potencia': 12, 'cilindrada': 125, 'peso': 130, 'precio': 3500,
                 'imagen': 'https://www.motofichas.com/images/phocagallery/Honda/pcx-125-2021/01-honda-pcx-125-2021-estudio-azul.jpg'}
            ]
            
            self.motos = pd.DataFrame(motos)
            
            # Datos simulados de valoraciones
            ratings = [
                {'user_id': 'admin', 'moto_id': 'moto2', 'rating': 4.5},
                {'user_id': 'admin', 'moto_id': 'moto4', 'rating': 4.0},
                {'user_id': 'test_user', 'moto_id': 'moto1', 'rating': 5.0},
                {'user_id': 'test_user', 'moto_id': 'moto7', 'rating': 4.5},
                {'user_id': 'maria', 'moto_id': 'moto3', 'rating': 4.0},
                {'user_id': 'maria', 'moto_id': 'moto6', 'rating': 5.0}
            ]
            self.ratings = pd.DataFrame(ratings)
            
            # Crear amistades simuladas
            friendships = [
                {'user_id': 'admin', 'friend_id': 'test_user'},
                {'user_id': 'test_user', 'friend_id': 'admin'},
                {'user_id': 'admin', 'friend_id': 'maria'},
                {'user_id': 'maria', 'friend_id': 'admin'}
            ]
            self.friendships = pd.DataFrame(friendships)
            
            # Crear interacciones simuladas
            interactions = []
            for _, row in self.ratings.iterrows():
                interactions.append({
                    'user_id': row['user_id'],
                    'moto_id': row['moto_id'],
                    'interaction_type': 'rating',
                    'weight': row['rating']
                })
            self.interactions = pd.DataFrame(interactions)
            
            logger.info("Datos simulados cargados correctamente")
            self.data_loaded = True
        except Exception as e:
            logger.error(f"Error al cargar datos simulados: {str(e)}")
            self.data_loaded = False
    
    def get_recommendations(self, user_id, top_n=5, refresh=True):
        """Obtiene recomendaciones para un usuario."""
        logger.info(f"Generando recomendaciones para usuario {user_id}")
        
        # AÑADIR ESTA SECCIÓN: Actualizar datos desde Neo4j si está disponible
        if refresh:
            try:
                from app.utils import get_db_connection
                connector = get_db_connection()
                if connector and connector.is_connected:
                    # Obtener datos actualizados del usuario
                    query = """
                    MATCH (u:User {user_id: $user_id})
                    RETURN u.user_id as user_id, u.experiencia as experiencia, 
                           u.uso_previsto as uso_previsto, u.presupuesto as presupuesto
                    """
                    result = connector.execute_query(query, {'user_id': user_id})
                    if result and len(result) > 0:
                        # Actualizar datos en memoria
                        user_data = result[0]
                        
                        # Verificar si el usuario existe en el dataframe
                        if user_id in self.users['user_id'].values:
                            # Actualizar usuario existente
                            idx = self.users.index[self.users['user_id'] == user_id].tolist()[0]
                            self.users.loc[idx, 'experiencia'] = user_data.get('experiencia', 'principiante')
                            self.users.loc[idx, 'uso_previsto'] = user_data.get('uso_previsto', 'urbano')
                            # Asegurarse de que el uso previsto no esté vacío
                            if not self.users.loc[idx, 'uso_previsto'] or str(self.users.loc[idx, 'uso_previsto']).strip() == '':
                                self.users.loc[idx, 'uso_previsto'] = 'urbano'
                            self.users.loc[idx, 'presupuesto'] = float(user_data.get('presupuesto', 8000))
                            logger.info(f"Datos de usuario {user_id} actualizados desde Neo4j")
            except Exception as e:
                logger.error(f"Error al refrescar datos desde Neo4j: {str(e)}")
        
        # Verificar y actualizar usuario si no existe
        if user_id not in self.users['user_id'].values:
            logger.warning(f"Usuario {user_id} no encontrado en la base de datos, añadiendo usuario")
            new_user = pd.DataFrame([{
                'user_id': user_id,
                'experiencia': 'principiante',
                'uso_previsto': 'urbano',
                'presupuesto': 8000.0
            }])
            self.users = pd.concat([self.users, new_user], ignore_index=True)
        
        # Mostrar datos de usuario para depuración
        user_idx = self.users[self.users['user_id'] == user_id].index[0]
        logger.info(f"Datos del usuario {user_id}:")
        logger.info(f"  Experiencia: {self.users.loc[user_idx, 'experiencia']}")
        logger.info(f"  Uso previsto: {self.users.loc[user_idx, 'uso_previsto']}")
        logger.info(f"  Presupuesto: {self.users.loc[user_idx, 'presupuesto']}")
        
        # Obtener recomendaciones
        return self._get_moto_ideal_recommendations(user_id, top_n)
    
    def _get_moto_ideal_recommendations(self, user_id, n=5):
        """Obtiene recomendaciones basadas en moto ideal."""
        try:
            # Crear y preparar MotoIdealRecommender
            from app.algoritmo.moto_ideal import MotoIdealRecommender
            
            # Obtener datos del usuario
            user_data = self.users[self.users['user_id'] == user_id].iloc[0]
            experiencia = user_data['experiencia']
            presupuesto = user_data['presupuesto']
            uso = user_data['uso_previsto']
            
            # Log para debugging
            logger.info(f"Calculando recomendaciones para {user_id}: experiencia={experiencia}, "
                       f"presupuesto={presupuesto}, uso={uso}")
            
            # Filtrar motos según criterios básicos
            motos_filtradas = self.motos.copy()
            
            # Filtro por experiencia y potencia
            if experiencia == 'principiante':
                # Para principiantes: priorizar motos de baja/media potencia
                motos_filtradas['score'] = motos_filtradas.apply(
                    lambda x: 5.0 if x['potencia'] < 50 else
                             3.0 if x['potencia'] < 70 else
                             1.0, axis=1)
            elif experiencia == 'intermedio':
                # Para intermedios: motos de potencia media
                motos_filtradas['score'] = motos_filtradas.apply(
                    lambda x: 5.0 if 50 <= x['potencia'] <= 100 else
                             3.0 if x['potencia'] < 125 else
                             1.0, axis=1)
            else:
                # Para expertos: motos de alta potencia
                motos_filtradas['score'] = motos_filtradas.apply(
                    lambda x: 5.0 if x['potencia'] > 100 else
                             3.0 if x['potencia'] >= 70 else
                             1.0, axis=1)
                             
            # Filtro por presupuesto
            motos_filtradas['score'] = motos_filtradas.apply(
                lambda x: x['score'] + 2.0 if x['precio'] <= presupuesto else
                         x['score'] + 0.5 if x['precio'] <= presupuesto * 1.2 else
                         x['score'] - 1.0, axis=1)
                         
            # Filtro por tipo de uso
            if uso == 'urbano':
                motos_filtradas['score'] = motos_filtradas.apply(
                    lambda x: x['score'] + 2.0 if x['tipo'] in ['naked', 'scooter'] else x['score'], axis=1)
            elif uso == 'carretera':
                motos_filtradas['score'] = motos_filtradas.apply(
                    lambda x: x['score'] + 2.0 if x['tipo'] in ['sport', 'touring'] else x['score'], axis=1)
            elif uso == 'offroad':
                motos_filtradas['score'] = motos_filtradas.apply(
                    lambda x: x['score'] + 2.0 if x['tipo'] in ['adventure', 'enduro'] else x['score'], axis=1)
            
            # Ordenar por puntuación
            top_motos = motos_filtradas.sort_values(by='score', ascending=False).head(n)
            
            # Preparar resultados
            result = []
            for _, row in top_motos.iterrows():
                reasons = []
                
                # Añadir razones específicas
                if experiencia == 'principiante' and row['potencia'] < 50:
                    reasons.append("Potencia ideal para principiantes")
                elif experiencia == 'intermedio' and 50 <= row['potencia'] <= 100:
                    reasons.append("Potencia adecuada para nivel intermedio")
                elif experiencia in ['avanzado', 'experto'] and row['potencia'] > 100:
                    reasons.append("Alta potencia ideal para expertos")
                    
                if row['precio'] <= presupuesto:
                    reasons.append(f"Dentro de tu presupuesto de {presupuesto}")
                    
                if uso == 'urbano' and row['tipo'] in ['naked', 'scooter']:
                    reasons.append("Ideal para uso urbano")
                elif uso == 'carretera' and row['tipo'] in ['sport', 'touring']:
                    reasons.append("Ideal para carretera")
                elif uso == 'offroad' and row['tipo'] in ['adventure', 'enduro']:
                    reasons.append("Ideal para off-road")
                    
                if not reasons:
                    reasons.append("Basado en tu perfil general")
                    
                result.append((row['moto_id'], row['score'], reasons))
                
            logger.info(f"Recomendaciones obtenidas para {user_id}: {len(result)} motos")
            return result
            
        except Exception as e:
            logger.error(f"Error en moto ideal: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _get_friend_recommendations(self, user_id, n=5):
        """Obtiene recomendaciones basadas en amigos."""
        try:
            # Si no hay datos de amistades, devolver lista vacía
            if self.friendships is None or self.friendships.empty:
                return []
            
            # Si no hay valoraciones, devolver lista vacía
            if self.ratings is None or self.ratings.empty:
                return []
                
            # Preparar datos para LabelPropagation
            friendships_data = list(self.friendships[['user_id', 'friend_id']].itertuples(index=False, name=None))
            ratings_data = list(self.ratings[['user_id', 'moto_id', 'rating']].itertuples(index=False, name=None))
            
            # Construir grafo social
            self.label_propagation.build_social_graph(friendships_data)
            self.label_propagation.set_user_preferences(ratings_data)
            
            # Propagar etiquetas y obtener recomendaciones
            self.label_propagation.propagate_labels()
            friend_recs = self.label_propagation.get_friend_recommendations(user_id, top_n=n)
            
            # Convertir al formato estándar
            result = []
            for moto_id, score in friend_recs:
                moto_info = self.motos[self.motos['moto_id'] == moto_id].iloc[0] if moto_id in self.motos['moto_id'].values else None
                
                # Generar razones
                reasons = ["Recomendado por tus amigos"]
                if moto_info is not None:
                    reasons.append(f"{moto_info['marca']} {moto_info['modelo']}")
                
                result.append((moto_id, float(score), reasons))
            
            return result
            
        except Exception as e:
            logger.error(f"Error en recomendaciones de amigos: {str(e)}")
            return []
    
    def _get_popular_recommendations(self, n=5):
        """Obtiene recomendaciones de motos populares usando PageRank."""
        try:
            # Si no hay interacciones, usar ratings para calcular popularidad
            if self.interactions is None or self.interactions.empty:
                if self.ratings is None or self.ratings.empty:
                    return []
                
                # Crear interacciones desde ratings
                interactions_data = []
                for _, row in self.ratings.iterrows():
                    interactions_data.append((row['user_id'], row['moto_id'], row['rating']))
            else:
                # Usar interacciones existentes
                if 'weight' not in self.interactions.columns:
                    self.interactions['weight'] = 1.0
                
                interactions_data = list(self.interactions[['user_id', 'moto_id', 'weight']].itertuples(index=False, name=None))
            
            # Construir grafo y ejecutar PageRank
            self.pagerank.build_graph(interactions_data)
            self.pagerank.run()
            
            # Obtener motos populares
            popular_recs = self.pagerank.get_popular_motos(top_n=n)
            
            # Convertir al formato estándar
            result = []
            for moto_id, score in popular_recs:
                moto_info = self.motos[self.motos['moto_id'] == moto_id].iloc[0] if moto_id in self.motos['moto_id'].values else None
                
                # Generar razones
                reasons = ["Moto popular entre usuarios"]
                if moto_info is not None:
                    reasons.append(f"{moto_info['marca']} {moto_info['modelo']}")
                
                result.append((moto_id, float(score), reasons))
            
            return result
            
        except Exception as e:
            logger.error(f"Error en recomendaciones populares: {str(e)}")
            return []
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.connector:
            self.connector.close()
