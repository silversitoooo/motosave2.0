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
  },
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
    
    // Inicializar los selectores de contadores
    const estilosContainer = document.getElementById('estilos-canvas');
    const marcasContainer = document.getElementById('marcas-canvas');
    
    if (estilosContainer) {
      setupBubblesSelector('estilos', estilosContainer);
    }
    
    if (marcasContainer) {
      setupBubblesSelector('marcas', marcasContainer);
    }
    
    // Inicializar estado
    window.testResults = {};
    
    // Ocultar todas las preguntas de rama por defecto
    document.querySelectorAll('.rama-tecnica, .rama-practica').forEach(pregunta => {
      pregunta.classList.remove('active');
    });
    
    // Configurar la primera pregunta como activa
    if (testState.stageContainers.length > 0) {
      testState.stageContainers[0].classList.add('active');
      updateProgressBar(0, getVisibleStagesCount());
    }
    
    console.log('Test inicializado con éxito');
  } else {
    console.warn('No se encontraron elementos de pregunta para inicializar el test');
  }
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
      const stageKey = this.closest('.pregunta').getAttribute('data-key');
      const value = this.value;
      
      // Guardar el valor en respuestas
      window.respuestas = window.respuestas || {};
      window.respuestas[stageKey] = value;
      
      // Guardar en testResults para coherencia
      window.testResults = window.testResults || {};
      window.testResults[stageKey] = value;
      
      console.log(`Seleccionado ${stageKey}: ${value}`);
      
      // --- DESHABILITADO: Control de ramas ahora solo en test_branch_fixed.js ---
      // if (stageKey === 'interesa_especificaciones') {
      //   setupBranchQuestions(value);
      // }
      
      // Si el select corresponde a experiencia, configurar la rama correspondiente
      if (stageKey === 'experiencia') {
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
  
  // Revisar si CounterSelector está disponible
  setTimeout(function() {
    console.log('CounterSelector disponible:', typeof window.CounterSelector === 'function');
    console.log('recuperarTest disponible:', typeof window.recuperarTest === 'function');
  }, 1000);
  
  // Asegurar que los contenedores tengan tamaño adecuado
  const contenedores = ['estilos-canvas', 'marcas-canvas'];
  contenedores.forEach(id => {
    const contenedor = document.getElementById(id);
    if (contenedor) {
      contenedor.style.minHeight = '300px';
      contenedor.style.minWidth = '100%';
    }
  });
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
      // Usar opciones básicas para estos tipos
      setupBasicOptions(stage.id, optionsContainer);
      break;

    case 'estilos_preferidos':
      // Configurar selector de contadores para estilos
      setupBubblesSelector('estilos', optionsContainer);
      break;

    case 'marcas_preferidas':
      // Configurar selector de contadores para marcas
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
        window.respuestas.uso_principal = value;
        window.testResults.uso_principal = value;
      } else {
        window.respuestas[optionType] = value;
        window.testResults[optionType] = value;
      }
      
      console.log(`Seleccionado ${optionType}: ${value}`);
    });
  });
}

