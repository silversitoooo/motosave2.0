/**
 * Test de preferencias de motos - Lógica principal
 */

console.log('Inicializando Test de Preferencias de Motos...');

// Inicialización global de respuestas
window.respuestas = {
  estilos: {},
  marcas: {}
};

// Estado general del test
const testState = {
  currentStageIndex: 0,
  stageContainers: [],
  stageIndicators: [],
  testResults: {},
  completionCallback: null
};

// Etapas configurables del test - Reordenadas para coincidir con el HTML
const testStages = [
  {
    id: 'pregunta-1',
    key: 'estilos',
    title: 'Estilos de Moto',
    description: 'Selecciona los estilos de moto que más te interesan',
    type: 'bubbles'
  },
  {
    id: 'pregunta-2',
    key: 'marcas',
    title: 'Marcas Preferidas', 
    description: 'Selecciona tus marcas favoritas o las que más te interesan',
    type: 'bubbles'
  },
  {
    id: 'pregunta-3',
    key: 'experiencia',
    title: 'Experiencia de Manejo',
    description: 'Cuéntanos sobre tu nivel de experiencia con las motos',
    type: 'select'
  },
  // Resto de preguntas se cargarán dinámicamente según la rama (inexperto/experto)
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

// Función para inicializar el test
function initializeTest() {
  console.log('Inicializando test...');
  
  // Obtener elementos principales
  const testContainer = document.querySelector('.test-container');
  const progressBar = document.getElementById('progress-bar');
  
  if (!testContainer) {
    console.error('No se encontró el contenedor principal del test');
    return;
  }
  
  // Usar los elementos existentes en lugar de crearlos
  const existingStages = document.querySelectorAll('.pregunta');
  if (existingStages.length > 0) {
    console.log(`Encontradas ${existingStages.length} etapas existentes en el HTML`);
    
    // Inicializar contenedores para cada etapa
    testState.stageContainers = Array.from(existingStages);
    
    // Configurar visibilidad inicial (mostrar solo la primera etapa)
    testState.stageContainers.forEach((container, i) => {
      if (i === 0) {
        container.classList.add('active');
        container.style.display = 'block';
      } else {
        container.classList.remove('active');
        container.style.display = 'none';
      }
    });
    
    // Configurar botones de navegación
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    if (prevBtn) {
      prevBtn.addEventListener('click', navigateToPreviousStage);
    }
    
    if (nextBtn) {
      nextBtn.addEventListener('click', navigateToNextStage);
    }
    
    // Inicializar burbujas para estilos y marcas
    setupBubblesSelector('estilos', document.getElementById('estilos-canvas'));
    setupBubblesSelector('marcas', document.getElementById('marcas-canvas'));
    
    // Configurar evento de selección para las opciones desplegables
    setupSelectListeners();
  } else {
    console.error('No se encontraron etapas del test en el HTML');
    return;
  }
  
  // Actualizar la barra de progreso
  updateProgressBar(0, testState.stageContainers.length);
  
  console.log('Test inicializado correctamente');
}

// Función para actualizar la barra de progreso
function updateProgressBar(current, total) {
  const progressBar = document.getElementById('progress-bar');
  if (progressBar) {
    const percentage = (current / (total - 1)) * 100;
    progressBar.style.width = `${percentage}%`;
  }
}

// Configurar listeners para los elementos select
function setupSelectListeners() {
  const selects = document.querySelectorAll('.pregunta select');
  selects.forEach(select => {
    select.addEventListener('change', function() {
      const key = this.name;
      const value = this.value;
      
      // Guardar valor seleccionado
      window.testResults = window.testResults || {};
      window.testResults[key] = value;
      
      console.log(`Seleccionado ${key}: ${value}`);
      
      // Si es el select de experiencia, configurar la rama correspondiente
      if (key === 'experiencia') {
        setupExperienceBranch(value);
      }
    });
  });
}

// Configurar la rama según la experiencia seleccionada
function setupExperienceBranch(experienceLevel) {
  console.log(`Configurando rama para nivel de experiencia: ${experienceLevel}`);
  
  const inexperto = document.querySelectorAll('.rama-inexperto');
  const experto = document.querySelectorAll('.rama-experto');
  
  // Ocultar todas las ramas primero
  inexperto.forEach(el => el.setAttribute('data-hidden', 'true'));
  experto.forEach(el => el.setAttribute('data-hidden', 'true'));
  
  // Mostrar la rama correspondiente
  if (experienceLevel === 'inexperto') {
    inexperto.forEach(el => el.removeAttribute('data-hidden'));
  } else {
    experto.forEach(el => el.removeAttribute('data-hidden'));
  }
}

// Exponer la función globalmente para que la template pueda usarla
window.initializeTest = initializeTest;

// Modificar el listener DOMContentLoaded para evitar inicialización duplicada
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM cargado. La inicialización se manejará por la plantilla HTML');
  // No inicializamos aquí para evitar duplicación, ya que la plantilla llamará a initializeTest
});

