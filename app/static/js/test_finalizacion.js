/**
 * Controlador de finalización del test - Gestiona la transición final del test
 * y el envío de resultados al servidor para generar recomendaciones.
 */

// Función para finalizar el test y enviar resultados
function finalizarTest() {
  console.log("Finalizando test y preparando envío de resultados...");
  
  // Asegurar que objetos globales existan
  window.testResults = window.testResults || {};
  window.respuestas = window.respuestas || { estilos: {}, marcas: {} };
  
  // VERIFICACIÓN PROACTIVA: Comprobar si hay datos en respuestas pero no en testResults
  if (Object.keys(window.respuestas.estilos || {}).length > 0 && 
      Object.keys(window.testResults.estilos || {}).length === 0) {
    console.warn("Se detectaron selecciones en respuestas pero no en testResults. Sincronizando...");
  }
  
  // ASEGURAR QUE LAS SELECCIONES DE BURBUJAS SE TRANSFIERAN A testResults (con verificación)
  window.testResults.estilos = Object.keys(window.respuestas.estilos || {}).length > 0 ? 
                               window.respuestas.estilos : 
                               window.testResults.estilos || {};
                               
  window.testResults.marcas = Object.keys(window.respuestas.marcas || {}).length > 0 ? 
                              window.respuestas.marcas : 
                              window.testResults.marcas || {};
  
  // Guardar datos adicionales que pudieran existir en window.testResults
  window.testResults.experiencia = window.testResults.experiencia || 'intermedio';
  window.testResults.presupuesto = window.testResults.presupuesto || '10000';
  window.testResults.uso = window.testResults.uso || 'mixto';
  window.testResults.uso_previsto = window.testResults.uso_previsto || window.testResults.uso || 'mixto';
  
  // VALIDACIÓN FINAL DE DATOS
  const estilosVacios = Object.keys(window.testResults.estilos).length === 0;
  const marcasVacias = Object.keys(window.testResults.marcas).length === 0;
  
  if (estilosVacios || marcasVacias) {
    console.warn("ADVERTENCIA: Algunas selecciones de burbujas están vacías:");
    if (estilosVacios) console.warn("- Estilos vacíos");
    if (marcasVacias) console.warn("- Marcas vacías");
    
    // Generar valores predeterminados si hay secciones vacías
    if (estilosVacios) {
      if (window.testResults.uso === 'ciudad') {
        window.testResults.estilos = {'naked': 0.8, 'scooter': 0.7};
      } else if (window.testResults.uso === 'paseo') {
        window.testResults.estilos = {'touring': 0.8, 'trail': 0.7};
      } else {
        window.testResults.estilos = {'naked': 0.8, 'sport': 0.6};
      }
      console.log("Se generaron estilos predeterminados:", window.testResults.estilos);
    }
    
    if (marcasVacias) {
      window.testResults.marcas = {'honda': 0.8, 'yamaha': 0.7, 'kawasaki': 0.6};
      console.log("Se generaron marcas predeterminadas:", window.testResults.marcas);
    }
  }
  
  // LOG DE DIAGNÓSTICO INTENSIVO
  console.log("=== DIAGNÓSTICO DE FINALIZACIÓN DE TEST ===");
  console.log("window.testResults:", JSON.stringify(window.testResults, null, 2));
  console.log("window.respuestas:", JSON.stringify(window.respuestas, null, 2));
  
  // Preparar datos para enviar al servidor
  const testData = {
    // Datos básicos del test
    experiencia: window.testResults.experiencia || 'intermedio',
    presupuesto: window.testResults.presupuesto || '10000',
    uso: window.testResults.uso || 'mixto',
    uso_previsto: window.testResults.uso_previsto || window.testResults.uso || 'mixto',
    
    // IMPORTANTE: Usar testResults para estilos y marcas (que ahora incluye datos de window.respuestas)
    estilos: window.testResults.estilos || {},
    marcas: window.testResults.marcas || {},
    
    // Forzar reset de recomendación
    reset_recommendation: 'true'
  };
  
  console.log("Datos finales para enviar:", JSON.stringify(testData, null, 2));
  
  // Crear formulario para enviar datos
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = "/guardar_test";  // URL directa sin usar url_for para evitar errores
  form.style.display = 'none';
  
  // Agregar campos al formulario
  for (const key in testData) {
    if (testData.hasOwnProperty(key)) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      
      // Convertir objetos a JSON string
      if (typeof testData[key] === 'object') {
        input.value = JSON.stringify(testData[key]);
      } else {
        input.value = testData[key];
      }
      
      form.appendChild(input);
    }
  }
  
  // Agregar formulario al documento y enviarlo
  document.body.appendChild(form);
  console.log("Enviando formulario con datos del test...");
  form.submit();
}

// Exportar para uso global
window.finalizarTest = finalizarTest;

console.log("Módulo de finalización del test cargado correctamente");