// Configurar selector de contadores para estilos y marcas
function setupBubblesSelector(type, container) {
  console.log(`Configurando selector de contadores para ${type}...`);
  
  if (!container) {
    console.error(`Contenedor para selección de ${type} no encontrado`);
    return;
  }
  
  // Limpiar el contenedor
  container.innerHTML = '';
  
  // Determinar opciones según el tipo
  let options = [];
  
  if (type === 'estilos') {
    options = [
      { id: 'naked', label: 'Naked', value: 1.0 },
      { id: 'sport', label: 'Deportiva', value: 1.0 },
      { id: 'supersport', label: 'Supersport', value: 1.0 },
      { id: 'touring', label: 'Touring', value: 1.0 },
      { id: 'adventure', label: 'Adventure', value: 1.0 },
      { id: 'trail', label: 'Trail', value: 1.0 },
      { id: 'enduro', label: 'Enduro', value: 1.0 },
      { id: 'motocross', label: 'Motocross', value: 1.0 },
      { id: 'supermoto', label: 'Supermoto', value: 1.0 },
      { id: 'scooter', label: 'Scooter', value: 1.0 },
      { id: 'custom', label: 'Custom', value: 1.0 },
      { id: 'cruiser', label: 'Cruiser', value: 1.0 },
      { id: 'chopper', label: 'Chopper', value: 1.0 },
      { id: 'cafe_racer', label: 'Café Racer', value: 1.0 },
      { id: 'scrambler', label: 'Scrambler', value: 1.0 },
      { id: 'bobber', label: 'Bobber', value: 1.0 },
      { id: 'streetfighter', label: 'Streetfighter', value: 1.0 },
      { id: 'vintage', label: 'Vintage/Clásica', value: 1.0 },
      { id: 'electrica', label: 'Eléctrica', value: 1.0 },
      { id: 'trike', label: 'Trike', value: 1.0 }
    ];
  } else if (type === 'marcas') {
    options = [
      // Marcas japonesas principales
      { id: 'honda', label: 'Honda', value: 1.0 },
      { id: 'yamaha', label: 'Yamaha', value: 1.0 },
      { id: 'suzuki', label: 'Suzuki', value: 1.0 },
      { id: 'kawasaki', label: 'Kawasaki', value: 1.0 },
      
      // Marcas europeas
      { id: 'ducati', label: 'Ducati', value: 1.0 },
      { id: 'bmw', label: 'BMW', value: 1.0 },
      { id: 'triumph', label: 'Triumph', value: 1.0 },
      { id: 'ktm', label: 'KTM', value: 1.0 },
      { id: 'husqvarna', label: 'Husqvarna', value: 1.0 },
      { id: 'aprilia', label: 'Aprilia', value: 1.0 },
      { id: 'mv_agusta', label: 'MV Agusta', value: 1.0 },
      { id: 'moto_guzzi', label: 'Moto Guzzi', value: 1.0 },
      { id: 'benelli', label: 'Benelli', value: 1.0 },
      
      // Marcas americanas
      { id: 'harley_davidson', label: 'Harley-Davidson', value: 1.0 },
      { id: 'indian', label: 'Indian', value: 1.0 },
      
      // Marcas chinas/asiáticas
      { id: 'cfmoto', label: 'CFMoto', value: 1.0 },
      { id: 'kymco', label: 'Kymco', value: 1.0 },
      { id: 'sym', label: 'SYM', value: 1.0 },
      { id: 'piaggio', label: 'Piaggio', value: 1.0 },
      { id: 'vespa', label: 'Vespa', value: 1.0 },
      
      // Marcas emergentes/otras
      { id: 'royal_enfield', label: 'Royal Enfield', value: 1.0 },
      { id: 'zero', label: 'Zero (Eléctrica)', value: 1.0 },
      { id: 'energica', label: 'Energica', value: 1.0 },
      { id: 'gas_gas', label: 'Gas Gas', value: 1.0 },
      { id: 'beta', label: 'Beta', value: 1.0 },
      { id: 'sherco', label: 'Sherco', value: 1.0 }
    ];
  }
  
  // Inicializar CounterSelector con verificación
  if (typeof window.CounterSelector !== 'function') {
    console.error('Error crítico: CounterSelector no está disponible como función');
    
    // Mostrar un mensaje de error en el contenedor
    container.innerHTML = `
      <div class="error-message">
        <p>Error al cargar el componente de selección.</p>
        <button onclick="window.location.reload()">Recargar página</button>
      </div>
    `;
    return;
  }
  
  try {
    // Crear instancia del selector de contadores
    const counterSelector = new window.CounterSelector(container, {
      items: options,
      onChange: (selections) => {
        // Guardar selecciones en objeto global 'respuestas'
        window.respuestas = window.respuestas || {};
        window.respuestas[type] = selections;
        
        // También guardar en testResults para coherencia
        window.testResults = window.testResults || {};
        window.testResults[type] = selections;
        
        // Log para diagnóstico
        console.log(`Selecciones de ${type} actualizadas:`, selections);
      }
    });
    
    // Guardar referencia global para facilitar el acceso
    window[`${type}Selector`] = counterSelector;
    
    console.log(`Selector de contadores para ${type} inicializado correctamente`);
  } catch (error) {
    console.error(`Error al inicializar selector para ${type}:`, error);
    
    // Mostrar mensaje de error en el contenedor
    container.innerHTML = `
      <div class="error-message">
        <p>Error: ${error.message}</p>
        <button onclick="window.location.reload()">Recargar página</button>
      </div>
    `;
  }
}

