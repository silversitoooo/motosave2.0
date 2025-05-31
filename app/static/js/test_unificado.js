/**
 * MotoSave Test Unificado
 * 
 * Este archivo combina todas las funcionalidades de:
 * - test.js: Lógica principal del test
 * - test_reorganizer.js: Reorganización de preguntas 
 * - test_debug.js: Datos de prueba para debugging
 * - test_finalizacion_fixed.js: Gestión de finalización de test
 * 
 * Eliminando código repetitivo y reorganizando para un mejor mantenimiento.
 */

// ==============================================
// INICIALIZACIÓN GLOBAL
// ==============================================
console.log('🏍️ Inicializando Test Unificado de Preferencias de Motos...');

// Estado y variables globales
window.respuestas = {
  estilos: {},
  marcas: {}
};

window.testResults = {};

// Estado general del test
const testState = {
  currentStageIndex: 0,
  stageContainers: [],
  stageIndicators: [],
  testResults: {},
  completionCallback: null
};

// Etapas configurables del test
const testStages = [
  {
    id: 'pregunta-1',
    key: 'estilos',
    title: 'Estilos de Moto',
    description: 'Selecciona los estilos de moto que más te interesan',
    type: 'selector'
  },
  {
    id: 'pregunta-2',
    key: 'marcas',
    title: 'Marcas Preferidas', 
    description: 'Selecciona tus marcas favoritas o las que más te interesan',
    type: 'selector'
  },
  {
    id: 'pregunta-3',
    key: 'experiencia',
    title: 'Experiencia de Manejo',
    description: 'Cuéntanos sobre tu nivel de experiencia con las motos',
    type: 'select'
  }
];

// Opciones para cada pregunta
const testOptions = {
  experiencia: [
    { id: 'principiante', label: 'Principiante', icon: 'fas fa-seedling' },
    { id: 'intermedio', label: 'Intermedio', icon: 'fas fa-user' },
    { id: 'experto', label: 'Experto', icon: 'fas fa-star' }
  ],
  presupuesto: [
    { id: '3000', label: 'Hasta 3.000€', icon: 'fas fa-euro-sign' },
    { id: '5000', label: 'Hasta 5.000€', icon: 'fas fa-euro-sign' },
    { id: '8000', label: 'Hasta 8.000€', icon: 'fas fa-euro-sign' },
    { id: '12000', label: 'Hasta 12.000€', icon: 'fas fa-euro-sign' },
    { id: '18000', label: 'Hasta 18.000€', icon: 'fas fa-euro-sign' },
    { id: '25000', label: 'Más de 18.000€', icon: 'fas fa-euro-sign' }
  ],
  uso_principal: [
    { id: 'ciudad', label: 'Ciudad/Commuting', icon: 'fas fa-building' },
    { id: 'paseo', label: 'Paseo/Ocio', icon: 'fas fa-route' },
    { id: 'mixto', label: 'Uso Mixto', icon: 'fas fa-random' }
  ]
};

// ==============================================
// FUNCIONES DE REORGANIZACIÓN DE PREGUNTAS
// ==============================================

/**
 * Reorganiza las preguntas del test según la rama seleccionada
 * (Técnica o práctica)
 */
function reorganizeTestQuestions() {
  console.log('🔄 Reorganizando preguntas del test...');
  
  // Determinar qué rama ha seleccionado el usuario
  const interesaTecnica = document.getElementById('interesa_especificaciones');
  if (!interesaTecnica) {
    console.warn('⚠️ No se encontró el selector de rama técnica/práctica');
    return;
  }
  
  const ramaSeleccionada = interesaTecnica.value;
  const esTecnica = ramaSeleccionada === 'si';
  
  console.log(`Rama seleccionada: ${esTecnica ? 'TÉCNICA' : 'PRÁCTICA'}`);
  
  // Ocultar todas las preguntas de ramas primero
  hideAllBranchQuestions();
  
  // Mostrar las preguntas de la rama correspondiente
  const selectores = esTecnica ? '.rama-tecnica' : '.rama-practica';
  document.querySelectorAll(selectores).forEach(pregunta => {
    pregunta.classList.add('active');
    console.log(`Activada pregunta: ${pregunta.id || 'sin ID'}`);
  });
  
  // Actualizar el estado global del test
  window.testResults.interesa_especificaciones = ramaSeleccionada;
  window.testResults.rama_seleccionada = esTecnica ? 'tecnica' : 'practica';
  
  console.log('✅ Preguntas reorganizadas correctamente según la rama seleccionada');
}

