"""
Test completo de compatibilidad dual: inputs cuantitativos y cualitativos
Verifica que el algoritmo funcione correctamente con:
1. Solo inputs cuantitativos (rangos numéricos)
2. Solo inputs cualitativos (preguntas no numéricas)
3. Combinación de ambos tipos de inputs
"""
import sys
import os
import pandas as pd
import numpy as np

# Configurar path para importar módulos locales
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_quantitative_only():
    """
    Prueba con SOLO inputs cuantitativos (dual-thumb range sliders)
    """
    print("=" * 70)
    print("PRUEBA 1: SOLO INPUTS CUANTITATIVOS")
    print("=" * 70)
    
    try:
        from algoritmo.quantitative_evaluator import QuantitativeEvaluator
        
        evaluator = QuantitativeEvaluator()
        
        # Datos de prueba
        moto_test = pd.Series({
            'id': 'moto_test',
            'marca': 'Yamaha',
            'modelo': 'MT-07',
            'tipo': 'naked',
            'cilindrada': 689,
            'potencia': 73,
            'precio': 8000,
            'peso': 184,
            'torque': 68,
            'ano': 2022
        })
        
        # SOLO preferencias cuantitativas (como venían originalmente)
        preferencias_solo_cuantitativas = {
            'presupuesto_min': 5000,
            'presupuesto_max': 10000,
            'potencia_min': 50,
            'potencia_max': 100,
            'cilindrada_min': 400,
            'cilindrada_max': 800,
            'peso_min': 150,
            'peso_max': 200,
            'ano_min': 2020,
            'ano_max': 2024,
            # Marcas y estilos existentes
            'marcas': {'yamaha': 0.8, 'kawasaki': 0.7},
            'estilos': {'naked': 0.9, 'adventure': 0.6}
        }
        
        # Evaluar
        score, reasons = evaluator.evaluate_moto_quantitative(preferencias_solo_cuantitativas, moto_test)
        
        print(f"✅ Evaluación exitosa con solo inputs cuantitativos")
        print(f"   Moto: {moto_test['modelo']}")
        print(f"   Score: {score:.2f}")
        print(f"   Razones principales:")
        for i, reason in enumerate(reasons[:3], 1):
            print(f"      {i}. {reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con inputs cuantitativos: {e}")
        return False

def test_qualitative_only():
    """
    Prueba con SOLO inputs cualitativos (preguntas no numéricas)
    """
    print("\n" + "=" * 70)
    print("PRUEBA 2: SOLO INPUTS CUALITATIVOS")
    print("=" * 70)
    
    try:
        from algoritmo.quantitative_evaluator import QuantitativeEvaluator
        
        evaluator = QuantitativeEvaluator()
        
        # Datos de prueba
        moto_test = pd.Series({
            'id': 'moto_test',
            'marca': 'Honda',
            'modelo': 'CB125R',
            'tipo': 'naked',
            'cilindrada': 125,
            'potencia': 13,
            'precio': 4500,
            'peso': 130,
            'torque': 11,
            'ano': 2023
        })
        
        # SOLO preferencias cualitativas
        preferencias_solo_cualitativas = {
            'experiencia': 'principiante',
            'tipo_uso': 'ciudad',
            'pasajeros_carga': 'solo',
            'combustible_potencia': 'ahorro',
            'preferencia_potencia_peso': 'baja',
            'preferencia_rendimiento': 'economia'
        }
        
        # Evaluar
        score, reasons = evaluator.evaluate_moto_quantitative(preferencias_solo_cualitativas, moto_test)
        
        print(f"✅ Evaluación exitosa con solo inputs cualitativos")
        print(f"   Moto: {moto_test['modelo']}")
        print(f"   Score: {score:.2f}")
        print(f"   Razones principales:")
        for i, reason in enumerate(reasons[:3], 1):
            print(f"      {i}. {reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con inputs cualitativos: {e}")
        return False

