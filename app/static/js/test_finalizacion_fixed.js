/**
 * Controlador de finalización del test - Gestiona la transición final del test
 * y el envío de resultados al servidor para generar recomendaciones.
 * VERSIÓN CORREGIDA: Detecta rama técnica/práctica para captura apropiada de rangos
 */

// Función para finalizar el test y enviar resultados
function finalizarTest() {
  console.log("Finalizando test y capturando rangos directos del usuario...");
  
  // Asegurar que objetos globales existan
  window.testResults = window.testResults || {};
  window.respuestas = window.respuestas || { estilos: {}, marcas: {} };
  // Verificar qué rama fue seleccionada con múltiples métodos
  let ramaSeleccionada = window.testResults.interesa_especificaciones || 'no';
  
  // Verificación adicional desde el DOM
  const selectElement = document.getElementById('interesa_especificaciones');
  if (selectElement && selectElement.value) {
    ramaSeleccionada = selectElement.value;
    console.log(`Valor desde DOM: ${ramaSeleccionada}`);
  }
  
  const esTecnica = ramaSeleccionada === 'si';
  console.log(`Rama seleccionada: ${esTecnica ? 'TÉCNICA' : 'PRÁCTICA'} (interesa_especificaciones: ${ramaSeleccionada})`);
  
  // VALIDACIÓN ADICIONAL: Verificar si las preguntas técnicas fueron realmente visitadas
  const preguntasTecnicasVisitadas = document.querySelectorAll('.rama-tecnica.active').length > 0;
  console.log(`Preguntas técnicas visibles en DOM: ${preguntasTecnicasVisitadas}`);
  
  // Agregar rama seleccionada a los resultados para debugging
  window.testResults.rama_seleccionada = esTecnica ? 'tecnica' : 'practica';
  window.testResults.interesa_especificaciones = ramaSeleccionada;
  
  // CAPTURA DIRECTA DE RANGOS SIN CONVERSIÓN
  // 1. Presupuesto - SIEMPRE DISPONIBLE
  const presupuestoMinSlider = document.getElementById('presupuesto_min');
  const presupuestoMaxSlider = document.getElementById('presupuesto_max');
  
  if (presupuestoMinSlider && presupuestoMaxSlider) {
    window.testResults.presupuesto_min = parseInt(presupuestoMinSlider.value);
    window.testResults.presupuesto_max = parseInt(presupuestoMaxSlider.value);
    console.log(`PRESUPUESTO CAPTURADO: Q${window.testResults.presupuesto_min.toLocaleString()} - Q${window.testResults.presupuesto_max.toLocaleString()}`);
  } else {
    console.warn("⚠️ Sliders de presupuesto no encontrados, usando valores por defecto");
    window.testResults.presupuesto_min = 15000;
    window.testResults.presupuesto_max = 50000;
  }
    // 2. Año - SIEMPRE DISPONIBLE
  const anoMinSlider = document.getElementById('ano_min');
  const anoMaxSlider = document.getElementById('ano_max');
  
  if (anoMinSlider && anoMaxSlider) {
    window.testResults.ano_min = parseInt(anoMinSlider.value);
    window.testResults.ano_max = parseInt(anoMaxSlider.value);
    console.log(`AÑO CAPTURADO: ${window.testResults.ano_min} - ${window.testResults.ano_max}`);
  } else {
    console.warn("⚠️ Sliders de año no encontrados, usando valores por defecto");
    window.testResults.ano_min = 2015;
    window.testResults.ano_max = 2025;
  }

  // 3. Peso - SIEMPRE DISPONIBLE (pregunta general)
  const pesoMinSlider = document.getElementById('peso_min');
  const pesoMaxSlider = document.getElementById('peso_max');
  
  if (pesoMinSlider && pesoMaxSlider) {
    window.testResults.peso_min = parseInt(pesoMinSlider.value);
    window.testResults.peso_max = parseInt(pesoMaxSlider.value);
    console.log(`PESO CAPTURADO: ${window.testResults.peso_min}kg - ${window.testResults.peso_max}kg`);
  } else {
    console.warn("⚠️ Sliders de peso no encontrados, usando valores por defecto");
    window.testResults.peso_min = 120;
    window.testResults.peso_max = 200;  }
    // 4-6. Rangos técnicos - SOLO capturar si realmente se eligió rama técnica Y las preguntas son visibles
  if (esTecnica && preguntasTecnicasVisitadas) {
    console.log("📊 Capturando rangos técnicos (rama técnica seleccionada y preguntas visibles)...");
    
    // 4. Cilindrada - SOLO en rama técnica
    const cilindradaMinSlider = document.getElementById('cilindrada_min');
    const cilindradaMaxSlider = document.getElementById('cilindrada_max');
    
    // Verificar que los elementos existan Y estén en una pregunta visible
    const cilindradaPregunta = cilindradaMinSlider?.closest('.pregunta');
    const cilindradaVisible = cilindradaPregunta && cilindradaPregunta.classList.contains('active');
    
    if (cilindradaMinSlider && cilindradaMaxSlider && cilindradaVisible) {
      window.testResults.cilindrada_min = parseInt(cilindradaMinSlider.value);
      window.testResults.cilindrada_max = parseInt(cilindradaMaxSlider.value);
      console.log(`CILINDRADA CAPTURADA: ${window.testResults.cilindrada_min}cc - ${window.testResults.cilindrada_max}cc`);
    } else {
      console.warn("⚠️ Sliders de cilindrada no encontrados o no visibles en rama técnica");
      window.testResults.cilindrada_min = 125;
      window.testResults.cilindrada_max = 600;
    }
    
    // 5. Potencia - SOLO en rama técnica
    const potenciaMinSlider = document.getElementById('potencia_min');
    const potenciaMaxSlider = document.getElementById('potencia_max');
    
    const potenciaPregunta = potenciaMinSlider?.closest('.pregunta');
    const potenciaVisible = potenciaPregunta && potenciaPregunta.classList.contains('active');
    
    if (potenciaMinSlider && potenciaMaxSlider && potenciaVisible) {
      window.testResults.potencia_min = parseInt(potenciaMinSlider.value);
      window.testResults.potencia_max = parseInt(potenciaMaxSlider.value);
      console.log(`POTENCIA CAPTURADA: ${window.testResults.potencia_min}CV - ${window.testResults.potencia_max}CV`);
    } else {
      console.warn("⚠️ Sliders de potencia no encontrados o no visibles en rama técnica");
      window.testResults.potencia_min = 15;
      window.testResults.potencia_max = 100;
    }
    
    // 6. Torque - SOLO en rama técnica
    const torqueMinSlider = document.getElementById('torque_min');
    const torqueMaxSlider = document.getElementById('torque_max');
    
    const torquePregunta = torqueMinSlider?.closest('.pregunta');
    const torqueVisible = torquePregunta && torquePregunta.classList.contains('active');
    
    if (torqueMinSlider && torqueMaxSlider && torqueVisible) {
      window.testResults.torque_min = parseInt(torqueMinSlider.value);
      window.testResults.torque_max = parseInt(torqueMaxSlider.value);
      console.log(`TORQUE CAPTURADO: ${window.testResults.torque_min}Nm - ${window.testResults.torque_max}Nm`);
    } else {
      console.warn("⚠️ Sliders de torque no encontrados o no visibles en rama técnica");
      window.testResults.torque_min = 10;
      window.testResults.torque_max = 80;
    }
  } else {
    console.log("🎯 Usando valores por defecto para rangos técnicos (rama práctica seleccionada)");
    // Valores por defecto amplios para rama práctica
    window.testResults.cilindrada_min = 125;
    window.testResults.cilindrada_max = 1000;
    window.testResults.potencia_min = 10;
    window.testResults.potencia_max = 150;
    window.testResults.torque_min = 8;
    window.testResults.torque_max = 120;
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
  console.log(`Rama: ${esTecnica ? 'TÉCNICA (con sliders)' : 'PRÁCTICA (valores por defecto)'}`);
  console.log(`Presupuesto: Q${window.testResults.presupuesto_min.toLocaleString()} - Q${window.testResults.presupuesto_max.toLocaleString()}`);
  console.log(`Año: ${window.testResults.ano_min} - ${window.testResults.ano_max}`);
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
    ano_min: window.testResults.ano_min,
    ano_max: window.testResults.ano_max,
    cilindrada_min: window.testResults.cilindrada_min,
    cilindrada_max: window.testResults.cilindrada_max,
    potencia_min: window.testResults.potencia_min,
    potencia_max: window.testResults.potencia_max,
    torque_min: window.testResults.torque_min,
    torque_max: window.testResults.torque_max,
    peso_min: window.testResults.peso_min,
    peso_max: window.testResults.peso_max,
    
    // Indicador de qué rama fue seleccionada
    interesa_especificaciones: ramaSeleccionada,
    rama_seleccionada: esTecnica ? 'tecnica' : 'practica',
    
    // PREFERENCIAS CATEGÓRICAS
    estilos: window.testResults.estilos || {},
    marcas: window.testResults.marcas || {},
    
    // Control
    reset_recommendation: 'true'
  };
  
  console.log(`Datos finales para enviar (rama ${esTecnica ? 'técnica' : 'práctica'}):`, JSON.stringify(testData, null, 2));
  
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
  console.log("Enviando formulario con detección de rama técnica/práctica...");
  form.submit();
}

// Exportar para uso global
window.finalizarTest = finalizarTest;

console.log("Módulo de finalización del test CORREGIDO (con detección de rama) cargado correctamente");