// Depuración adicional al cargar la página
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM cargado en test.js');
  console.log('Elementos de pregunta:', document.querySelectorAll('.pregunta').length);
  console.log('Botones de navegación:', {
    prev: document.getElementById('prev-btn'),
    next: document.getElementById('next-btn')
  });
  
  // Revisar si MagneticBubbles está disponible
  setTimeout(function() {
    console.log('MagneticBubbles disponible:', typeof window.MagneticBubbles === 'function');
    console.log('recuperarTest disponible:', typeof window.recuperarTest === 'function');
  }, 1000);
});

// Configurar el contenido específico para cada etapa
function setupStageContent(stage, container) {
  const optionsContainer = container.querySelector(`#options-${stage.id}`);
  
  if (!optionsContainer) {
    console.error(`No se encontró el contenedor de opciones para la etapa ${stage.id}`);
    return;
  }
  
  // Diferentes configuraciones según el tipo de etapa
  switch(stage.id) {
    case 'experiencia':
    case 'presupuesto':
    case 'uso_principal':
      setupBasicOptions(stage.id, optionsContainer);
      break;
    case 'estilos_preferidos':
      setupBubblesSelector('estilos', optionsContainer);
      break;
    case 'marcas_preferidas':
      setupBubblesSelector('marcas', optionsContainer);
      break;
    default:
      console.warn(`Tipo de etapa no reconocido: ${stage.id}`);
  }
}

// Configurar opciones básicas (botones simples)
function setupBasicOptions(optionType, container) {
  const options = testOptions[optionType];
  
  if (!options) {
    console.error(`No se encontraron opciones para ${optionType}`);
    return;
  }
  
  const optionsHTML = options.map(option => {
    return `
      <div class="option-card" data-value="${option.id}">
        <i class="${option.icon}"></i>
        <span>${option.label}</span>
      </div>
    `;
  }).join('');
  
  container.innerHTML = optionsHTML;
  
  // Añadir evento de selección
  container.querySelectorAll('.option-card').forEach(card => {
    card.addEventListener('click', (e) => {
      // Remover selección previa
      container.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
      
      // Marcar como seleccionado
      card.classList.add('selected');
      
      // Guardar valor seleccionado
      const value = card.getAttribute('data-value');
      if (optionType === 'uso_principal') {
        window.testResults = window.testResults || {};
        window.testResults.uso = value;
      } else {
        window.testResults = window.testResults || {};
        window.testResults[optionType] = value;
      }
      
      console.log(`Seleccionado ${optionType}: ${value}`);
    });
  });
}