/**
 * Oculta todas las preguntas específicas de rama
 */
function hideAllBranchQuestions() {
  console.log('Ocultando todas las preguntas de rama...');
  
  // Ocultar todas las preguntas de rama técnica y práctica
  document.querySelectorAll('.rama-tecnica, .rama-practica').forEach(pregunta => {
    pregunta.classList.remove('active');
  });
  
  console.log('Todas las preguntas de ramas han sido ocultadas');
}

// ==============================================
// FUNCIONES DE MANEJO DEL TEST
// ==============================================

/**
 * Inicializa el test cargando los contenedores y configurando los eventos
 */
function initializeTest() {
  console.log('🚀 Inicializando test...');
  
  const existingStages = document.querySelectorAll('.pregunta');
  
  // Recolectar contenedores y configurar indicadores
  if (existingStages.length > 0) {
    // Usar los contenedores existentes en el HTML
    testState.stageContainers = Array.from(existingStages);
    
    // Configurar indicadores (si existen)
    testState.stageIndicators = Array.from(document.querySelectorAll('.stage-indicator'));
    
    // Configurar botones de navegación
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    if (prevBtn) {
      prevBtn.addEventListener('click', navigateToPreviousStage);
    }
    
    if (nextBtn) {
      nextBtn.addEventListener('click', navigateToNextStage);
    }
    
    // Configurar listeners para selects
    setupSelectListeners();
    
    // Inicializar los selectores de burbujas
    inicializarSoloEstilos();
    inicializarSoloMarcas();
    
    // Ocultar preguntas de rama al inicio
    hideAllBranchQuestions();
    
    // Mostrar la primera pregunta
    updateVisibleStage();
    
    console.log('✅ Test inicializado correctamente');
  } else {
    console.warn('⚠️ No se encontraron contenedores para las preguntas del test');
  }
}

/**
 * Configura los escuchadores para los elementos select
 */
function setupSelectListeners() {
  const selects = document.querySelectorAll('select[data-test-key]');
  
  selects.forEach(select => {
    const key = select.getAttribute('data-test-key');
    
    select.addEventListener('change', (event) => {
      window.testResults[key] = event.target.value;
      console.log(`💾 Guardada respuesta para ${key}: ${event.target.value}`);
      
      // Caso especial: si es el selector de especificaciones técnicas
      if (key === 'interesa_especificaciones') {
        reorganizeTestQuestions();
      }
    });
    
    // Inicializar con el valor actual si ya está seleccionado
    if (select.value) {
      window.testResults[key] = select.value;
    }
  });
}

/**
 * Navega a la etapa anterior
 */
function navigateToPreviousStage() {
  if (testState.currentStageIndex > 0) {
    testState.currentStageIndex--;
    updateVisibleStage();
  }
}

/**
 * Navega a la siguiente etapa
 */
function navigateToNextStage() {
  if (testState.currentStageIndex < testState.stageContainers.length - 1) {
    testState.currentStageIndex++;
    updateVisibleStage();
  } else {
    // Estamos en la última etapa, mostrar modal de finalización
    showCompletionModal();
  }
}

/**
 * Actualiza la etapa visible
 */
function updateVisibleStage() {
  // Ocultar todas las etapas
  testState.stageContainers.forEach(container => {
    container.classList.remove('active');
  });
  
  // Mostrar la etapa actual
  if (testState.stageContainers[testState.currentStageIndex]) {
    testState.stageContainers[testState.currentStageIndex].classList.add('active');
  }
  
  // Actualizar indicadores
  updateStageIndicators();
  
  // Actualizar botones
  updateNavigationButtons();
}