// Navegación a la etapa anterior
function navigateToPreviousStage() {
  const currentIndex = testState.currentStageIndex;
  if (currentIndex <= 0) return;
  
  // Obtener clave de la etapa actual para guardar datos
  const currentStage = testState.stageContainers[currentIndex];
  const currentKey = currentStage.getAttribute('data-key');
  
  // Guardar selecciones actuales si es un selector de contadores
  if (currentStage.getAttribute('data-type') === 'selector' || currentStage.getAttribute('data-type') === 'bubbles') {
    const counterSelector = window[`${currentKey}Selector`];
    if (counterSelector) {
      window.respuestas[currentKey] = counterSelector.getSelections();
      window.testResults[currentKey] = counterSelector.getSelections();
    }
  }
  
  // Guardar datos de selects
  const select = currentStage.querySelector('select');
  if (select && select.value) {
    window.respuestas[currentKey] = select.value;
    window.testResults[currentKey] = select.value;
  }
  
  // Ocultar etapa actual
  currentStage.classList.remove('active');
  
  // Buscar la etapa anterior visible
  let prevIndex = findPreviousVisibleStage(currentIndex);
  if (prevIndex !== -1 && prevIndex >= 0) {
    // Obtener la rama activa según la selección del usuario
    const ramaTecnicaActiva = document.getElementById('interesa_especificaciones')?.value === 'si';
    const ramaPracticaActiva = document.getElementById('interesa_especificaciones')?.value === 'no';
    
    // Ocultar TODAS las preguntas de ambas ramas primero
    document.querySelectorAll('.rama-tecnica, .rama-practica').forEach(p => {
      p.classList.remove('active');
    });
    
    // Si es una pregunta de rama, verificar que sea de la rama correcta
    const prevStage = testState.stageContainers[prevIndex];
    if (prevStage.classList.contains('rama-tecnica') && !ramaTecnicaActiva) {
      console.error('Error de navegación: Intentando mostrar pregunta técnica pero la rama técnica no está activa');
      return; // No continuar si hay incoherencia
    } else if (prevStage.classList.contains('rama-practica') && !ramaPracticaActiva) {
      console.error('Error de navegación: Intentando mostrar pregunta práctica pero la rama práctica no está activa');
      return; // No continuar si hay incoherencia
    }
    
    // Mostrar etapa anterior
    prevStage.classList.add('active');
    testState.currentStageIndex = prevIndex;
    
    // Actualizar barra de progreso
    updateProgressBar(prevIndex, getVisibleStagesCount());
    
    // Habilitar/deshabilitar botones según corresponda
    document.getElementById('prev-btn').disabled = (prevIndex === 0);
    document.getElementById('next-btn').disabled = false;
    
    // Restaurar texto del botón siguiente si no es la última etapa
    if (!isLastVisibleStage(prevIndex)) {
      document.getElementById('next-btn').innerHTML = 'Siguiente <i class="fas fa-arrow-right"></i>';
    }
  }
  
  // Verificar integridad después de la navegación
  setTimeout(verificarYRestaurarCanvas, 100, 'navegación previa');
}