// Configurar selector de burbujas para estilos y marcas
function setupBubblesSelector(type, container) {
  console.log(`Configurando selector de burbujas para ${type}...`);
  
  if (!container) {
    console.error(`Contenedor para burbujas de ${type} no encontrado`);
    return;
  }
  
  // Crear canvas para las burbujas si no existe
  let canvasElement = container.querySelector('canvas');
  if (!canvasElement) {
    canvasElement = document.createElement('canvas');
    canvasElement.id = `canvas-${type}`;
    canvasElement.className = 'bubbles-canvas';
    canvasElement.style.width = '100%';
    canvasElement.style.height = '100%';
    container.appendChild(canvasElement);
  }
  
  // Determinar opciones según el tipo
  let options = [];
  
  if (type === 'estilos') {
    options = [
      { id: 'naked', label: 'Naked', value: 1.0 },
      { id: 'sport', label: 'Deportiva', value: 1.0 },
      { id: 'touring', label: 'Touring', value: 1.0 },
      { id: 'trail', label: 'Trail/Adventure', value: 1.0 },
      { id: 'scooter', label: 'Scooter', value: 1.0 },
      { id: 'custom', label: 'Custom/Cruiser', value: 1.0 }
    ];
  } else if (type === 'marcas') {
    options = [
      { id: 'honda', label: 'Honda', value: 1.0 },
      { id: 'yamaha', label: 'Yamaha', value: 1.0 },
      { id: 'suzuki', label: 'Suzuki', value: 1.0 },
      { id: 'kawasaki', label: 'Kawasaki', value: 1.0 },
      { id: 'ducati', label: 'Ducati', value: 1.0 },
      { id: 'bmw', label: 'BMW', value: 1.0 },
      { id: 'triumph', label: 'Triumph', value: 1.0 },
      { id: 'ktm', label: 'KTM', value: 1.0 }
    ];
  }
  
  // Inicializar MagneticBubbles con verificación
  if (typeof window.MagneticBubbles !== 'function') {
    console.error('Error crítico: MagneticBubbles no está disponible como función');
    
    // Intento de recuperación automática usando la recuperación existente
    if (typeof window.recuperarTest === 'function') {
      console.log('Intentando recuperación automática de burbujas...');
      setTimeout(window.recuperarTest, 500);
    } else {
      alert('Error al cargar el componente de burbujas. Por favor, recarga la página.');
    }
    return;
  }
  
  try {
    // Configurar dimensiones consistentes para ambos canvas
    const containerWidth = container.clientWidth || 300;
    const containerHeight = container.clientHeight || 400;
    canvasElement.width = containerWidth;
    canvasElement.height = containerHeight;
    
    const bubbles = new window.MagneticBubbles(canvasElement, {
      items: options,
      selectionMode: 'multiple',
      canvasBackground: 'rgba(0, 0, 0, 0.8)',
      bubbleBaseColor: '#f97316',
      bubbleSelectedColor: '#ea580c',
      textColor: '#ffffff',
      width: containerWidth,
      height: containerHeight
    });
    
    // Guardar referencia global para facilitar el acceso
    window[`${type}Bubbles`] = bubbles;
    
    // Evento de cambio de selección
    canvasElement.addEventListener('selection-changed', (e) => {
      const selections = e.detail.selections;
      
      // Guardar selecciones en objeto global 'respuestas'
      window.respuestas = window.respuestas || {};
      window.respuestas[type] = selections;
      
      // También guardar en testResults para coherencia
      window.testResults = window.testResults || {};
      window.testResults[type] = selections;
      
      // Log para diagnóstico
      console.log(`Selecciones de ${type} actualizadas:`, selections);
    });
    
    console.log(`Burbujas de ${type} inicializadas correctamente`);
  } catch (error) {
    console.error(`Error al inicializar burbujas para ${type}:`, error);
    
    // Intento de recuperación automática
    if (typeof window.recuperarTest === 'function') {
      console.log('Intentando recuperación después de error...');
      setTimeout(window.recuperarTest, 500);
    }
  }
}

/**
 * Verifica periódicamente el estado de los canvas y los restaura si es necesario
 */
function iniciarVerificacionPeriodica() {
    // Verificar cada 3 segundos 
    const intervaloVerificacion = setInterval(function() {
        const preguntaActiva = document.querySelector('.pregunta-container.active');
        if (!preguntaActiva) return;
        
        // Determinar qué tipo de canvas verificar según la pregunta activa
        let canvasId = null;
        if (preguntaActiva.id === 'pregunta-1') {
            canvasId = 'estilos-canvas';
        } else if (preguntaActiva.id === 'pregunta-2') {
            canvasId = 'marcas-canvas';
        }
        
        if (canvasId) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            // Verificar si el canvas tiene contenido visible
            const esVacio = canvas.innerHTML.trim() === '';
            const esInvisible = canvas.offsetHeight < 50 || canvas.offsetWidth < 50;
            
            if (esVacio || esInvisible) {
                console.warn(`Canvas ${canvasId} detectado vacío o invisible. Intentando restaurar...`);
                if (canvasId === 'estilos-canvas') {
                    inicializarSoloEstilos();
                } else if (canvasId === 'marcas-canvas') {
                    inicializarSoloMarcas();
                }
            }
        }
    }, 3000);
    
    // Almacenar el ID del intervalo para poder detenerlo cuando sea necesario
    window.verificacionCanvasInterval = intervaloVerificacion;
}

// Iniciar la verificación después de cargar la página
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(iniciarVerificacionPeriodica, 2000);
});

// Asegurar que se verifica el estado al cambiar de pestaña
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function() {
        // Dar tiempo para que se complete la transición
        setTimeout(function() {
            console.log("Verificando estado de canvas después de cambio de pestaña");
            const preguntaActiva = document.querySelector('.pregunta-container.active');
            if (preguntaActiva && preguntaActiva.id === 'pregunta-1') {
                verificarEstadoCanvas('estilos-canvas');
            } else if (preguntaActiva && preguntaActiva.id === 'pregunta-2') {
                verificarEstadoCanvas('marcas-canvas');
            }
        }, 500);
    });
});