/**
 * Actualiza los indicadores de etapa
 */
function updateStageIndicators() {
  testState.stageIndicators.forEach((indicator, index) => {
    if (index < testState.currentStageIndex) {
      indicator.classList.add('completed');
      indicator.classList.remove('active');
    } else if (index === testState.currentStageIndex) {
      indicator.classList.add('active');
      indicator.classList.remove('completed');
    } else {
      indicator.classList.remove('active', 'completed');
    }
  });
}

/**
 * Actualiza los botones de navegación
 */
function updateNavigationButtons() {
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  
  if (prevBtn) {
    prevBtn.disabled = testState.currentStageIndex === 0;
  }
  
  if (nextBtn) {
    const isLastStage = testState.currentStageIndex === testState.stageContainers.length - 1;
    nextBtn.textContent = isLastStage ? 'Finalizar' : 'Siguiente';
  }
}

/**
 * Muestra el modal de finalización del test
 */
function showCompletionModal() {
  // Preparar los resultados antes de mostrar modal
  prepareTestResults();
  
  // Mostrar modal
  const modal = document.getElementById('completion-modal');
  if (!modal) {
    console.warn('⚠️ No se encontró el modal de finalización');
    return;
  }
  
  // Asegurar que el botón del modal llame a la función correcta
  const finishButton = modal.querySelector('button');
  if (finishButton) {
    // Limpiar listeners existentes
    const newButton = finishButton.cloneNode(true);
    finishButton.parentNode.replaceChild(newButton, finishButton);
    
    // Añadir nuevo listener
    newButton.addEventListener('click', () => {
      finalizarTest();
    });
  }
  
  // Mostrar modal
  modal.style.display = 'flex';
}

/**
 * Prepara los resultados del test
 */
function prepareTestResults() {
  // Asegurar que el objeto de resultados existe
  window.testResults = window.testResults || {};
  
  // Transferir selecciones de burbujas si existen
  if (window.respuestas) {
    window.testResults.estilos = window.respuestas.estilos || {};
    window.testResults.marcas = window.respuestas.marcas || {};
  }
  
  console.log('📋 Resultados del test preparados:', window.testResults);
}

// ==============================================
// FUNCIONES DE MANIPULACIÓN DE BURBUJAS
// ==============================================

/**
 * Configura los selectores de burbujas
 */
function setupBubblesSelector(key, container) {
  if (!container) {
    console.warn(`⚠️ No se encontró el contenedor para ${key}`);
    return;
  }
  
  console.log(`🔘 Configurando selector de burbujas para ${key}...`);
  
  // La implementación específica de las burbujas depende de tu UI
  // Esta es una versión simplificada
  
  const bubbles = container.querySelectorAll('.bubble-item');
  bubbles.forEach(bubble => {
    const itemId = bubble.getAttribute('data-id');
    const itemLabel = bubble.getAttribute('data-label');
    
    // Restaurar estado si ya estaba seleccionado
    if (window.respuestas[key] && window.respuestas[key][itemId]) {
      bubble.classList.add('selected');
    }
    
    bubble.addEventListener('click', () => {
      bubble.classList.toggle('selected');
      
      // Actualizar respuestas
      if (bubble.classList.contains('selected')) {
        window.respuestas[key][itemId] = itemLabel || itemId;
      } else {
        delete window.respuestas[key][itemId];
      }
      
      console.log(`💾 Actualizada selección de ${key}: ${itemId} - ${bubble.classList.contains('selected') ? 'seleccionado' : 'deseleccionado'}`);
    });
  });
}

/**
 * Inicializa solo el selector de estilos
 */
function inicializarSoloEstilos() {
  setupBubblesSelector('estilos', document.getElementById('estilos-canvas'));
}

/**
 * Inicializa solo el selector de marcas
 */
function inicializarSoloMarcas() {
  setupBubblesSelector('marcas', document.getElementById('marcas-canvas'));
}

