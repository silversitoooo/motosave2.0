"""
Script simple para corregir datos faltantes en Neo4j
"""
from neo4j import GraphDatabase

def simple_fix():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "22446688"))
    
    with driver.session() as session:
        print("Fixing motorcycle styles...")
        
        # Fix Yamaha MT series as naked
        result = session.run("""
            MATCH (m:Moto) 
            WHERE toLower(m.marca) CONTAINS 'yamaha'
            AND (m.estilo IS NULL OR m.estilo = '')
            AND (toLower(m.modelo) CONTAINS 'mt' OR toLower(m.nombre) CONTAINS 'mt')
            SET m.estilo = 'naked'
            RETURN count(m) as updated
        """)
        print(f"Updated {result.single()['updated']} Yamaha MT as naked")
        
        # Fix Honda CBR as sport
        result = session.run("""
            MATCH (m:Moto) 
            WHERE toLower(m.marca) CONTAINS 'honda'
            AND (m.estilo IS NULL OR m.estilo = '')
            AND (toLower(m.modelo) CONTAINS 'cbr' OR toLower(m.nombre) CONTAINS 'cbr')
            SET m.estilo = 'sport'
            RETURN count(m) as updated
        """)
        print(f"Updated {result.single()['updated']} Honda CBR as sport")
        
        # Test Yamaha naked availability
        result = session.run("""
            MATCH (m:Moto) 
            WHERE toLower(m.marca) CONTAINS 'yamaha'
            AND toLower(m.estilo) = 'naked'
            AND m.precio IS NOT NULL
            RETURN count(m) as total
        """)
        print(f"Yamaha naked available: {result.single()['total']}")
        
    driver.close()
    print("Done!")

if __name__ == "__main__":
    simple_fix()
