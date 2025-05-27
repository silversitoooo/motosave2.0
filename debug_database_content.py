"""
Script para debuggear el contenido de la base de datos Neo4j
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Starting debug script...")

try:
    from neo4j import GraphDatabase
    print("Neo4j imported successfully")
except ImportError as e:
    print(f"Error importing Neo4j: {e}")
    sys.exit(1)

def debug_database():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "22446688"))
    
    try:
        with driver.session() as session:
            print("=== ANÁLISIS DE BASE DE DATOS ===\n")
            
            # 1. Total de motos
            result = session.run("MATCH (m:Moto) RETURN count(m) as total")
            total_motos = result.single()["total"]
            print(f"Total de motos en la base: {total_motos}")
            
            # 2. Motos con datos completos
            result = session.run("""
                MATCH (m:Moto) 
                WHERE m.precio IS NOT NULL 
                AND m.cilindrada IS NOT NULL 
                AND m.potencia IS NOT NULL 
                AND m.peso IS NOT NULL 
                AND m.torque IS NOT NULL
                RETURN count(m) as completas
            """)
            motos_completas = result.single()["completas"]
            print(f"Motos con datos técnicos completos: {motos_completas}")
            
            # 3. Motos que cumplen los criterios del último test
            criterios_test = {
                'presupuesto_min': 36900,
                'presupuesto_max': 110000,
                'cilindrada_min': 112,
                'cilindrada_max': 1100,
                'potencia_min': 9,
                'potencia_max': 165,
                'peso_min': 108,
                'peso_max': 275
            }
            
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toFloat(m.precio) >= $presupuesto_min 
                AND toFloat(m.precio) <= $presupuesto_max
                AND toFloat(m.cilindrada) >= $cilindrada_min 
                AND toFloat(m.cilindrada) <= $cilindrada_max
                AND toFloat(m.potencia) >= $potencia_min 
                AND toFloat(m.potencia) <= $potencia_max
                AND toFloat(m.peso) >= $peso_min 
                AND toFloat(m.peso) <= $peso_max
                RETURN m.marca, m.modelo, m.ano, m.precio, m.cilindrada, m.potencia, m.peso
                ORDER BY m.marca, m.modelo
            """, **criterios_test)
            
            print(f"\nMotos que cumplen criterios del test:")
            count = 0
            for record in result:
                count += 1
                print(f"{count}. {record['m.marca']} {record['m.modelo']} {record['m.ano']} - "
                      f"Precio: {record['m.precio']}, Cilindrada: {record['m.cilindrada']}, "
                      f"Potencia: {record['m.potencia']}, Peso: {record['m.peso']}")
            
            # 4. Distribución por marca
            print(f"\n=== DISTRIBUCIÓN POR MARCA ===")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE m.precio IS NOT NULL 
                RETURN m.marca as marca, count(m) as cantidad
                ORDER BY cantidad DESC
                LIMIT 15
            """)
            
            for record in result:
                print(f"{record['marca']}: {record['cantidad']} motos")
            
            # 5. Rangos de precios
            print(f"\n=== RANGOS DE DATOS ===")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE m.precio IS NOT NULL 
                RETURN 
                    min(toFloat(m.precio)) as precio_min,
                    max(toFloat(m.precio)) as precio_max,
                    avg(toFloat(m.precio)) as precio_avg
            """)
            
            record = result.single()
            print(f"Precios - Min: {record['precio_min']}, Max: {record['precio_max']}, Promedio: {record['precio_avg']:.2f}")
            
            # 6. Problema específico: buscar Yamaha naked
            print(f"\n=== BÚSQUEDA ESPECÍFICA: YAMAHA NAKED ===")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'yamaha'
                AND (toLower(m.estilo) CONTAINS 'naked' OR toLower(m.tipo) CONTAINS 'naked')
                AND m.precio IS NOT NULL
                RETURN m.marca, m.modelo, m.ano, m.precio, m.estilo
                ORDER BY m.modelo
                LIMIT 10
            """)
            
            yamaha_count = 0
            for record in result:
                yamaha_count += 1
                print(f"{yamaha_count}. {record['m.marca']} {record['m.modelo']} {record['m.ano']} - "
                      f"Precio: {record['m.precio']}, Estilo: {record['m.estilo']}")
            
            if yamaha_count == 0:
                print("¡NO SE ENCONTRARON YAMAHA NAKED!")
                
                # Buscar Yamaha sin filtro de estilo
                result = session.run("""
                    MATCH (m:Moto) 
                    WHERE toLower(m.marca) CONTAINS 'yamaha'
                    AND m.precio IS NOT NULL
                    RETURN m.marca, m.modelo, m.ano, m.precio, m.estilo
                    ORDER BY m.modelo
                    LIMIT 10
                """)
                
                print("\nYamaha disponibles (cualquier estilo):")
                for record in result:
                    print(f"- {record['m.marca']} {record['m.modelo']} {record['m.ano']} - "
                          f"Precio: {record['m.precio']}, Estilo: {record['m.estilo']}")
    
    finally:
        driver.close()

if __name__ == "__main__":
    debug_database()
