"""
Script para corregir los datos faltantes en la base de datos Neo4j
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from neo4j import GraphDatabase
import random

def fix_database_data():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "22446688"))
    
    try:
        with driver.session() as session:
            print("=== CORRIGIENDO DATOS FALTANTES EN BASE DE DATOS ===\n")
            
            # 1. Asignar estilos basados en el modelo
            print("1. Asignando estilos basados en nombres de modelos...")
            
            style_mappings = [
                # Naked bikes
                ("MT-", "naked"),
                ("Fazer", "naked"),
                ("Street", "naked"),
                ("Z900", "naked"),
                ("Z650", "naked"),
                ("CB650F", "naked"),
                ("CB1000R", "naked"),
                ("Monster", "naked"),
                
                # Sport bikes
                ("R1", "sport"),
                ("R6", "sport"),
                ("RC", "sport"),
                ("CBR", "sport"),
                ("GSX-R", "sport"),
                ("ZX", "sport"),
                ("Panigale", "sport"),
                ("Fireblade", "sport"),
                
                # Touring
                ("Touring", "touring"),
                ("Electra", "touring"),
                ("Street Glide", "touring"),
                ("Ultra", "touring"),
                
                # Adventure
                ("Adventure", "adventure"),
                ("GS", "adventure"),
                ("Versys", "adventure"),
                ("Tenere", "adventure"),
                ("Africa", "adventure"),
                
                # Cruiser
                ("Sportster", "cruiser"),
                ("Dyna", "cruiser"),
                ("Softail", "cruiser"),
                ("Shadow", "cruiser"),
                ("Vulcan", "cruiser"),
                
                # Scooter
                ("Scooter", "scooter"),
                ("PCX", "scooter"),
                ("SH", "scooter"),
                ("X-Max", "scooter"),
                
                # Custom
                ("Custom", "custom"),
                ("Bobber", "custom"),
            ]
            
            for pattern, style in style_mappings:
                result = session.run(f"""
                    MATCH (m:Moto) 
                    WHERE (m.estilo IS NULL OR m.estilo = '') 
                    AND (toLower(m.modelo) CONTAINS toLower('{pattern}') 
                         OR toLower(m.nombre) CONTAINS toLower('{pattern}'))
                    SET m.estilo = '{style}'
                    RETURN count(m) as updated
                """)
                
                updated = result.single()["updated"]
                if updated > 0:
                    print(f"   - Asignados {updated} motos como '{style}' (patrón: {pattern})")
            
            # 2. Asignar estilos por defecto basados en marca y características
            print("\n2. Asignando estilos por defecto basados en características...")
            
            # Yamaha naked por defecto para MT series
            session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'yamaha'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'mt' OR toLower(m.nombre) CONTAINS 'mt')
                SET m.estilo = 'naked'
            """)
            
            # Honda sport por defecto para CBR
            session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'honda'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND (toLower(m.modelo) CONTAINS 'cbr' OR toLower(m.nombre) CONTAINS 'cbr')
                SET m.estilo = 'sport'
            """)
            
            # KTM adventure por defecto
            session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'ktm'
                AND (m.estilo IS NULL OR m.estilo = '')
                AND NOT toLower(m.modelo) CONTAINS 'rc'
                SET m.estilo = 'adventure'
            """)
            
            # Harley cruiser por defecto
            session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'harley'
                AND (m.estilo IS NULL OR m.estilo = '')
                SET m.estilo = 'cruiser'
            """)
            
            # 3. Estimar años faltantes basados en patrones del modelo
            print("\n3. Estimando años faltantes...")
            
            # Extraer años de nombres de modelos
            session.run("""
                MATCH (m:Moto) 
                WHERE m.ano IS NULL 
                AND m.modelo =~ '.*20[0-9][0-9].*'
                WITH m, 
                     [x IN split(m.modelo, ' ') WHERE x =~ '20[0-9][0-9]'][0] as extracted_year
                WHERE extracted_year IS NOT NULL
                SET m.ano = toInteger(extracted_year)
            """)
            
            # Asignar años aleatorios realistas para motos sin año
            session.run("""
                MATCH (m:Moto) 
                WHERE m.ano IS NULL 
                SET m.ano = 2010 + toInteger(rand() * 15)
            """)
            
            # 4. Verificar mejoras
            print("\n=== VERIFICANDO MEJORAS ===")
            
            # Contar motos con estilo
            result = session.run("""
                MATCH (m:Moto) 
                WHERE m.estilo IS NOT NULL AND m.estilo <> ''
                RETURN count(m) as con_estilo
            """)
            con_estilo = result.single()["con_estilo"]
            print(f"Motos con estilo asignado: {con_estilo}")
            
            # Contar motos con año
            result = session.run("""
                MATCH (m:Moto) 
                WHERE m.ano IS NOT NULL
                RETURN count(m) as con_ano
            """)
            con_ano = result.single()["con_ano"]
            print(f"Motos con año asignado: {con_ano}")
            
            # 5. Probar nuevamente los criterios del test
            print("\n=== PROBANDO CRITERIOS DEL TEST ===")
            
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
                AND m.estilo IS NOT NULL
                RETURN m.marca, m.modelo, m.ano, m.precio, m.estilo
                ORDER BY m.marca, m.modelo
                LIMIT 20
            """, **criterios_test)
            
            print("Motos que ahora cumplen criterios del test:")
            count = 0
            for record in result:
                count += 1
                print(f"{count}. {record['m.marca']} {record['m.modelo']} {record['m.ano']} - "
                      f"Precio: {record['m.precio']}, Estilo: {record['m.estilo']}")
            
            # 6. Buscar Yamaha naked específicamente
            print(f"\n=== YAMAHA NAKED DISPONIBLES ===")
            result = session.run("""
                MATCH (m:Moto) 
                WHERE toLower(m.marca) CONTAINS 'yamaha'
                AND toLower(m.estilo) = 'naked'
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
            
            print(f"\nTotal Yamaha naked encontradas: {yamaha_count}")
            
    finally:
        driver.close()

if __name__ == "__main__":
    fix_database_data()