/**
 * Verifica y restaura el estado de los canvases
 */
function verificarYRestaurarCanvas(origen) {
  const estilosCanvas = document.getElementById('estilos-canvas');
  const marcasCanvas = document.getElementById('marcas-canvas');
  
  if (estilosCanvas) {
    setupBubblesSelector('estilos', estilosCanvas);
  }
  
  if (marcasCanvas) {
    setupBubblesSelector('marcas', marcasCanvas);
  }
  
  console.log(`🔄 Canvas restaurados desde: ${origen}`);
}

// ==============================================
// FUNCIÓN DE FINALIZACIÓN DEL TEST
// ==============================================

/**
 * Finaliza el test y envía los resultados al servidor
 */
function finalizarTest() {
  console.log("✅ Finalizando test y capturando rangos directos del usuario...");
  
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
  
  // Verificar si las preguntas técnicas fueron realmente visitadas
  const preguntasTecnicasVisitadas = document.querySelectorAll('.rama-tecnica.active').length > 0;
  console.log(`Preguntas técnicas visibles en DOM: ${preguntasTecnicasVisitadas}`);
  
  // Agregar rama seleccionada a los resultados para debugging
  window.testResults.rama_seleccionada = esTecnica ? 'tecnica' : 'practica';
  window.testResults.interesa_especificaciones = ramaSeleccionada;
  
  // CAPTURA DIRECTA DE RANGOS SIN CONVERSIÓN
  // 1. Presupuesto - SIEMPRE DISPONIBLE
  captureRangeValues('presupuesto', 15000, 50000);
  
  // 2. Año - SIEMPRE DISPONIBLE
  captureRangeValues('ano', 2015, 2025);
  
  // 3. Peso - SIEMPRE DISPONIBLE
  captureRangeValues('peso', 120, 200);
  
  // 4-6. Rangos técnicos - SOLO capturar si realmente se eligió rama técnica
  if (esTecnica && preguntasTecnicasVisitadas) {
    console.log("📊 Capturando rangos técnicos (rama técnica seleccionada y preguntas visibles)...");
    
    // Cilindrada
    captureRangeValues('cilindrada', 125, 600, true);
    
    // Potencia
    captureRangeValues('potencia', 15, 100, true);
    
    // Torque
    captureRangeValues('torque', 10, 80, true);
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
  
  // Preparar datos para enviar al servidor
  const testData = {
    // Datos básicos del test
    experiencia: window.testResults.experiencia,
    uso: window.testResults.uso,
    uso_previsto: window.testResults.uso_previsto,
    
    // RANGOS CUANTITATIVOS DIRECTOS
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
    }
  }
  
  // Agregar formulario al documento y enviarlo
  document.body.appendChild(form);
  console.log("📨 Enviando formulario con detección de rama técnica/práctica...");
  form.submit();
}

/**
 * Captura valores de rangos desde sliders
 * @param {string} key - Nombre del campo (sin sufijos _min/_max)
 * @param {number} defaultMin - Valor mínimo por defecto
 * @param {number} defaultMax - Valor máximo por defecto
 * @param {boolean} checkVisibility - Verificar si el elemento está en una pregunta visible
 */
function captureRangeValues(key, defaultMin, defaultMax, checkVisibility = false) {
  const minSlider = document.getElementById(`${key}_min`);
  const maxSlider = document.getElementById(`${key}_max`);
  
  let isVisible = true;
  if (checkVisibility) {
    const pregunta = minSlider?.closest('.pregunta');
    isVisible = pregunta && pregunta.classList.contains('active');
  }
  
  if (minSlider && maxSlider && isVisible) {
    window.testResults[`${key}_min`] = parseInt(minSlider.value);
    window.testResults[`${key}_max`] = parseInt(maxSlider.value);
    console.log(`✅ ${key.toUpperCase()} CAPTURADO: ${window.testResults[`${key}_min`]} - ${window.testResults[`${key}_max`]}`);
  } else {
    console.warn(`⚠️ Sliders de ${key} no encontrados o no visibles, usando valores por defecto`);
    window.testResults[`${key}_min`] = defaultMin;
    window.testResults[`${key}_max`] = defaultMax;
  }
}