function verificarEstadoCanvas(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const container = canvas.parentElement;
    if (!container) return;
    
    const containerRect = container.getBoundingClientRect();
    
    // Si el contenedor es muy pequeño o invisible
    if (containerRect.width < 100 || containerRect.height < 100) {
        console.warn(`Contenedor de ${canvasId} demasiado pequeño, forzando redimensión`);
        
        // Forzar tamaño mínimo al contenedor
        container.style.minWidth = '300px';
        container.style.minHeight = '300px';
        
        // Reinicializar el canvas
        if (canvasId === 'estilos-canvas') {
            inicializarSoloEstilos();
        } else if (canvasId === 'marcas-canvas') {
            inicializarSoloMarcas();
        }
    }
}

// Navegación a la etapa anterior
function navigateToPreviousStage() {
  console.log("Navegando a la etapa anterior");
  
  if (testState.currentStageIndex > 0) {
    // Guardar el estado de la etapa actual antes de cambiar
    const currentStage = testState.stageContainers[testState.currentStageIndex];
    const currentType = currentStage.getAttribute('data-type');
    const currentKey = currentStage.getAttribute('data-key');
    
    // Guardar datos específicos de burbujas si es necesario
    if (currentType === 'bubbles' && (currentKey === 'estilos' || currentKey === 'marcas')) {
      // Guardar explícitamente el estado del canvas actual
      const bubbleInstance = window[`${currentKey}Bubbles`];
      if (bubbleInstance && typeof bubbleInstance.getSelections === 'function') {
        window.respuestas = window.respuestas || {};
        window.respuestas[currentKey] = bubbleInstance.getSelections();
        
        window.testResults = window.testResults || {};
        window.testResults[currentKey] = window.respuestas[currentKey];
      }
    }
    
    // Ocultar etapa actual
    testState.stageContainers[testState.currentStageIndex].classList.remove('active');
    testState.stageContainers[testState.currentStageIndex].style.display = 'none';
    
    // Mostrar etapa anterior
    testState.currentStageIndex--;
    testState.stageContainers[testState.currentStageIndex].classList.add('active');
    testState.stageContainers[testState.currentStageIndex].style.display = 'block';
    
    // Verificar si la nueva etapa activa necesita reinicialización
    const newStage = testState.stageContainers[testState.currentStageIndex];
    const newType = newStage.getAttribute('data-type');
    const newKey = newStage.getAttribute('data-key');
    
    if (newType === 'bubbles') {
      console.log(`Navegado a etapa de burbujas ${newKey}, verificando canvas...`);
      
      // Llamar a funciones de recuperación para garantizar que el canvas sea funcional
      setTimeout(function() {
        if (typeof window.verificarYRestaurarCanvas === 'function') {
          window.verificarYRestaurarCanvas('prev-navigation');
        } else if (typeof window.recuperarTest === 'function') {
          window.recuperarTest();
        }
      }, 100);
    }
    
    // Actualizar botón "Anterior" 
    document.getElementById('prev-btn').disabled = (testState.currentStageIndex === 0);
    
    // Actualizar barra de progreso
    updateProgressBar(testState.currentStageIndex, testState.stageContainers.length);
  }
}

