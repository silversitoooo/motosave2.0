"""
Integrador para el algoritmo standalone y la aplicación principal.
Este archivo actúa como un puente entre la versión standalone del algoritmo
y la versión que utiliza Neo4j.
"""
import pandas as pd
import logging
from algoritmo_standalone import MotoIdealRecommender

# Intentar importar el DatabaseConnector
try:
    from app.algoritmo.utils import DatabaseConnector
except ImportError:
    # Si no se puede importar, usamos una versión simplificada
    logger.warning("No se pudo importar DatabaseConnector, se usará una versión simplificada")
    DatabaseConnector = None

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MotoRecommenderIntegration")

class MotoRecommenderAdapter:
    """
    Adaptador para usar el recomendador standalone en la aplicación principal.
    """
    def __init__(self, db_connector=None, uri=None, user=None, password=None):
        """
        Inicializa el adaptador.
        
        Args:
            db_connector: Opcional. Si se proporciona, se usará para obtener datos de Neo4j.
            uri: URI de conexión a Neo4j (bolt://localhost:7687)
            user: Usuario de Neo4j
            password: Contraseña de Neo4j
        """
        # Si se proporciona un conector de base de datos, lo usamos
        if db_connector:
            self.db_connector = db_connector
        # Si no, y se proporcionan los parámetros de conexión, creamos uno nuevo
        elif uri and user and password and DatabaseConnector:
            try:
                self.db_connector = DatabaseConnector(uri=uri, user=user, password=password)
                logger.info(f"Conexión establecida con Neo4j en {uri}")
            except Exception as e:
                logger.error(f"Error al conectar con Neo4j: {str(e)}")
                self.db_connector = None
        else:
            self.db_connector = None
            
        self.recommender = MotoIdealRecommender()
        self.data_loaded = False
        
    def test_connection(self):
        """Prueba la conexión a Neo4j"""
        if self.db_connector:
            try:
                # Intentar una consulta simple
                result = self.db_connector.session.run("RETURN 1 as test").single()
                return result and result.get("test") == 1
            except Exception as e:
                logger.error(f"Error al probar la conexión: {str(e)}")
                return False
        return False
        
    def load_data(self, user_df=None, moto_df=None, ratings_df=None):
        """
        Carga datos en el recomendador, ya sea desde dataframes proporcionados
        o desde Neo4j a través del conector.
        """
        try:
            # Si se proporcionaron dataframes, usarlos directamente
            if user_df is not None and moto_df is not None:
                logger.info("Cargando datos desde DataFrames proporcionados")
                self.recommender.load_data(user_df, moto_df, ratings_df if ratings_df is not None else pd.DataFrame())
                self.data_loaded = True
                return True
                
            # Si no se proporcionaron dataframes pero hay conector a BD, obtener datos de Neo4j
            if self.db_connector is not None:
                logger.info("Obteniendo datos desde Neo4j")
                try:
                    # Obtener datos de Neo4j
                    user_data = self.db_connector.get_user_data()
                    moto_data = self.db_connector.get_moto_data()
                    ratings_data = self.db_connector.get_ratings_data()
                    
                    # Cargar datos en el recomendador
                    self.recommender.load_data(user_data, moto_data, ratings_data)
                    self.data_loaded = True
                    return True
                except Exception as e:
                    logger.error(f"Error al obtener datos desde Neo4j: {str(e)}")
                    raise
                    
            logger.error("No se proporcionaron datos ni conector a BD")
            return False
            
        except Exception as e:
            logger.error(f"Error al cargar datos: {str(e)}")
            return False
            
    def get_recommendations(self, user_id, top_n=5):
        """
        Obtiene recomendaciones para un usuario.
        
        Args:
            user_id: ID del usuario para el que se generan recomendaciones
            top_n: Número de recomendaciones a generar
            
        Returns:
            list: Lista de tuplas (moto_id, score, reasons) ordenadas por puntuación,
                 o lista vacía en caso de error
        """
        try:
            # Verificar si los datos están cargados
            if not self.data_loaded:
                loaded = self.load_data()
                if not loaded:
                    logger.error("No se pudieron cargar los datos para generar recomendaciones")
                    return []
                    
            # Generar recomendaciones
            return self.recommender.get_moto_ideal(user_id, top_n)
            
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


# Función para probar la integración con datos simulados
def test_integration():
    """
    Prueba la integración del adaptador con datos simulados.
    """
    print("\n==== PRUEBA DE INTEGRACIÓN DEL RECOMENDADOR ====\n")
    
    # Datos simulados de usuarios
    users = [
        {'user_id': 'user1', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000},
        {'user_id': 'user2', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000}
    ]
    user_df = pd.DataFrame(users)
    
    # Datos simulados de motos
    motos = [
        {'moto_id': 'moto1', 'modelo': 'Honda CB125R', 'marca': 'Honda', 'tipo': 'naked', 'potencia': 15, 'precio': 4500},
        {'moto_id': 'moto2', 'modelo': 'Yamaha MT-07', 'marca': 'Yamaha', 'tipo': 'naked', 'potencia': 73, 'precio': 8000}
    ]
    moto_df = pd.DataFrame(motos)
    
    # Datos simulados de valoraciones
    ratings = [
        {'user_id': 'user1', 'moto_id': 'moto1', 'rating': 5},
        {'user_id': 'user2', 'moto_id': 'moto2', 'rating': 4.5}
    ]
    ratings_df = pd.DataFrame(ratings)
    
    # Crear adaptador
    adapter = MotoRecommenderAdapter()
    
    # Cargar datos
    print("Cargando datos simulados...")
    adapter.load_data(user_df, moto_df, ratings_df)
    
    # Probar recomendaciones
    for user_id in user_df['user_id']:
        print(f"\nGenerando recomendaciones para {user_id}:")
        recs = adapter.get_recommendations(user_id)
        
        if recs:
            for moto_id, score, reasons in recs:
                moto = moto_df[moto_df['moto_id'] == moto_id].iloc[0]
                print(f"- {moto['modelo']} ({moto['marca']})")
                print(f"  Score: {score:.2f}")
                print(f"  Razones: {', '.join(reasons)}")
        else:
            print("No se generaron recomendaciones")
    
    print("\n==== FIN DE LA PRUEBA DE INTEGRACIÓN ====\n")


# Ejecutar la prueba si este script se ejecuta directamente
if __name__ == "__main__":
    test_integration()
