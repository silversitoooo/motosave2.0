"""
Comprehensive script to fix missing motorcycle data in Neo4j database
"""
from neo4j import GraphDatabase
import traceback

def fix_database():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "22446688"))
    
    try:
        with driver.session() as session:
            print("=== FIXING MOTORCYCLE DATABASE ===\n")
            
            # 1. Fix Yamaha MT series as naked
            print("1. Fixing Yamaha MT series as naked...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'yamaha'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'mt' OR toLower(m.nombre) CONTAINS 'mt')
                SET m.estilo = 'naked'
                RETURN count(m) as updated
            """)
            yamaha_mt_updated = result.single()['updated']
            print(f"   ✓ Updated {yamaha_mt_updated} Yamaha MT motorcycles")
            
            # 2. Fix Honda CBR as sport
            print("2. Fixing Honda CBR series as sport...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'honda'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'cbr' OR toLower(m.nombre) CONTAINS 'cbr')
                SET m.estilo = 'sport'
                RETURN count(m) as updated
            """)
            honda_cbr_updated = result.single()['updated']
            print(f"   ✓ Updated {honda_cbr_updated} Honda CBR motorcycles")
            
            # 3. Fix Kawasaki Ninja as sport
            print("3. Fixing Kawasaki Ninja series as sport...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'kawasaki'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'ninja' OR toLower(m.nombre) CONTAINS 'ninja')
                SET m.estilo = 'sport'
                RETURN count(m) as updated
            """)
            kawasaki_ninja_updated = result.single()['updated']
            print(f"   ✓ Updated {kawasaki_ninja_updated} Kawasaki Ninja motorcycles")
            
            # 4. Fix Yamaha R series as sport
            print("4. Fixing Yamaha R series as sport...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'yamaha'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'r1' OR toLower(m.modelo) CONTAINS 'r6' 
                     OR toLower(m.modelo) CONTAINS 'r3' OR toLower(m.modelo) CONTAINS 'yzf'
                     OR toLower(m.nombre) CONTAINS 'r1' OR toLower(m.nombre) CONTAINS 'r6')
                SET m.estilo = 'sport'
                RETURN count(m) as updated
            """)
            yamaha_r_updated = result.single()['updated']
            print(f"   ✓ Updated {yamaha_r_updated} Yamaha R series motorcycles")
            
            # 5. Fix KTM Duke as naked
            print("5. Fixing KTM Duke series as naked...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'ktm'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'duke' OR toLower(m.nombre) CONTAINS 'duke')
                SET m.estilo = 'naked'
                RETURN count(m) as updated
            """)
            ktm_duke_updated = result.single()['updated']
            print(f"   ✓ Updated {ktm_duke_updated} KTM Duke motorcycles")
            
            # 6. Fix KTM RC as sport (this should include your RC 8C)
            print("6. Fixing KTM RC series as sport...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'ktm'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'rc' OR toLower(m.nombre) CONTAINS 'rc')
                SET m.estilo = 'sport'
                RETURN count(m) as updated
            """)
            ktm_rc_updated = result.single()['updated']
            print(f"   ✓ Updated {ktm_rc_updated} KTM RC motorcycles")
            
            # 7. Fix Harley Davidson as cruiser
            print("7. Fixing Harley Davidson as cruiser...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'harley'
                AND (m.estilo IS NULL OR m.estilo = '')
                SET m.estilo = 'cruiser'
                RETURN count(m) as updated
            """)
            harley_updated = result.single()['updated']
            print(f"   ✓ Updated {harley_updated} Harley Davidson motorcycles")
            
            # 8. Fix scooters
            print("8. Fixing scooters...")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'scooter' OR toLower(m.nombre) CONTAINS 'scooter'
                     OR toLower(m.marca) CONTAINS 'vespa' OR toLower(m.marca) CONTAINS 'piaggio'
                     OR toLower(m.modelo) CONTAINS 'pcx' OR toLower(m.modelo) CONTAINS 'nmax'
                     OR toLower(m.modelo) CONTAINS 'xmax')
                SET m.estilo = 'scooter'
                RETURN count(m) as updated
            """)
            scooter_updated = result.single()['updated']
            print(f"   ✓ Updated {scooter_updated} scooter motorcycles")
            
            # 9. Test the fixes
            print("\n=== VERIFICATION ===")
            
            # Check Yamaha naked availability now
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'yamaha'
                AND toLower(m.estilo) = 'naked'
                AND m.precio IS NOT NULL
                RETURN count(m) as total
            """)
            yamaha_naked_count = result.single()['total']
            print(f"Yamaha naked motorcycles available: {yamaha_naked_count}")
            
            # Check total motorcycles with style data
            result = session.run("""
                MATCH (m:Moto) 
                WHERE m.estilo IS NOT NULL AND m.estilo <> ''
                RETURN count(m) as total
            """)
            total_with_style = result.single()['total']
            print(f"Total motorcycles with style data: {total_with_style}")
            
            # Test with relaxed criteria (similar to your test)
            print("\n=== TESTING RELAXED CRITERIA ===")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toFloat(m.precio) >= 5000 
                AND toFloat(m.precio) <= 50000
                AND toFloat(m.cilindrada) >= 125 
                AND toFloat(m.cilindrada) <= 1000
                AND m.estilo IS NOT NULL
                RETURN m.marca, m.modelo, m.ano, m.precio, m.estilo, m.cilindrada
                ORDER BY m.marca, m.modelo
                LIMIT 20
            """)
            
            print("Sample motorcycles with relaxed criteria:")
            count = 0
            for record in result:
                count += 1
                print(f"{count:2d}. {record['m.marca']} {record['m.modelo']} - "
                      f"Precio: {record['m.precio']}, Estilo: {record['m.estilo']}, "
                      f"Cilindrada: {record['m.cilindrada']}")
            
            print(f"\n=== SUMMARY ===")
            print(f"Total updates made:")
            print(f"- Yamaha MT (naked): {yamaha_mt_updated}")
            print(f"- Honda CBR (sport): {honda_cbr_updated}")
            print(f"- Kawasaki Ninja (sport): {kawasaki_ninja_updated}")
            print(f"- Yamaha R series (sport): {yamaha_r_updated}")
            print(f"- KTM Duke (naked): {ktm_duke_updated}")
            print(f"- KTM RC (sport): {ktm_rc_updated}")
            print(f"- Harley Davidson (cruiser): {harley_updated}")
            print(f"- Scooters: {scooter_updated}")
            print(f"Total motorcycles now with style: {total_with_style}")
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        driver.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    fix_database()