// Navegación a la siguiente etapa
function navigateToNextStage() {
  // Log del estado actual para depuración
  console.log("Navegando a la siguiente etapa:", {
    currentStageIndex: testState.currentStageIndex,
    currentStageId: testState.stageContainers[testState.currentStageIndex].id,
    totalStages: testState.stageContainers.length,
  });
  
  // Validar selección según tipo de etapa
  const currentStage = testState.stageContainers[testState.currentStageIndex];
  const stageType = currentStage.getAttribute('data-type');
  const stageKey = currentStage.getAttribute('data-key');
  
  // Guardar datos específicos de burbujas si es necesario
  if (stageType === 'bubbles' && (stageKey === 'estilos' || stageKey === 'marcas')) {
    // Guardar explícitamente el estado del canvas actual
    const bubbleInstance = window[`${stageKey}Bubbles`];
    if (bubbleInstance && typeof bubbleInstance.getSelections === 'function') {
      window.respuestas = window.respuestas || {};
      window.respuestas[stageKey] = bubbleInstance.getSelections();
      
      window.testResults = window.testResults || {};
      window.testResults[stageKey] = window.respuestas[stageKey];
    }
  }
  
  // Validación específica por tipo
  if (stageType === 'select') {
    const select = currentStage.querySelector('select');
    if (select && select.value) {
      // Guardar la selección
      window.testResults = window.testResults || {};
      window.testResults[stageKey] = select.value;
    }
  } else if (stageType === 'bubbles') {
    // Para etapas de burbujas, no validamos - permitimos avanzar sin selecciones
    console.log(`Etapa de burbujas de ${stageKey}, no se requiere validación estricta`);
  }
  
  // Si es la última etapa visible, finalizar test
  let isLastVisible = true;
  for (let i = testState.currentStageIndex + 1; i < testState.stageContainers.length; i++) {
    if (!testState.stageContainers[i].hasAttribute('data-hidden')) {
      isLastVisible = false;
      break;
    }
  }
  
  if (isLastVisible) {
    console.log("Última etapa alcanzada, mostrando modal de finalización");
    showCompletionModal();
    return;
  }
  
  // Encontrar la siguiente etapa visible
  let nextIndex = testState.currentStageIndex + 1;
  while (nextIndex < testState.stageContainers.length && 
         testState.stageContainers[nextIndex].hasAttribute('data-hidden')) {
    nextIndex++;
  }
  
  if (nextIndex < testState.stageContainers.length) {
    // Ocultar etapa actual
    testState.stageContainers[testState.currentStageIndex].classList.remove('active');
    testState.stageContainers[testState.currentStageIndex].style.display = 'none';
    
    // Mostrar siguiente etapa
    testState.currentStageIndex = nextIndex;
    testState.stageContainers[testState.currentStageIndex].classList.add('active');
    testState.stageContainers[testState.currentStageIndex].style.display = 'block';
    
    // Verificar si la nueva etapa activa necesita reinicialización
    const newStage = testState.stageContainers[testState.currentStageIndex];
    const newType = newStage.getAttribute('data-type');
    const newKey = newStage.getAttribute('data-key');
    
    if (newType === 'bubbles') {
      console.log(`Navegado a etapa de burbujas ${newKey}, verificando canvas...`);
      
      // Llamar a funciones de recuperación para garantizar que el canvas sea funcional
      setTimeout(function() {
        if (typeof window.verificarYRestaurarCanvas === 'function') {
          window.verificarYRestaurarCanvas('next-navigation');
        } else if (typeof window.recuperarTest === 'function') {
          window.recuperarTest();
        }
      }, 100);
    }
    
    // Habilitar botón "Anterior"
    document.getElementById('prev-btn').disabled = false;
    
    // Actualizar barra de progreso
    updateProgressBar(testState.currentStageIndex, testState.stageContainers.length);
  } else {
    // Si no hay más etapas visibles, mostrar la finalización
    showCompletionModal();
  }
}

// Mostrar modal de finalización
function showCompletionModal() {
  // Transferir datos de burbujas al testResults
  window.testResults = window.testResults || {};
  
  // Asegurar que las selecciones de burbujas se transfieran
  if (window.respuestas && window.respuestas.estilos) {
    window.testResults.estilos = window.respuestas.estilos;
    console.log("Transferidos datos de estilos a testResults:", window.respuestas.estilos);
  }
  
  if (window.respuestas && window.respuestas.marcas) {
    window.testResults.marcas = window.respuestas.marcas;
    console.log("Transferidos datos de marcas a testResults:", window.respuestas.marcas);
  }
  
  // Usar el modal existente en el HTML en lugar de crearlo
  const modal = document.getElementById('completion-modal');
  if (!modal) {
    console.error("Modal de finalización no encontrado en el HTML");
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
      // Última verificación y transferencia de datos
      if (window.respuestas && window.respuestas.estilos) {
        window.testResults.estilos = window.respuestas.estilos;
      }
      
      if (window.respuestas && window.respuestas.marcas) {
        window.testResults.marcas = window.respuestas.marcas;
      }
      
      // Log final de diagnóstico
      console.log("Datos finales del test:", window.testResults);
      
      // Llamar a la función finalizarTest que está definida en el HTML
      if (typeof finalizarTest === 'function') {
        finalizarTest(window.testResults);
      } else {
        console.error("Función finalizarTest no encontrada");
        alert("Error al finalizar el test. Por favor, inténtalo de nuevo.");
      }
    });
  }
  
  // Mostrar modal
  modal.style.display = 'flex';
}