// Función para encontrar la etapa anterior visible
function findPreviousVisibleStage(currentIndex) {
  let prevIndex = currentIndex - 1;
  const ramaTecnicaActiva = document.getElementById('interesa_especificaciones')?.value === 'si';
  const ramaPracticaActiva = document.getElementById('interesa_especificaciones')?.value === 'no';
  
  console.log(`Buscando etapa previa visible antes de ${currentIndex}, rama técnica: ${ramaTecnicaActiva}, rama práctica: ${ramaPracticaActiva}`);
  
  while (prevIndex >= 0) {
    const stage = testState.stageContainers[prevIndex];
    
    // Si es una pregunta normal (no de rama)
    if (!stage.classList.contains('rama-tecnica') && !stage.classList.contains('rama-practica')) {
      if (!stage.hasAttribute('data-hidden')) {
        // Pregunta normal visible
        console.log(`Encontrada etapa previa general: ${prevIndex}, ID: ${stage.id}`);
        return prevIndex;
      }
    }
    // Si es una pregunta de rama técnica y estamos en rama técnica
    else if (stage.classList.contains('rama-tecnica')) {
      if (ramaTecnicaActiva) {
        console.log(`Encontrada etapa previa técnica: ${prevIndex}, ID: ${stage.id}`);
        return prevIndex;
      } else {
        // No es la rama activa, saltamos esta pregunta
        console.log(`Ignorando pregunta técnica previa ${stage.id} porque no es la rama seleccionada`);
      }
    }
    // Si es una pregunta de rama práctica y estamos en rama práctica
    else if (stage.classList.contains('rama-practica')) {
      if (ramaPracticaActiva) {
        console.log(`Encontrada etapa previa práctica: ${prevIndex}, ID: ${stage.id}`);
        return prevIndex;
      } else {
        // No es la rama activa, saltamos esta pregunta
        console.log(`Ignorando pregunta práctica previa ${stage.id} porque no es la rama seleccionada`);
      }
    }
    
    prevIndex--;
  }
  
  return -1; // No se encontró etapa anterior visible
}

// Navegación a la siguiente etapa
function navigateToNextStage() {
  const currentIndex = testState.currentStageIndex;
  
  // Obtener clave de la etapa actual para guardar datos
  const currentStage = testState.stageContainers[currentIndex];
  const stageKey = currentStage.getAttribute('data-key');
  
  // Guardar selecciones actuales si es un selector de contadores
  if (currentStage.getAttribute('data-type') === 'selector' || currentStage.getAttribute('data-type') === 'bubbles') {
    const counterSelector = window[`${stageKey}Selector`];
    if (counterSelector) {
      window.respuestas[stageKey] = counterSelector.getSelections();
      window.testResults[stageKey] = counterSelector.getSelections();
    }
  }
  
  // Guardar datos de selects
  const select = currentStage.querySelector('select');
  if (select && select.value) {
    window.respuestas[stageKey] = select.value;
    window.testResults[stageKey] = select.value;
  }
  
  // Guardar datos de inputs (presupuesto)
  const inputs = currentStage.querySelectorAll('input');
  if (inputs.length > 0) {
    inputs.forEach(input => {
      if (input.name && input.value) {
        window.respuestas[input.name] = input.value;
        window.testResults[input.name] = input.value;
      }
    });
  }
  
  // Ocultar etapa actual
  currentStage.classList.remove('active');
  
  // Buscar la siguiente etapa visible
  let nextIndex = findNextVisibleStage(currentIndex);
  if (nextIndex !== -1 && nextIndex < testState.stageContainers.length) {
    // Obtener la rama activa según la selección del usuario
    const ramaTecnicaActiva = document.getElementById('interesa_especificaciones')?.value === 'si';
    const ramaPracticaActiva = document.getElementById('interesa_especificaciones')?.value === 'no';
    
    // Ocultar TODAS las preguntas de ambas ramas primero
    document.querySelectorAll('.rama-tecnica, .rama-practica').forEach(p => {
      p.classList.remove('active');
    });
    
    // Si es una pregunta de rama, verificar que sea de la rama correcta
    const nextStage = testState.stageContainers[nextIndex];
    if (nextStage.classList.contains('rama-tecnica') && !ramaTecnicaActiva) {
      console.error('Error de navegación: Intentando mostrar pregunta técnica pero la rama técnica no está activa');
      return; // No continuar si hay incoherencia
    } else if (nextStage.classList.contains('rama-practica') && !ramaPracticaActiva) {
      console.error('Error de navegación: Intentando mostrar pregunta práctica pero la rama práctica no está activa');
      return; // No continuar si hay incoherencia
    }
    
    // Mostrar siguiente etapa
    nextStage.classList.add('active');
    testState.currentStageIndex = nextIndex;
    
    // Actualizar barra de progreso
    updateProgressBar(nextIndex, getVisibleStagesCount());
    
    // Habilitar/deshabilitar botones según corresponda
    document.getElementById('prev-btn').disabled = false;
    document.getElementById('next-btn').disabled = false;
    
    // Si es la última etapa visible, cambiar texto del botón
    if (isLastVisibleStage(nextIndex)) {
      document.getElementById('next-btn').innerHTML = 'Finalizar <i class="fas fa-check"></i>';
    } else {
      document.getElementById('next-btn').innerHTML = 'Siguiente <i class="fas fa-arrow-right"></i>';
    }
  } else {
    // No hay más etapas, mostrar modal de finalización
    showCompletionModal();
  }
    // Verificar integridad después de la navegación
  setTimeout(verificarYRestaurarCanvas, 100, 'navegación siguiente');
  
  // Verificar si es la última pregunta de la rama activa para mostrar el botón de finalización
  if (isLastVisibleStage(testState.currentStageIndex)) {
    document.getElementById('next-btn').innerHTML = 'Finalizar <i class="fas fa-check"></i>';
    console.log('Llegando al final del test, mostrando botón de finalización');
  }
}

