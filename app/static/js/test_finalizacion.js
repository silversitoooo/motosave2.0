/**
 * Controlador de finalización del test - Gestiona la transición final del test
 * y el envío de resultados al servidor para generar recomendaciones.
 */

// Función para finalizar el test y enviar resultados
function finalizarTest() {
  console.log("Finalizando test y capturando rangos directos del usuario...");
  
  // Asegurar que objetos globales existan
  window.testResults = window.testResults || {};
  window.respuestas = window.respuestas || { estilos: {}, marcas: {} };
  
  // CAPTURA DIRECTA DE RANGOS SIN CONVERSIÓN
  // 1. Presupuesto - usar valores exactos del slider dual
  const presupuestoMinSlider = document.getElementById('presupuesto_min');
  const presupuestoMaxSlider = document.getElementById('presupuesto_max');
  
  if (presupuestoMinSlider && presupuestoMaxSlider) {
    window.testResults.presupuesto_min = parseInt(presupuestoMinSlider.value);
    window.testResults.presupuesto_max = parseInt(presupuestoMaxSlider.value);
    console.log(`PRESUPUESTO CAPTURADO: ${window.testResults.presupuesto_min} - ${window.testResults.presupuesto_max}`);
  } else {
    // Valores por defecto solo si no hay sliders
    window.testResults.presupuesto_min = 5000;
    window.testResults.presupuesto_max = 50000;
  }
  
  // 2. Cilindrada - usar valores exactos del slider dual
  const cilindradaMinSlider = document.getElementById('cilindrada_min');
  const cilindradaMaxSlider = document.getElementById('cilindrada_max');
  
  if (cilindradaMinSlider && cilindradaMaxSlider) {
    window.testResults.cilindrada_min = parseInt(cilindradaMinSlider.value);
    window.testResults.cilindrada_max = parseInt(cilindradaMaxSlider.value);
    console.log(`CILINDRADA CAPTURADA: ${window.testResults.cilindrada_min}cc - ${window.testResults.cilindrada_max}cc`);
  } else {
    // Valores por defecto
    window.testResults.cilindrada_min = 125;
    window.testResults.cilindrada_max = 1000;
  }
  
  // 3. Potencia - usar valores exactos del slider dual
  const potenciaMinSlider = document.getElementById('potencia_min');
  const potenciaMaxSlider = document.getElementById('potencia_max');
  
  if (potenciaMinSlider && potenciaMaxSlider) {
    window.testResults.potencia_min = parseInt(potenciaMinSlider.value);
    window.testResults.potencia_max = parseInt(potenciaMaxSlider.value);
    console.log(`POTENCIA CAPTURADA: ${window.testResults.potencia_min}CV - ${window.testResults.potencia_max}CV`);
  } else {
    // Valores por defecto
    window.testResults.potencia_min = 15;
    window.testResults.potencia_max = 200;
  }
  
  // 4. Torque - usar valores exactos del slider dual (si existe)
  const torqueMinSlider = document.getElementById('torque_min');
  const torqueMaxSlider = document.getElementById('torque_max');
  
  if (torqueMinSlider && torqueMaxSlider) {
    window.testResults.torque_min = parseInt(torqueMinSlider.value);
    window.testResults.torque_max = parseInt(torqueMaxSlider.value);
    console.log(`TORQUE CAPTURADO: ${window.testResults.torque_min}Nm - ${window.testResults.torque_max}Nm`);
  } else {
    // Valores por defecto para torque
    window.testResults.torque_min = 10;
    window.testResults.torque_max = 150;
  }
  
  // 5. Peso - usar valores exactos del slider dual (si existe)
  const pesoMinSlider = document.getElementById('peso_min');
  const pesoMaxSlider = document.getElementById('peso_max');
  
  if (pesoMinSlider && pesoMaxSlider) {
    window.testResults.peso_min = parseInt(pesoMinSlider.value);
    window.testResults.peso_max = parseInt(pesoMaxSlider.value);
    console.log(`PESO CAPTURADO: ${window.testResults.peso_min}kg - ${window.testResults.peso_max}kg`);
  } else {
    // Valores por defecto para peso
    window.testResults.peso_min = 100;
    window.testResults.peso_max = 300;
  }
  
  // TRANSFERIR SELECCIONES DE BURBUJAS
  window.testResults.estilos = Object.keys(window.respuestas.estilos || {}).length > 0 ? 
                               window.respuestas.estilos : 
                               window.testResults.estilos || {};
                               
  window.testResults.marcas = Object.keys(window.respuestas.marcas || {}).length > 0 ? 
                              window.respuestas.marcas : 
                              window.testResults.marcas || {};
  
  // CAPTURAR PREFERENCIAS CUALITATIVAS
  window.testResults.experiencia = window.testResults.experiencia || 'intermedio';
  window.testResults.uso = window.testResults.uso || 'mixto';
  window.testResults.uso_previsto = window.testResults.uso_previsto || window.testResults.uso || 'mixto';
  
  // VALIDACIÓN FINAL DE RANGOS
  console.log("=== RANGOS CAPTURADOS DIRECTAMENTE DEL TEST ===");
  console.log(`Presupuesto: Q${window.testResults.presupuesto_min.toLocaleString()} - Q${window.testResults.presupuesto_max.toLocaleString()}`);
  console.log(`Cilindrada: ${window.testResults.cilindrada_min}cc - ${window.testResults.cilindrada_max}cc`);
  console.log(`Potencia: ${window.testResults.potencia_min}CV - ${window.testResults.potencia_max}CV`);
  console.log(`Torque: ${window.testResults.torque_min}Nm - ${window.testResults.torque_max}Nm`);
  console.log(`Peso: ${window.testResults.peso_min}kg - ${window.testResults.peso_max}kg`);
  console.log("=================================================");
  
  // Preparar datos para enviar al servidor - SIN CONVERSIONES
  const testData = {
    // Datos básicos del test
    experiencia: window.testResults.experiencia,
    uso: window.testResults.uso,
    uso_previsto: window.testResults.uso_previsto,
    
    // RANGOS CUANTITATIVOS DIRECTOS (sin conversión)
    presupuesto_min: window.testResults.presupuesto_min,
    presupuesto_max: window.testResults.presupuesto_max,
    cilindrada_min: window.testResults.cilindrada_min,
    cilindrada_max: window.testResults.cilindrada_max,
    potencia_min: window.testResults.potencia_min,
    potencia_max: window.testResults.potencia_max,
    torque_min: window.testResults.torque_min,
    torque_max: window.testResults.torque_max,
    peso_min: window.testResults.peso_min,
    peso_max: window.testResults.peso_max,
    
    // PREFERENCIAS CATEGÓRICAS
    estilos: window.testResults.estilos || {},
    marcas: window.testResults.marcas || {},
    
    // Control
    reset_recommendation: 'true'
  };
  
  console.log("Datos finales para enviar (sin conversiones):", JSON.stringify(testData, null, 2));
  
  // Crear formulario para enviar datos
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = "/guardar_test";
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
      console.log(`Campo: ${key} = ${input.value} (${typeof testData[key]})`);
    }
  }
  
  // Agregar formulario al documento y enviarlo
  document.body.appendChild(form);
  console.log("Enviando formulario con rangos directos del test...");
  form.submit();
}

// Exportar para uso global
window.finalizarTest = finalizarTest;

console.log("Módulo de finalización del test (con rangos directos) cargado correctamente");