// ==============================================
// DATOS DE PRUEBA PARA DEBUGGING
// ==============================================

/**
 * Datos de prueba para recomendaciones
 */
function loadTestData() {
  let testData = [
    {
      "modelo": "Test Moto 1",
      "marca": "Test Brand 1",
      "precio": 10000,
      "estilo": "Sport",
      "imagen": "test1.jpg",
      "score": 0.85,
      "razones": ["Razón 1", "Razón 2"]
    },
    {
      "modelo": "Test Moto 2",
      "marca": "Test Brand 2",
      "precio": 15000,
      "estilo": "Adventure",
      "imagen": "test2.jpg",
      "score": 0.75,
      "razones": ["Razón 3", "Razón 4"]
    }
  ];
  
  // Assign to window object
  window.testRecomendaciones = testData;
  
  console.log("🧪 Datos de prueba cargados:", window.testRecomendaciones);
}

// ==============================================
// DIAGNÓSTICO Y COMPROBACIÓN DE DEPENDENCIAS
// ==============================================

/**
 * Comprueba que todas las dependencias necesarias estén disponibles
 */
function diagnosticoDependencias() {
  console.log('🔍 Diagnóstico de dependencias del test unificado');
  
  // Comprobar componentes externos
  const counterSelectorDisponible = typeof window.CounterSelector === 'function';
  console.log(`✓ CounterSelector: ${counterSelectorDisponible ? 'Disponible ✅' : 'No disponible ❌'}`);
  
  const debugPanelDisponible = typeof window.debugPanel !== 'undefined';
  console.log(`✓ DebugPanel: ${debugPanelDisponible ? 'Disponible ✅' : 'No disponible ❌'}`);
  
  // Comprobar funciones propias exportadas
  const funcionesExportadas = [
    'finalizarTest', 
    'reorganizeTestQuestions', 
    'inicializarSoloEstilos', 
    'inicializarSoloMarcas',
    'verificarYRestaurarCanvas'
  ];
  
  funcionesExportadas.forEach(fn => {
    console.log(`✓ window.${fn}: ${typeof window[fn] === 'function' ? 'Exportada ✅' : 'No exportada ❌'}`);
  });
  
  // Estado global
  console.log(`✓ window.testResults: ${typeof window.testResults !== 'undefined' ? 'Inicializado ✅' : 'No inicializado ❌'}`);
  console.log(`✓ window.respuestas: ${typeof window.respuestas !== 'undefined' ? 'Inicializado ✅' : 'No inicializado ❌'}`);
  
  return {
    counterSelector: counterSelectorDisponible,
    debugPanel: debugPanelDisponible,
    funcionesExportadas: funcionesExportadas.filter(fn => typeof window[fn] === 'function')
  };
}

// ==============================================
// INICIALIZACIÓN Y EXPORTACIÓN DE FUNCIONES
// ==============================================

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  console.log('🔧 Test Unificado cargado');
  
  // Inicializar test
  initializeTest();
  
  // Ocultar preguntas de rama al inicio
  setTimeout(hideAllBranchQuestions, 100);
  
  // Cargar datos de prueba (solo para desarrollo)
  if (window.location.href.includes('debug=true')) {
    loadTestData();
  }
  
  // Ejecutar diagnóstico para verificar dependencias
  setTimeout(diagnosticoDependencias, 500);
});

// Exponer funciones globalmente para que sean accesibles desde otros scripts
window.finalizarTest = finalizarTest;
window.reorganizeTestQuestions = reorganizeTestQuestions;
window.inicializarSoloEstilos = inicializarSoloEstilos;
window.inicializarSoloMarcas = inicializarSoloMarcas;
window.verificarYRestaurarCanvas = verificarYRestaurarCanvas;
window.diagnosticoTestUnificado = diagnosticoDependencias;