// Función para encontrar la siguiente etapa visible
function findNextVisibleStage(currentIndex) {
  let nextIndex = currentIndex + 1;
  
  // Determinar la rama seleccionada por el usuario
  const interesaTecnica = document.getElementById('interesa_especificaciones')?.value === 'si';
  const interesaPractica = document.getElementById('interesa_especificaciones')?.value === 'no';
  
  console.log(`Buscando siguiente etapa visible después de ${currentIndex}, rama técnica: ${interesaTecnica}, rama práctica: ${interesaPractica}`);
  
  while (nextIndex < testState.stageContainers.length) {
    const stage = testState.stageContainers[nextIndex];
    
    // Si es una pregunta normal (no de rama)
    if (!stage.classList.contains('rama-tecnica') && !stage.classList.contains('rama-practica')) {
      if (!stage.hasAttribute('data-hidden')) {
        // Pregunta normal visible
        console.log(`Encontrada siguiente pregunta general: ${nextIndex}, ID: ${stage.id}`);
        return nextIndex;
      }
    }
    // Si es una pregunta de rama técnica
    else if (stage.classList.contains('rama-tecnica')) {
      if (interesaTecnica) {
        // Solo considerar si estamos en la rama técnica
        console.log(`Encontrada siguiente pregunta técnica: ${nextIndex}, ID: ${stage.id}`);
        return nextIndex;
      } else {
        // No es la rama activa, saltamos esta pregunta
        console.log(`Ignorando pregunta técnica ${stage.id} porque no es la rama seleccionada`);
      }
    } 
    // Si es una pregunta de rama práctica
    else if (stage.classList.contains('rama-practica')) {
      if (interesaPractica) {
        // Solo considerar si estamos en la rama práctica
        console.log(`Encontrada siguiente pregunta práctica: ${nextIndex}, ID: ${stage.id}`);
        return nextIndex;
      } else {
        // No es la rama activa, saltamos esta pregunta
        console.log(`Ignorando pregunta práctica ${stage.id} porque no es la rama seleccionada`);
      }
    }
    
    nextIndex++;
  }
  
  return -1; // No se encontró próxima etapa visible
}

// Función para verificar si es la última etapa visible
function isLastVisibleStage(index) {
  return findNextVisibleStage(index) === -1;
}