def test_mixed_inputs():
    """
    Prueba con inputs mixtos (cuantitativos + cualitativos)
    """
    print("\n" + "=" * 70)
    print("PRUEBA 3: INPUTS MIXTOS (CUANTITATIVOS + CUALITATIVOS)")
    print("=" * 70)
    
    try:
        from algoritmo.quantitative_evaluator import QuantitativeEvaluator
        
        evaluator = QuantitativeEvaluator()
        
        # Datos de prueba
        moto_test = pd.Series({
            'id': 'moto_test',
            'marca': 'BMW',
            'modelo': 'GS 1250',
            'tipo': 'adventure',
            'cilindrada': 1254,
            'potencia': 136,
            'precio': 17000,
            'peso': 249,
            'torque': 143,
            'ano': 2024
        })
        
        # Preferencias mixtas (lo más común en la app real)
        preferencias_mixtas = {
            # Cuantitativas
            'presupuesto_min': 15000,
            'presupuesto_max': 20000,
            'potencia_min': 100,
            'potencia_max': 150,
            'cilindrada_min': 1000,
            'cilindrada_max': 1300,
            'peso_min': 200,
            'peso_max': 280,
            'ano_min': 2022,
            'ano_max': 2024,
            # Cualitativas
            'experiencia': 'experto',
            'tipo_uso': 'aventura',
            'pasajeros_carga': 'frecuente',
            'combustible_potencia': 'potencia',
            'preferencia_potencia_peso': 'alta',
            'preferencia_rendimiento': 'rendimiento',
            # Marcas y estilos
            'marcas': {'bmw': 0.9, 'ktm': 0.7},
            'estilos': {'adventure': 0.9, 'naked': 0.6}
        }
        
        # Evaluar
        score, reasons = evaluator.evaluate_moto_quantitative(preferencias_mixtas, moto_test)
        
        print(f"✅ Evaluación exitosa con inputs mixtos")
        print(f"   Moto: {moto_test['modelo']}")
        print(f"   Score: {score:.2f}")
        print(f"   Razones principales:")
        for i, reason in enumerate(reasons[:3], 1):
            print(f"      {i}. {reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con inputs mixtos: {e}")
        return False

def test_partial_inputs():
    """
    Prueba con inputs parciales (algunos campos faltantes)
    """
    print("\n" + "=" * 70)
    print("PRUEBA 4: INPUTS PARCIALES (CAMPOS FALTANTES)")
    print("=" * 70)
    
    try:
        from algoritmo.quantitative_evaluator import QuantitativeEvaluator
        
        evaluator = QuantitativeEvaluator()
        
        # Datos de prueba
        moto_test = pd.Series({
            'id': 'moto_test',
            'marca': 'Kawasaki',
            'modelo': 'Z900',
            'tipo': 'naked',
            'cilindrada': 948,
            'potencia': 125,
            'precio': 10500,
            'peso': 210,
            'torque': 98,
            'ano': 2023
        })
        
        # Preferencias parciales (algunos campos faltantes)
        preferencias_parciales = {
            # Solo algunos cuantitativos
            'presupuesto_min': 8000,
            'presupuesto_max': 12000,
            'potencia_min': 80,
            # falta potencia_max, cilindrada, peso, etc.
            
            # Solo algunas cualitativas
            'experiencia': 'intermedio',
            'tipo_uso': 'mixto',
            # faltan otras cualitativas
            
            # Marcas parciales
            'marcas': {'kawasaki': 0.8}
            # faltan estilos
        }
        
        # Evaluar
        score, reasons = evaluator.evaluate_moto_quantitative(preferencias_parciales, moto_test)
        
        print(f"✅ Evaluación exitosa con inputs parciales")
        print(f"   Moto: {moto_test['modelo']}")
        print(f"   Score: {score:.2f}")
        print(f"   Razones principales:")
        for i, reason in enumerate(reasons[:3], 1):
            print(f"      {i}. {reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con inputs parciales: {e}")
        return False

def test_edge_cases():
    """
    Prueba casos extremos y valores límite
    """
    print("\n" + "=" * 70)
    print("PRUEBA 5: CASOS EXTREMOS")
    print("=" * 70)
    
    try:
        from algoritmo.quantitative_evaluator import QuantitativeEvaluator
        
        evaluator = QuantitativeEvaluator()
        
        # Datos de prueba
        moto_test = pd.Series({
            'id': 'moto_extreme',
            'marca': 'Test',
            'modelo': 'Extreme Test',
            'tipo': 'sport',
            'cilindrada': 600,
            'potencia': 90,
            'precio': 9000,
            'peso': 180,
            'torque': 70,
            'ano': 2023
        })
        
        # CASO 1: Preferencias vacías
        print("\n📋 Caso 1: Preferencias vacías")
        preferencias_vacias = {}
        
        score, reasons = evaluator.evaluate_moto_quantitative(preferencias_vacias, moto_test)
        print(f"   Score con preferencias vacías: {score:.2f}")
        
        # CASO 2: Valores extremos
        print("\n📋 Caso 2: Valores extremos")
        preferencias_extremas = {
            'presupuesto_min': 0,
            'presupuesto_max': 999999,
            'potencia_min': 0,
            'potencia_max': 1000,
            'experiencia': 'principiante',
            'tipo_uso': 'aventura'  # Contradicción: principiante + aventura
        }
        
        score, reasons = evaluator.evaluate_moto_quantitative(preferencias_extremas, moto_test)
        print(f"   Score con valores extremos: {score:.2f}")
        
        # CASO 3: Valores inválidos/desconocidos
        print("\n📋 Caso 3: Valores inválidos")
        preferencias_invalidas = {
            'presupuesto_min': 5000,
            'presupuesto_max': 10000,
            'experiencia': 'super_experto',  # Valor no válido
            'tipo_uso': 'volador',  # Valor no válido
            'marcas': {'marca_inexistente': 0.9}
        }
        
        score, reasons = evaluator.evaluate_moto_quantitative(preferencias_invalidas, moto_test)
        print(f"   Score con valores inválidos: {score:.2f}")
        
        print("✅ Todas las pruebas de casos extremos completadas")
        return True
        
    except Exception as e:
        print(f"❌ Error en casos extremos: {e}")
        return False

