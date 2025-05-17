"""
Algoritmo de recomendación de moto ideal basado en las preferencias del usuario.
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MotoIdealRecommender:
    """
    Recomendador que encuentra la moto ideal para un usuario basado en sus preferencias
    y características de las motos.
    """
    
    def __init__(self):
        """Inicializa el recomendador de moto ideal."""
        self.users_features = None
        self.motos_features = None
        self.motos_features_processed = None  # Variable para almacenar datos procesados
        self.ratings_matrix = None
        self.similarity_users = None
        self.similarity_motos = None
        
    def load_data(self, users_df, motos_df, ratings_df=None):
        """
        Carga datos de usuarios, motos y valoraciones.
        
        Args:
            users_df (pandas.DataFrame): DataFrame con datos de usuarios
            motos_df (pandas.DataFrame): DataFrame con datos de motos
            ratings_df (pandas.DataFrame, optional): DataFrame con valoraciones
        """
        self.users_features = users_df.copy() if users_df is not None else pd.DataFrame()
        self.motos_features = motos_df.copy() if motos_df is not None else pd.DataFrame()
        
        if ratings_df is not None and not ratings_df.empty:
            self.ratings_df = ratings_df.copy()
            
            # Crear matriz de valoraciones (usuarios x motos)
            user_ids = self.users_features['user_id'].unique()
            moto_ids = self.motos_features['moto_id'].unique()
            
            # Inicializar matriz con ceros y tipo float64 explícitamente
            self.ratings_matrix = pd.DataFrame(0.0, index=user_ids, columns=moto_ids, dtype=float)
                
            # Llenar la matriz con valoraciones
            for _, row in self.ratings_df.iterrows():
                # Convertir valoraciones a float para evitar warnings
                self.ratings_matrix.at[row['user_id'], row['moto_id']] = float(row['rating'])
        
        # Preprocesar datos para cálculos posteriores
        if not self.motos_features.empty:
            self._preprocess_data()
        
    def _preprocess_data(self):
        """
        Preprocesa los datos para calcular similitudes.
        """
        # Importar DataPreprocessor para procesar los datos
        try:
            from .utils import DataPreprocessor
        except ImportError:
            try:
                from app.algoritmo.utils import DataPreprocessor
            except ImportError:
                logger.error("No se pudo importar DataPreprocessor")
                return
            
        # Preservar moto_id para reindexación posterior
        moto_ids = None
        if 'moto_id' in self.motos_features.columns:
            moto_ids = self.motos_features['moto_id'].copy()
            
        # PASO 1: Proteger columna moto_id durante el procesamiento
        if moto_ids is not None:
            processed_df = self.motos_features.drop('moto_id', axis=1)
        else:
            processed_df = self.motos_features.copy()
            
        # PASO 2: Codificar variables categóricas
        try:
            self.motos_features_processed = DataPreprocessor.encode_categorical(processed_df)
            
            # PASO 3: Normalizar variables numéricas
            numeric_columns = ['potencia', 'peso', 'cilindrada', 'precio']
            numeric_columns = [col for col in numeric_columns if col in self.motos_features_processed.columns]
            
            if numeric_columns:
                self.motos_features_processed = DataPreprocessor.normalize_features(
                    self.motos_features_processed, 
                    columns=numeric_columns
                )
                
            # PASO 4: Reincorporar moto_id
            if moto_ids is not None:
                self.motos_features_processed['moto_id'] = moto_ids
                
            logger.info(f"Datos de motos procesados. Columnas: {self.motos_features_processed.columns.tolist()}")
            
            # Calcular similitudes
            self._calculate_similarities()
        except Exception as e:
            logger.error(f"Error en preprocesamiento: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
    def _calculate_similarities(self):
        """Calcula similitudes entre usuarios y entre motos."""
        try:
            # Calcular similitud entre motos basada en características
            if self.motos_features_processed is not None and not self.motos_features_processed.empty:
                # Crear copia para manipulación
                features_for_similarity = self.motos_features_processed.copy()
                
                # Excluir columna de ID para el cálculo de similitud
                if 'moto_id' in features_for_similarity.columns:
                    features_for_similarity = features_for_similarity.drop('moto_id', axis=1)
                
                # AÑADIR ESTO: Eliminar filas o columnas con NaN
                features_for_similarity = features_for_similarity.fillna(0)  # Rellenar NaN con 0
                
                # Verificar que todos los datos sean numéricos
                cat_columns = features_for_similarity.select_dtypes(include=['object']).columns
                if not cat_columns.empty:
                    features_for_similarity = features_for_similarity.select_dtypes(exclude=['object'])
                
                # Calcular matriz de similitud si hay datos
                if not features_for_similarity.empty:
                    self.similarity_motos = cosine_similarity(features_for_similarity.values)
                else:
                    logger.warning("No hay suficientes datos numéricos para calcular similitud")
        except Exception as e:
            logger.error(f"Error al calcular similitudes: {str(e)}")
            self.similarity_motos = None
            
    def get_moto_ideal(self, user_id, top_n=5):
        """
        Obtiene las motos ideales para un usuario.
        
        Args:
            user_id (str): ID del usuario
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score)
        """
        # Verificar si el usuario existe en nuestros datos
        if user_id not in self.users_features['user_id'].values:
            logger.warning(f"El usuario {user_id} no existe en la base de datos")
            return []
            
        try:
            # Obtener índice del usuario
            user_idx = self.users_features[self.users_features['user_id'] == user_id].index[0]
            
            # Extraer datos del usuario con valores predeterminados por si falta alguno
            user_data = {
                'experiencia': str(self.users_features.loc[user_idx, 'experiencia']).lower() 
                    if 'experiencia' in self.users_features.columns else 'principiante',
                'presupuesto': float(self.users_features.loc[user_idx, 'presupuesto']) 
                    if 'presupuesto' in self.users_features.columns else 8000,
                'uso_previsto': str(self.users_features.loc[user_idx, 'uso_previsto']).lower() 
                    if 'uso_previsto' in self.users_features.columns else 'urbano'
            }
            
            # Logs para depuración
            logger.info(f"Calculando moto ideal para usuario {user_id}, experiencia: {user_data['experiencia']}, " 
                       f"presupuesto: {user_data['presupuesto']}, uso: {user_data['uso_previsto']}")
            
            # Calcular puntuación para cada moto
            scores = []
            
            for _, moto_row in self.motos_features.iterrows():
                moto_id = moto_row['moto_id']
                compatibility_score = 0.0
                reasons = []
                
                # 1. Factor experiencia vs potencia
                if 'potencia' in moto_row:
                    try:
                        potencia = float(moto_row['potencia'])
                        
                        # Lógica de compatibilidad según experiencia
                        if user_data['experiencia'] in ('principiante', 'inexperto'):
                            if potencia < 50:
                                compatibility_score += 3.0
                                reasons.append("Baja potencia ideal para principiantes")
                            elif potencia < 70:
                                compatibility_score += 1.5
                                reasons.append("Potencia moderada aceptable para principiantes")
                            else:
                                compatibility_score -= 1.0
                                reasons.append("Potencia demasiado alta para principiantes")
                        elif user_data['experiencia'] == 'intermedio':
                            if 50 <= potencia <= 100:
                                compatibility_score += 3.0
                                reasons.append("Potencia media ideal para nivel intermedio")
                            elif potencia < 50 or potencia <= 120:
                                compatibility_score += 1.5
                                reasons.append("Potencia aceptable para nivel intermedio")
                            else:
                                compatibility_score -= 0.5
                                reasons.append("Potencia algo elevada para tu experiencia")
                        elif user_data['experiencia'] in ('avanzado', 'experto'):
                            if potencia > 100:
                                compatibility_score += 3.0
                                reasons.append("Alta potencia ideal para expertos")
                            elif potencia >= 70:
                                compatibility_score += 1.5
                                reasons.append("Potencia aceptable para nivel avanzado")
                            else:
                                compatibility_score -= 1.0
                                reasons.append("Potencia insuficiente para nivel avanzado")
                    except (ValueError, TypeError):
                        pass
                
                # 2. Factor presupuesto vs precio
                if 'precio' in moto_row:
                    try:
                        precio = float(moto_row['precio'])
                        
                        if precio <= user_data['presupuesto']:
                            compatibility_score += 2.0
                            reasons.append(f"Dentro de tu presupuesto ({precio} ≤ {user_data['presupuesto']})")
                        elif precio <= user_data['presupuesto'] * 1.2:
                            compatibility_score += 0.5
                            reasons.append(f"Ligeramente por encima de tu presupuesto ({precio} vs {user_data['presupuesto']})")
                        else:
                            compatibility_score -= 2.0
                            reasons.append(f"Fuera de tu presupuesto ({precio} > {user_data['presupuesto']})")
                    except (ValueError, TypeError):
                        pass
                
                # 3. Factor uso previsto vs tipo de moto
                if 'tipo' in moto_row:
                    tipo = str(moto_row['tipo']).lower()
                    
                    # Mapeo mejorado de uso previsto a tipos de motos
                    if user_data['uso_previsto'] in ('urbano', 'ciudad'):
                        if tipo in ('naked', 'scooter'):
                            compatibility_score += 2.0
                            reasons.append(f"Tipo {tipo} ideal para uso urbano")
                    elif user_data['uso_previsto'] in ('carretera', 'viaje', 'paseo'):
                        if tipo in ('sport', 'touring', 'adventure'):
                            compatibility_score += 2.0
                            reasons.append(f"Tipo {tipo} ideal para uso en carretera/viajes")
                    elif user_data['uso_previsto'] == 'offroad':
                        if tipo in ('adventure', 'enduro'):
                            compatibility_score += 2.0
                            reasons.append(f"Tipo {tipo} ideal para uso offroad")
                
                # Añadir puntuación final y razones
                scores.append((moto_id, compatibility_score, reasons))
            
            # Ordenar por puntuación descendente
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            
            # Para depuración mostrar top recomendación
            if sorted_scores:
                top_moto = sorted_scores[0]
                logger.info(f"Moto ideal para {user_id}: {top_moto[0]} con puntuación {top_moto[1]}")
                logger.info(f"Razones: {top_moto[2]}")
            
            # Devolver solo moto_id y puntuación para compatibilidad
            return [(moto_id, score) for moto_id, score, _ in sorted_scores[:top_n]]
        except Exception as e:
            logger.error(f"Error al calcular moto ideal para {user_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
        
    def get_recommendations_from_neo4j(self, user_data, neo4j_driver, top_n=20):
        """
        Obtiene recomendaciones de Neo4j basadas en preferencias del usuario.
        
        Args:
            user_data (dict): Datos del usuario (experiencia, presupuesto, uso_previsto, marcas_preferidas)
            neo4j_driver: Driver de conexión a Neo4j
            top_n (int): Número de recomendaciones a devolver
            
        Returns:
            list: Lista de diccionarios con las recomendaciones y sus puntuaciones
        """
        try:
            # Extraer marcas preferidas (si existen)
            selected_brands = user_data.get('marcas_preferidas', [])
            if not selected_brands:
                logger.info("No hay marcas seleccionadas, se usará lista vacía")
                selected_brands = []
                
            # Determinar tipo preferido basado en uso_previsto
            pref_tipo = ""
            if user_data.get('uso_previsto') == 'urbano':
                pref_tipo = "scooter"
            elif user_data.get('uso_previsto') == 'carretera':
                pref_tipo = "sport"
            elif user_data.get('uso_previsto') == 'offroad':
                pref_tipo = "adventure"
                
            # Obtener presupuesto máximo
            max_price = float(user_data.get('presupuesto', 10000))
            
            # Consulta Cypher mejorada
            query = """
            // Consulta de recomendación mejorada
            MATCH (m:Moto)-[:FABRICADA_POR]->(b:Marca)
            WHERE b.nombre IN $selectedBrands OR size($selectedBrands) = 0

            // Encontrar motos similares
            WITH m AS startMoto
            MATCH (startMoto)-[:SIMILAR_CILINDRADA|SIMILAR_PRECIO*1..2]-(recommended:Moto)
            WHERE startMoto <> recommended

            // Calcular puntuación
            WITH recommended, COUNT(*) AS pathCount,
                 CASE 
                     WHEN recommended.marca IN $selectedBrands THEN 3.0 ELSE 0 
                 END AS brandBonus,
                 CASE 
                     WHEN recommended.tipo = $prefTipo THEN 2.0 ELSE 0
                 END AS tipoBonus,
                 CASE
                     WHEN recommended.precio <= $maxPrice THEN 1.0 ELSE -1.0
                 END AS priceBonus
            WITH recommended, 
                 pathCount*0.5 + brandBonus + tipoBonus + priceBonus AS totalScore
            WHERE totalScore > 0

            // Devolver recomendaciones ordenadas por puntuación
            RETURN recommended.marca AS marca,
                   recommended.modelo AS modelo,
                   recommended.anio AS anio,
                   recommended.precio AS precio,
                   recommended.tipo AS tipo,
                   recommended.cilindrada AS cilindrada,
                   recommended.potencia AS potencia,
                   recommended.imagen AS imagen,
                   recommended.url AS url,
                   totalScore AS score
            ORDER BY score DESC
            LIMIT $topN
            """
            
            # Parámetros para la consulta
            params = {
                "selectedBrands": selected_brands,
                "prefTipo": pref_tipo,
                "maxPrice": max_price,
                "topN": top_n
            }
            
            logger.info(f"Ejecutando consulta Neo4j con parámetros: {params}")
            
            # Ejecutar consulta
            with neo4j_driver.session() as session:
                result = session.run(query, params)
                recommendations = [dict(record) for record in result]
                
            logger.info(f"Obtenidas {len(recommendations)} recomendaciones desde Neo4j")
            return recommendations
        
        except Exception as e:
            logger.error(f"Error al obtener recomendaciones desde Neo4j: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def get_hybrid_recommendations(self, user_id, neo4j_driver, top_n=10):
        """
        Combina las recomendaciones de moto ideal con las obtenidas de Neo4j.
        
        Args:
            user_id (str): ID del usuario
            neo4j_driver: Conexión a Neo4j
            top_n (int): Número de recomendaciones
            
        Returns:
            list: Lista de recomendaciones combinadas
        """
        # Verificar si el usuario existe
        if user_id not in self.users_features['user_id'].values:
            logger.warning(f"Usuario {user_id} no encontrado en la base de datos")
            return []
            
        # Obtener datos del usuario
        user_idx = self.users_features[self.users_features['user_id'] == user_id].index[0]
        user_data = {
            'experiencia': str(self.users_features.loc[user_idx, 'experiencia']).lower() 
                if 'experiencia' in self.users_features.columns else 'principiante',
            'presupuesto': float(self.users_features.loc[user_idx, 'presupuesto']) 
                if 'presupuesto' in self.users_features.columns else 8000,
            'uso_previsto': str(self.users_features.loc[user_idx, 'uso_previsto']).lower() 
                if 'uso_previsto' in self.users_features.columns else 'urbano',
            'marcas_preferidas': self.users_features.loc[user_idx, 'marcas_preferidas'].split(',') 
                if 'marcas_preferidas' in self.users_features.columns and 
                   isinstance(self.users_features.loc[user_idx, 'marcas_preferidas'], str) 
                else []
        }
        
        # 1. Obtener recomendaciones del algoritmo tradicional
        traditional_recs = self.get_moto_ideal(user_id, top_n=top_n)
        
        # 2. Obtener recomendaciones basadas en Neo4j
        graph_recs = self.get_recommendations_from_neo4j(user_data, neo4j_driver, top_n=top_n)
        
        # 3. Combinar resultados (dar mayor peso a Neo4j si hay marcas seleccionadas)
        neo4j_weight = 0.7 if user_data['marcas_preferidas'] else 0.5
        trad_weight = 1.0 - neo4j_weight
        
        # Preparar diccionario para combinar resultados
        combined_scores = {}
        
        # Añadir recomendaciones tradicionales
        for moto_id, score in traditional_recs:
            combined_scores[moto_id] = {
                'score': score * trad_weight,
                'source': 'traditional'
            }
        
        # Añadir recomendaciones de Neo4j
        for rec in graph_recs:
            # Crear un identificador único para la moto
            neo4j_moto_id = f"{rec['marca']}_{rec['modelo']}"
            
            # Ver si ya existe en las recomendaciones tradicionales
            matching_id = None
            for moto_id in combined_scores:
                # Buscar en motos_features la marca y modelo que corresponden a este moto_id
                if moto_id in self.motos_features['moto_id'].values:
                    moto_idx = self.motos_features[self.motos_features['moto_id'] == moto_id].index[0]
                    marca = self.motos_features.loc[moto_idx, 'marca'] if 'marca' in self.motos_features.columns else ""
                    modelo = self.motos_features.loc[moto_idx, 'modelo'] if 'modelo' in self.motos_features.columns else ""
                    
                    if marca == rec['marca'] and modelo == rec['modelo']:
                        matching_id = moto_id
                        break
            
            if matching_id:
                # Si ya existe, combinar puntuaciones
                combined_scores[matching_id]['score'] += rec['score'] * neo4j_weight
                combined_scores[matching_id]['source'] = 'hybrid'
                # Añadir datos adicionales de Neo4j si no existen
                if 'imagen' not in combined_scores[matching_id] and 'imagen' in rec:
                    combined_scores[matching_id]['imagen'] = rec['imagen']
                if 'url' not in combined_scores[matching_id] and 'url' in rec:
                    combined_scores[matching_id]['url'] = rec['url']
            else:
                # Si es nueva, añadir con todos sus datos
                rec_copy = rec.copy()
                rec_copy['score'] = rec['score'] * neo4j_weight
                rec_copy['source'] = 'neo4j'
                rec_copy['moto_id'] = neo4j_moto_id  # Usar ID generado
                combined_scores[neo4j_moto_id] = rec_copy
        
        # Convertir a lista y ordenar por puntuación
        final_recommendations = list(combined_scores.values())
        final_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return final_recommendations[:top_n]