// Función para contar etapas visibles
function getVisibleStagesCount() {
  let count = 0;
  const ramaTecnicaActiva = document.getElementById('interesa_especificaciones')?.value === 'si';
  const ramaPracticaActiva = document.getElementById('interesa_especificaciones')?.value === 'no';
  
  console.log(`Calculando etapas visibles. Rama técnica activa: ${ramaTecnicaActiva}, Rama práctica activa: ${ramaPracticaActiva}`);
  
  // Contar preguntas generales primero (siempre visibles)
  const preguntasGenerales = Array.from(testState.stageContainers).filter(stage => {
    return !stage.classList.contains('rama-tecnica') && 
           !stage.classList.contains('rama-practica') && 
           !stage.hasAttribute('data-hidden');
  });
  count += preguntasGenerales.length;
  console.log(`Preguntas generales: ${preguntasGenerales.length}`);
  
  // Para las ramas técnica/práctica, solo contar las preguntas de la rama seleccionada
  if (ramaTecnicaActiva) {
    // Identificar cuántas preguntas específicas hay en la rama técnica
    const preguntasTecnicas = document.querySelectorAll('.rama-tecnica');
    count += preguntasTecnicas.length;
    console.log(`Preguntas técnicas: ${preguntasTecnicas.length}`);
  } else if (ramaPracticaActiva) {
    // Identificar cuántas preguntas específicas hay en la rama práctica
    const preguntasPracticas = document.querySelectorAll('.rama-practica');
    count += preguntasPracticas.length;
    console.log(`Preguntas prácticas: ${preguntasPracticas.length}`);
  }
  
  return count;
}

// Mostrar modal de finalización
function showCompletionModal() {
  // Transferir datos de selectores al testResults
  window.testResults = window.testResults || {};
  
  // Asegurar que las selecciones de contadores se transfieran
  if (window.respuestas && window.respuestas.estilos) {
    window.testResults.estilos = window.respuestas.estilos;
  }
  
  if (window.respuestas && window.respuestas.marcas) {
    window.testResults.marcas = window.respuestas.marcas;
  }
  
  // Usar el modal existente en el HTML en lugar de crearlo
  const modal = document.getElementById('completion-modal');
  if (!modal) {
    console.error('Modal de finalización no encontrado en el HTML');
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
      if (typeof testState.completionCallback === 'function') {
        testState.completionCallback(window.testResults);
      } else {
        console.log('Test finalizado. Datos:', window.testResults);
      }
    });
  }
  
  // Mostrar modal
  modal.style.display = 'flex';
}

// Reemplazar estas funciones para que usen CounterSelector en lugar de burbujas

function inicializarSoloEstilos() {
  setupBubblesSelector('estilos', document.getElementById('estilos-canvas'));
}

function inicializarSoloMarcas() {
  setupBubblesSelector('marcas', document.getElementById('marcas-canvas'));
}

// También añadir esta función para verificar y restaurar el estado
function verificarYRestaurarCanvas(origen) {
  const estilosCanvas = document.getElementById('estilos-canvas');
  const marcasCanvas = document.getElementById('marcas-canvas');
  
  if (estilosCanvas) {
    setupBubblesSelector('estilos', estilosCanvas);
  }
  
  if (marcasCanvas) {
    setupBubblesSelector('marcas', marcasCanvas);
  }
  
  console.log(`Canvas restaurados desde: ${origen}`);
}

// Función para ocultar todas las preguntas de rama
function hideAllBranchQuestions() {
  console.log('Ocultando todas las preguntas de rama...');
  
  // Ocultar todas las preguntas de rama técnica y práctica
  document.querySelectorAll('.rama-tecnica, .rama-practica').forEach(pregunta => {
    pregunta.classList.remove('active');
  });
  
  console.log('Todas las preguntas de ramas han sido ocultadas');
}

// Llamar a esta función al inicio
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(hideAllBranchQuestions, 100);
});

// Exponer funciones globalmente para que sean accesibles desde otros scripts
window.inicializarSoloEstilos = inicializarSoloEstilos;
window.inicializarSoloMarcas = inicializarSoloMarcas;
window.verificarYRestaurarCanvas = verificarYRestaurarCanvas;