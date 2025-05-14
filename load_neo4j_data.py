from app.algoritmo.utils import DatabaseConnector
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_test_data():
    """Carga datos de prueba en Neo4j"""
    
    # Conectar a Neo4j
    connector = DatabaseConnector(
        uri='bolt://localhost:7687',
        user='neo4j',
        password='22446688'  # Cambia esto
    )
    
    if not connector.is_connected:
        logger.error("No se pudo conectar a Neo4j")
        return False
    
    # Datos de usuarios
    users = [
        {'user_id': 'admin', 'experiencia': 'intermedio', 'uso_previsto': 'carretera', 'presupuesto': 10000, 'nombre': 'Admin'},
        {'user_id': 'test_user', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 5000, 'nombre': 'Usuario de Prueba'},
        {'user_id': 'maria', 'experiencia': 'experto', 'uso_previsto': 'offroad', 'presupuesto': 15000, 'nombre': 'María'},
        {'user_id': 'ariel1234', 'experiencia': 'principiante', 'uso_previsto': 'urbano', 'presupuesto': 8000, 'nombre': 'Ariel'}
    ]
    
    # Datos de motos
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
    
    # Datos de valoraciones
    ratings = [
        {'user_id': 'admin', 'moto_id': 'moto2', 'rating': 4.5},
        {'user_id': 'admin', 'moto_id': 'moto3', 'rating': 3.5},
        {'user_id': 'test_user', 'moto_id': 'moto1', 'rating': 4.8},
        {'user_id': 'maria', 'moto_id': 'moto3', 'rating': 4.2},
        {'user_id': 'maria', 'moto_id': 'moto6', 'rating': 4.9},
        {'user_id': 'ariel1234', 'moto_id': 'moto5', 'rating': 4.7}
    ]
    
    # Datos de amistades
    friendships = [
        {'user_id': 'admin', 'friend_id': 'maria'},
        {'user_id': 'ariel1234', 'friend_id': 'test_user'},
        {'user_id': 'maria', 'friend_id': 'test_user'}
    ]
    
    # Cargar datos a Neo4j
    try:
        # Primero limpiar datos existentes
        connector.execute_query("MATCH (n) DETACH DELETE n")
        logger.info("Base de datos limpiada correctamente")
        
        # Cargar usuarios
        for user in users:
            query = """
            CREATE (u:User {
                user_id: $user_id,
                experiencia: $experiencia,
                uso_previsto: $uso_previsto,
                presupuesto: $presupuesto,
                nombre: $nombre
            })
            """
            connector.execute_query(query, params=user)
        logger.info(f"Cargados {len(users)} usuarios")
        
        # Cargar motos
        for moto in motos:
            query = """
            CREATE (m:Moto {
                moto_id: $moto_id,
                modelo: $modelo,
                marca: $marca,
                tipo: $tipo,
                potencia: $potencia,
                cilindrada: $cilindrada,
                peso: $peso,
                precio: $precio,
                imagen: $imagen
            })
            """
            connector.execute_query(query, params=moto)
        logger.info(f"Cargadas {len(motos)} motos")
        
        # Cargar valoraciones
        for rating in ratings:
            query = """
            MATCH (u:User {user_id: $user_id})
            MATCH (m:Moto {moto_id: $moto_id})
            CREATE (u)-[r:RATED {rating: $rating}]->(m)
            """
            connector.execute_query(query, params=rating)
        logger.info(f"Cargadas {len(ratings)} valoraciones")
        
        # Cargar amistades
        for friendship in friendships:
            query = """
            MATCH (u1:User {user_id: $user_id})
            MATCH (u2:User {user_id: $friend_id})
            CREATE (u1)-[r:FRIEND_OF]->(u2)
            """
            connector.execute_query(query, params=friendship)
        logger.info(f"Cargadas {len(friendships)} amistades")
        
        return True
    except Exception as e:
        logger.error(f"Error al cargar datos: {str(e)}")
        return False
    finally:
        connector.close()

if __name__ == "__main__":
    success = load_test_data()
    if success:
        print("✅ Datos cargados correctamente en Neo4j")
    else:
        print("❌ Error al cargar datos en Neo4j")