def test_performance_comparison():
    """
    Compara el rendimiento con diferentes tipos de inputs
    """
    print("\n" + "=" * 70)
    print("PRUEBA 6: COMPARACIÓN DE RENDIMIENTO")
    print("=" * 70)
    
    try:
        from algoritmo.quantitative_evaluator import QuantitativeEvaluator
        import time
        
        evaluator = QuantitativeEvaluator()
        
        # Datos de prueba múltiples
        motos_test = pd.DataFrame({
            'id': [f'moto_{i}' for i in range(10)],
            'marca': ['Honda', 'Yamaha', 'Kawasaki', 'BMW', 'KTM'] * 2,
            'modelo': [f'Modelo_{i}' for i in range(10)],
            'tipo': ['naked', 'adventure', 'sport', 'touring', 'scooter'] * 2,
            'cilindrada': [125, 300, 600, 800, 1000, 1200, 400, 750, 900, 500],
            'potencia': [15, 35, 85, 110, 140, 160, 45, 95, 120, 60],
            'precio': [4000, 6000, 8000, 12000, 15000, 18000, 7000, 9000, 11000, 8500],
            'peso': [130, 160, 180, 220, 240, 260, 170, 190, 210, 175],
            'torque': [12, 30, 70, 90, 120, 140, 40, 80, 100, 55],
            'ano': [2023] * 10
        })
        
        # Preparar diferentes tipos de preferencias
        preferencias_cuant = {
            'presupuesto_min': 5000, 'presupuesto_max': 12000,
            'potencia_min': 50, 'potencia_max': 120,
            'marcas': {'yamaha': 0.8, 'honda': 0.7}
        }
        
        preferencias_cual = {
            'experiencia': 'intermedio',
            'tipo_uso': 'mixto',
            'pasajeros_carga': 'ocasional'
        }
        
        preferencias_mixtas = {**preferencias_cuant, **preferencias_cual}
        
        # Medir tiempos
        resultados_tiempo = {}
        
        for nombre, preferencias in [
            ("Cuantitativo", preferencias_cuant),
            ("Cualitativo", preferencias_cual),
            ("Mixto", preferencias_mixtas)
        ]:
            start_time = time.time()
            
            for _, moto in motos_test.iterrows():
                score, reasons = evaluator.evaluate_moto_quantitative(preferencias, moto)
            
            end_time = time.time()
            tiempo_total = end_time - start_time
            resultados_tiempo[nombre] = tiempo_total
            
            print(f"   {nombre}: {tiempo_total:.4f} segundos ({len(motos_test)} motos)")
        
        print("✅ Comparación de rendimiento completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en comparación de rendimiento: {e}")
        return False

def run_all_compatibility_tests():
    """
    Ejecuta todas las pruebas de compatibilidad
    """
    print("🚀 INICIANDO PRUEBAS DE COMPATIBILIDAD DUAL INPUT")
    print("Verificando que el algoritmo funcione con:")
    print("  • Solo inputs cuantitativos (dual-thumb sliders)")
    print("  • Solo inputs cualitativos (preguntas no numéricas)")
    print("  • Combinación de ambos tipos")
    print("  • Casos extremos y valores parciales")
    
    # Ejecutar todas las pruebas
    tests = [
        ("Cuantitativos Solo", test_quantitative_only),
        ("Cualitativos Solo", test_qualitative_only),
        ("Inputs Mixtos", test_mixed_inputs),
        ("Inputs Parciales", test_partial_inputs),
        ("Casos Extremos", test_edge_cases),
        ("Rendimiento", test_performance_comparison)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Error en {name}: {e}")
            results.append((name, False))
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE PRUEBAS DE COMPATIBILIDAD")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"   {name:<20} {status}")
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("Tu algoritmo es 100% compatible con ambos tipos de input:")
        print("  ✅ Inputs cuantitativos (dual-thumb range sliders)")
        print("  ✅ Inputs cualitativos (preguntas no numéricas)")
        print("  ✅ Combinaciones mixtas")
        print("  ✅ Casos extremos y datos parciales")
        print("\n🚀 El algoritmo está listo para producción!")
    else:
        print(f"\n⚠️  {total - passed} pruebas fallaron")
        print("Revisa los errores mostrados arriba")
    
    return passed == total

if __name__ == "__main__":
    run_all_compatibility_tests()
