"""
Implementación aislada del algoritmo MotoIdealRecommender para usar sin dependencias de Flask/Werkzeug.
Este archivo puede ser utilizado tanto dentro de la aplicación principal como de manera independiente
para pruebas o diagnósticos.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MotoRecommender")

class MotoIdealRecommender:
    """
    Recomendador de motos ideales basado en perfil de usuario y características de motos.
    Esta versión funciona de manera independiente sin requerir Flask o Neo4j.
    """
    def __init__(self):
        """
        Inicializa el recomendador de motos ideal.
        """
        self.users_features = None  # Características de los usuarios
        self.motos_features = None  # Características de las motos
        self.ratings_matrix = None  # Matriz de valoraciones usuario-moto
        self.similarity_users = None  # Similitud entre usuarios
        self.similarity_motos = None  # Similitud entre motos
        
    def load_data(self, user_features, moto_features, user_ratings):
        """
        Carga los datos necesarios para las recomendaciones.
        
        Args:
            user_features (pandas.DataFrame): Características de los usuarios 
                (experiencia, uso_previsto, presupuesto, etc.)
            moto_features (pandas.DataFrame): Características de las motos 
                (potencia, tipo, precio, etc.)
            user_ratings (pandas.DataFrame): Valoraciones de usuarios para motos
                (user_id, moto_id, rating)
        """
        logger.info("Cargando datos para el recomendador...")
        self.users_features = user_features
        self.motos_features = moto_features
        
        # Crear la matriz de valoraciones
        self.ratings_matrix = pd.pivot_table(
            user_ratings, 
            values='rating', 
            index='user_id', 
            columns='moto_id', 
            fill_value=0
        )
        
        # Procesar datos para el uso posterior
        self._preprocess_data()
        
    def _preprocess_data(self):
        """
        Preprocesa los datos para calcular similitudes.
        """
        # Calcular matrices de similitud
        self._calculate_similarities()
        
    def _calculate_similarities(self):
        """
        Calcula matrices de similitud entre usuarios y entre motos.
        """
        logger.info("Calculando similitudes...")
        # Similitud entre usuarios basada en sus valoraciones
        if len(self.ratings_matrix) > 1:  # Al menos 2 usuarios
            self.similarity_users = cosine_similarity(self.ratings_matrix)
        else:
            self.similarity_users = [[1.0]]  # Solo un usuario
        
        # Preparar características numéricas para el cálculo de similitud de motos
        # Excluir columnas no numéricas
        exclude_cols = ['moto_id', 'modelo', 'marca', 'tipo']
        features_for_sim = self.motos_features.select_dtypes(include=['number'])
        features_for_sim = features_for_sim.drop([col for col in exclude_cols if col in features_for_sim.columns], axis=1, errors='ignore')
        
        if not features_for_sim.empty and features_for_sim.shape[1] > 0:
            self.similarity_motos = cosine_similarity(features_for_sim)
        else:
            # Crear una matriz de similitud de identidad si no hay características numéricas
            n_motos = len(self.motos_features)
            self.similarity_motos = np.eye(n_motos)
    
    def get_moto_ideal(self, user_id, top_n=5):
        """
        Genera recomendaciones de motos ideales para un usuario.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n (int): Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score, reasons) ordenadas por puntuación
        """
        logger.info(f"Generando recomendaciones para usuario: {user_id}")
        
        # Verificar si el usuario existe
        if user_id not in self.users_features['user_id'].values:
            logger.warning(f"Usuario {user_id} no encontrado en los datos")
            return []
            
        # Obtener perfil del usuario
        user_profile = self.users_features[self.users_features['user_id'] == user_id].iloc[0]
        
        # Calcular recomendaciones para cada moto
        recommendations = {}
        
        for _, moto in self.motos_features.iterrows():
            moto_id = moto['moto_id']
            score, reasons = self._evaluate_moto_for_user(user_profile, moto)
            recommendations[moto_id] = (score, reasons)
            
        # Ordenar por puntuación
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1][0], reverse=True)
        
        # Formatear resultados con razones
        result = [(moto_id, score, reasons) for moto_id, (score, reasons) in sorted_recs[:top_n]]
        
        logger.info(f"Generadas {len(result)} recomendaciones para {user_id}")
        return result
    
    def _evaluate_moto_for_user(self, user_profile, moto):
        """
        Evalúa una moto para un usuario específico basado en su perfil y las características de la moto.
        
        Args:
            user_profile: Perfil del usuario (Series con experiencia, uso_previsto, presupuesto)
            moto: Características de la moto (Series con tipo, potencia, precio)
            
        Returns:
            tuple: (score, reasons) donde score es un float y reasons es una lista de strings
        """
        score = 0
        reasons = []
        
        # 1. Verificar compatibilidad de experiencia y potencia
        experiencia = user_profile['experiencia']
        potencia = moto['potencia']
        
        # Reglas para experiencia
        if experiencia == 'principiante':
            # Para principiantes, motos con poca potencia
            if potencia <= 50:
                score += 3
                reasons.append("Potencia adecuada para principiantes")
            elif potencia <= 80:
                score += 1
                reasons.append("Potencia aceptable para principiantes con precaución")
            else:
                score -= 2
                reasons.append("Potencia excesiva para principiantes")
                
        elif experiencia == 'intermedio':
            # Para nivel intermedio, potencia media
            if 50 <= potencia <= 100:
                score += 3
                reasons.append("Potencia ideal para nivel intermedio")
            elif potencia <= 150:
                score += 1
                reasons.append("Potencia adecuada para nivel intermedio avanzado")
            elif potencia < 50:
                score -= 1
                reasons.append("Potencia insuficiente para nivel intermedio")
            else:
                score -= 0.5
                reasons.append("Potencia alta para nivel intermedio")
                
        elif experiencia == 'experto':
            # Para expertos, más potencia
            if potencia >= 100:
                score += 3
                reasons.append("Potencia adecuada para expertos")
            elif potencia >= 70:
                score += 1
                reasons.append("Potencia aceptable para expertos")
            else:
                score -= 1
                reasons.append("Potencia baja para el nivel de experiencia")
        
        # 2. Compatibilidad de tipo según uso previsto
        uso = user_profile['uso_previsto']
        tipo = moto['tipo']
        
        # Reglas para uso previsto
        if uso == 'urbano':
            if tipo in ['naked', 'scooter']:
                score += 3
                reasons.append(f"Tipo {tipo} ideal para uso urbano")
            elif tipo in ['sport', 'custom']:
                score += 1
                reasons.append(f"Tipo {tipo} aceptable para uso urbano")
            else:
                score -= 0.5
                reasons.append(f"Tipo {tipo} no es óptimo para uso urbano")
                
        elif uso == 'carretera':
            if tipo in ['sport', 'touring']:
                score += 3
                reasons.append(f"Tipo {tipo} ideal para carretera")
            elif tipo in ['naked', 'adventure']:
                score += 1
                reasons.append(f"Tipo {tipo} bueno para carretera")
            else:
                score -= 0.5
                reasons.append(f"Tipo {tipo} no es óptimo para carretera")
                
        elif uso == 'offroad':
            if tipo in ['enduro', 'cross', 'adventure']:
                score += 3
                reasons.append(f"Tipo {tipo} ideal para offroad")
            elif tipo in ['trail']:
                score += 1
                reasons.append(f"Tipo {tipo} aceptable para offroad")
            else:
                score -= 1
                reasons.append(f"Tipo {tipo} no adecuado para offroad")
        
        # 3. Compatibilidad de precio
        presupuesto = user_profile['presupuesto']
        precio = moto['precio']
        
        if precio <= presupuesto:
            score += 2
            reasons.append(f"Precio ({precio}€) dentro del presupuesto ({presupuesto}€)")
        elif precio <= presupuesto * 1.1:
            score += 0.5
            reasons.append(f"Precio ({precio}€) ligeramente sobre el presupuesto ({presupuesto}€)")
        else:
            score -= 1
            diff_percent = ((precio - presupuesto) / presupuesto) * 100
            reasons.append(f"Precio ({precio}€) excede el presupuesto en {diff_percent:.1f}%")
        
        # Normalizar puntuación para que esté entre 0 y 5
        normalized_score = max(0, min(5, score))
        
        return normalized_score, reasons


# Función para ejecutar pruebas del algoritmo con datos simulados
def run_test_with_sample_data():
    """
    Ejecuta una prueba del algoritmo con datos de ejemplo.
    """
    print("\n==== PRUEBA DEL ALGORITMO MOTOIDEALRECOMMENDER ====\n")
    
    # Datos simulados de usuarios
    users = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000},
        {'user_id': 'user3', 'experiencia': 'experto', 'uso_previsto': 'offroad', 'presupuesto': 15000}
    ]
    user_df = pd.DataFrame(users)
    
    # Datos simulados de motos
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'potencia': 15, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Kawasaki ZX-10R', 'marca': 'Kawasaki', 'tipo': 'sport', 'potencia': 200, 'precio': 18000},
        {'moto_id': 'moto3', 'modelo': 'BMW R1250GS', 'marca': 'BMW', 'tipo': 'adventure', 'potencia': 136, 'precio': 20000},
        {'moto_id': 'moto4', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'potencia': 73, 'precio': 8000}
    ]
    moto_df = pd.DataFrame(motos)
    
    # Datos simulados de valoraciones
    ratings = [
        {'user_id': 'user1', 'moto_id': 'moto1', 'rating': 5},
        {'user_id': 'user1', 'moto_id': 'moto4', 'rating': 4},
        {'user_id': 'user2', 'moto_id': 'moto2', 'rating': 5},
        {'user_id': 'user2', 'moto_id': 'moto3', 'rating': 3},
        {'user_id': 'user3', 'moto_id': 'moto2', 'rating': 4},
        {'user_id': 'user3', 'moto_id': 'moto3', 'rating': 5}
    ]
    ratings_df = pd.DataFrame(ratings)
    
    print(f"Usuarios creados: {len(user_df)}")
    print(f"Motos creadas: {len(moto_df)}")
    print(f"Valoraciones creadas: {len(ratings_df)}")
    
    # Probar con cada usuario
    try:
        for user_id in user_df['user_id']:
            print(f"\nProbando recomendaciones para usuario: {user_id}")
            
            # Crear recomendador
            recommender = MotoIdealRecommender()
            
            # Cargar datos
            recommender.load_data(user_df, moto_df, ratings_df)
            
            # Obtener recomendaciones
            recommendations = recommender.get_moto_ideal(user_id, top_n=2)
            
            print(f"\nRecomendaciones para {user_id}:")
            if recommendations:
                for moto_id, score, reasons in recommendations:
                    moto = moto_df[moto_df['moto_id'] == moto_id].iloc[0]
                    print(f"- {moto['modelo']} ({moto['marca']})")
                    print(f"  Score: {score:.2f}")
                    print(f"  Razones: {', '.join(reasons)}")
            else:
                print("No se generaron recomendaciones")
        
        print("\nPrueba completada exitosamente")
        
    except Exception as e:
        print(f"\nError en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n==== FIN DE LA PRUEBA ====\n")


# Ejecutar la prueba si este script se ejecuta directamente
if __name__ == "__main__":
    run_test_with_sample_data()
