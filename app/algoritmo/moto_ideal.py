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
        """
        Calcula similitudes entre usuarios y entre motos.
        """
        try:
            # Calcular similitud entre motos basada en características
            if self.motos_features_processed is not None and not self.motos_features_processed.empty:
                # Crear copia para manipulación
                features_for_similarity = self.motos_features_processed.copy()
                
                # Excluir columna de ID para el cálculo de similitud
                if 'moto_id' in features_for_similarity.columns:
                    features_for_similarity = features_for_similarity.drop('moto_id', axis=1)
                
                # Verificar que todos los datos sean numéricos
                cat_columns = features_for_similarity.select_dtypes(include=['object']).columns
                if not cat_columns.empty:
                    logger.warning(f"Excluyendo columnas categóricas de similitud: {cat_columns.tolist()}")
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