// Datos estáticos para las burbujas
const estilos = [
  "Deportiva", "Naked", "Adventure", "Cruiser", "Touring", 
  "Scooter", "Custom", "Trail", "Enduro", "Clásica"
];

const marcas = [
  "Honda", "Yamaha", "Kawasaki", "Suzuki", "BMW", "KTM", 
  "Ducati", "Triumph", "Harley-Davidson", "Royal Enfield", 
  "Aprilia", "Vespa", "Moto Guzzi", "Indian", "Husqvarna"
];

// Exponemos los arrays al scope global
window.estilos = estilos;
window.marcas = marcas;

// Variables globales para el componente MagneticBubbles
let bubbleInstances = {};
let activeCanvas = null;

// Objeto global para almacenar respuestas
window.respuestas = window.respuestas || {
  estilos: {},
  marcas: {},
  experiencia: "",
  uso: "",
  acompanantes: "",
  consumo: "",
  precio: "",
  potencia: "",
  torque: "",
  cilindrada: "",
  uso_experto: "",
  acompanantes_experto: "",
  precio_experto: ""
};

// Función para inicializar el test
function initializeTest() {
  try {
    console.log("Inicializando test con MagneticBubbles");
    
    // Ocultar botón de reintentar si está visible
    const retryButton = document.getElementById('retry-button');
    if (retryButton) {
      retryButton.style.display = 'none';
    }
    
    // Comprobar que MagneticBubbles está disponible
    if (!window.MagneticBubbles) {
      console.error('Error: MagneticBubbles no está cargado correctamente');
      if (retryButton) retryButton.style.display = 'block';
      return;
    }
    
    // Asegurarse de que solo la primera pregunta esté visible
    const preguntas = document.querySelectorAll('.pregunta');
    
    if (preguntas.length === 0) {
      console.error('Error: No se encontraron elementos con la clase .pregunta');
      if (retryButton) retryButton.style.display = 'block';
      return;
    }
    
    console.log(`Encontradas ${preguntas.length} preguntas en el DOM`);
    
    preguntas.forEach(element => {
      if (element.id === 'pregunta-1') {
        element.style.display = 'block';
        element.classList.add('active');
        console.log('Pregunta 1 activada');
      } else {
        element.style.display = 'none';
        element.classList.remove('active');
      }
    });
    
    // Actualizar barra de progreso inicial
    updateProgressBar();
    
    // Inicializar la primera pregunta con MagneticBubbles
    console.log('Inicializando burbujas de estilos...');
    
    // Verificar que el elemento canvas exista
    const estilosCanvas = document.getElementById('estilos-canvas');
    if (!estilosCanvas) {
      console.error('Error: No se encontró el contenedor para las burbujas #estilos-canvas');
      if (retryButton) retryButton.style.display = 'block';
      return;
    }
    
    // Limpiar cualquier contenido previo
    estilosCanvas.innerHTML = '';
    if (retryButton) estilosCanvas.appendChild(retryButton);
    
    // Inicializar con un pequeño retraso
    setTimeout(() => {
      try {
        initBubbles('estilos');
        // Configurar eventos de la interfaz
        setupEventListeners();
        console.log("MagneticBubbles inicializado correctamente");
      } catch (error) {
        console.error("Error al inicializar burbujas:", error);
        if (retryButton) retryButton.style.display = 'block';
      }
    }, 200);
    
  } catch (error) {
    console.error("Error al inicializar MagneticBubbles:", error);
    const retryButton = document.getElementById('retry-button');
    if (retryButton) retryButton.style.display = 'block';
  }
}

// Inicializar las burbujas para una pregunta específica
function initBubbles(type) {
  console.log(`Inicializando burbujas para tipo: ${type}`);
  
  // Obtener el canvas adecuado
  const canvasId = `${type}-canvas`;
  const canvasElement = document.getElementById(canvasId);
  
  if (!canvasElement) {
    console.error(`Error: Canvas element "${canvasId}" no encontrado`);
    return;
  }
  
  console.log(`Canvas encontrado: ${canvasId}`, canvasElement);
  activeCanvas = type;
  
  try {
    // Determinar los datos a usar
    let items = [];
    if (type === 'estilos') {
      items = window.estilos || estilos || [
        "Deportiva", "Naked", "Adventure", "Cruiser", "Touring", 
        "Scooter", "Custom", "Trail", "Enduro", "Clásica"
      ];
    } else if (type === 'marcas') {
      items = window.marcas || marcas || [
        "Honda", "Yamaha", "Kawasaki", "Suzuki", "BMW", "KTM", 
        "Ducati", "Triumph", "Harley-Davidson", "Royal Enfield", 
        "Aprilia", "Vespa", "Moto Guzzi", "Indian", "Husqvarna"
      ];
    }
    
    console.log(`Usando ${items.length} elementos para ${type}:`, items);
    
    if (!window.MagneticBubbles) {
      console.error('Error: La clase MagneticBubbles no está disponible en el scope global');
      return;
    }    // Crear instancia de MagneticBubbles
    bubbleInstances[type] = new MagneticBubbles(canvasId, items, {
      minRadius: 40,              // Burbujas más grandes (era 30)
      maxRadius: 65,              // Burbujas más grandes (era 55)
      padding: 15,                // Espacio entre burbujas
      repulsionForce: 0.15,       // Fuerza de repulsión optimizada
      dampening: 0.9,             // Amortiguación para movimiento fluido
      attractionForce: 0,         // Sin atracción al centro
      initialImpulse: 1.5,        // Impulso inicial moderado
      textFont: '14px Arial, sans-serif', // Texto más grande para mejor legibilidad
      colorPalette: [             // Paleta de colores: gris para todas
        '#707070', '#707070', '#707070', '#707070', '#707070',
        '#707070', '#707070', '#707070', '#707070', '#707070'
      ]
    });
    
    // Configurar evento para capturar selecciones
    canvasElement.addEventListener('selection-changed', (e) => {
      const selections = e.detail.selections;
      window.respuestas[type] = selections;
      console.log(`Selecciones de ${type} actualizadas:`, selections);
    });
    
    console.log(`Burbujas de ${type} inicializadas correctamente`);
    
  } catch (error) {
    console.error(`Error al inicializar las burbujas de ${type}:`, error);
  }
}

// Reinicializar burbujas para una pregunta
function reinitBubbles(type) {
  cleanupAndInitializeBubbles(type)
    .then(() => console.log(`Burbujas de ${type} reinicializadas correctamente`))
    .catch(error => console.error(`Error al reinicializar burbujas de ${type}:`, error));
}

// Helper para limpiar y reinicializar burbujas de forma estandarizada
function cleanupAndInitializeBubbles(type) {
  // Destruir instancia existente
  if (bubbleInstances[type]) {
    bubbleInstances[type].destroy();
    delete bubbleInstances[type];
  }
  
  // Limpiar el contenedor antes de reinicializar
  const canvasContainer = document.getElementById(`${type}-canvas`);
  if (canvasContainer) {
    // Solo conservar el botón de reintentar si existe
    const retryButton = canvasContainer.querySelector('#retry-button');
    canvasContainer.innerHTML = '';
    if (retryButton) canvasContainer.appendChild(retryButton);
  }
  
  // Inicializar con un retraso para asegurar que el DOM esté listo
  return new Promise(resolve => {
    setTimeout(() => {
      initBubbles(type);
      resolve();
    }, 500);
  });
}

// Aplicar impulso a las burbujas
function applyImpulseToBubbles(type, strength = 1.0) {
  if (bubbleInstances[type] && typeof bubbleInstances[type].applyImpulse === 'function') {
    try {
      bubbleInstances[type].applyImpulse(strength);
      console.log(`Impulso aplicado a las burbujas de ${type} con fuerza ${strength}`);
    } catch (error) {
      console.error(`Error al aplicar impulso a las burbujas de ${type}:`, error);
    }
  } else {
    console.warn(`No se puede aplicar impulso: no existe instancia para ${type} o no tiene método applyImpulse`);
  }
}

// Configurar eventos en la interfaz
function setupEventListeners() {
  // Configurar botones de navegación
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  
  if (prevBtn) {
    prevBtn.addEventListener('click', navigatePrev);
  }
  
  if (nextBtn) {
    nextBtn.addEventListener('click', navigateNext);
  }
  
  // Botón para reiniciar las burbujas
  const resetBtn = document.getElementById('reset-bubbles');
  if (resetBtn) {
    resetBtn.addEventListener('click', function() {
      if (activeCanvas && bubbleInstances[activeCanvas]) {
        bubbleInstances[activeCanvas].resetSelections();
        bubbleInstances[activeCanvas].applyImpulse(1.0);
      }
    });
  }
  
  // Evento en cambio de ventana para redimensionar
  window.addEventListener('resize', () => {
    if (activeCanvas && bubbleInstances[activeCanvas]) {
      // El componente MagneticBubbles maneja esto internamente
      console.log('Ventana redimensionada, el componente se ajustará automáticamente');
    }
  });
}

// Navegación a pregunta anterior
function navigatePrev() {
  const currentQuestion = document.querySelector('.pregunta.active');
  if (!currentQuestion) return;
  
  // Obtener el número de pregunta actual
  const currentId = currentQuestion.id;
  const match = currentId.match(/pregunta-(\d+)(?:-(\w+))?/);
  
  if (!match) return;
  
  let questionNum = parseInt(match[1]);
  const questionType = match[2]; // 'inexperto' o 'experto' o undefined
  
  // Guardar respuesta actual si hay select
  saveCurrentResponse(currentQuestion);
  
  // Ocultar pregunta actual
  currentQuestion.classList.remove('active');
  currentQuestion.style.display = 'none';
  
  let prevQuestionId;
  
  // Lógica para encontrar la pregunta anterior
  if (questionType) {
    // Estamos en una rama específica
    if (questionNum > 4) {
      // Ir a la pregunta anterior en la misma rama
      prevQuestionId = `pregunta-${questionNum-1}-${questionType}`;
    } else {
      // Volver a la pregunta 3 (experiencia)
      prevQuestionId = 'pregunta-3';
    }
  } else {
    // Preguntas iniciales 1-3
    if (questionNum > 1) {
      prevQuestionId = `pregunta-${questionNum-1}`;
    }
  }
    // Mostrar pregunta anterior
  if (prevQuestionId) {
    const prevQuestion = document.getElementById(prevQuestionId);
    if (prevQuestion) {
      prevQuestion.classList.add('active');
      prevQuestion.style.display = 'block';
        // Reinicializar burbujas según la pregunta
      if (prevQuestionId === 'pregunta-1') {
        cleanupAndInitializeBubbles('estilos');
      } else if (prevQuestionId === 'pregunta-2') {
        cleanupAndInitializeBubbles('marcas');
      }
    }
  }
    // Actualizar estado del botón anterior
  document.getElementById('prev-btn').disabled = (prevQuestionId === 'pregunta-1');
  
  // Actualizar barra de progreso
  updateProgressBar(questionNum - 1);
}

// Navegación a siguiente pregunta
function navigateNext() {
  const currentQuestion = document.querySelector('.pregunta.active');
  if (!currentQuestion) return;
  
  // Obtener el número de pregunta actual
  const currentId = currentQuestion.id;
  const match = currentId.match(/pregunta-(\d+)(?:-(\w+))?/);
  
  if (!match) return;
  
  let questionNum = parseInt(match[1]);
  const questionType = match[2]; // 'inexperto' o 'experto' o undefined
  
  // Guardar respuesta actual
  saveCurrentResponse(currentQuestion);
  
  // Ocultar pregunta actual
  currentQuestion.classList.remove('active');
  currentQuestion.style.display = 'none';
  
  let nextQuestionId;
  
  // Encontrar la siguiente pregunta según el flujo
  if (questionNum === 3) {
    // Ramificación según nivel de experiencia
    const experienciaSelect = document.getElementById('experiencia');
    const path = experienciaSelect.value === 'experto' ? 'experto' : 'inexperto';
    nextQuestionId = `pregunta-4-${path}`;
  } else if (questionType) {
    // Seguimos en una rama específica
    const maxQuestion = questionType === 'experto' ? 9 : 7;
    
    if (questionNum < maxQuestion) {
      nextQuestionId = `pregunta-${questionNum+1}-${questionType}`;
    } else {
      // Final del test
      showCompletionModal();
      return;
    }  } else {
    // Preguntas iniciales 1-3
    if (questionNum < 3) {
      nextQuestionId = `pregunta-${questionNum+1}`;      // Si pasamos a la pregunta 2, inicializar burbujas de marcas
      if (questionNum + 1 === 2) {
        cleanupAndInitializeBubbles('marcas');
      }
    }
  }
  
  // Mostrar siguiente pregunta
  if (nextQuestionId) {
    const nextQuestion = document.getElementById(nextQuestionId);
    if (nextQuestion) {
      nextQuestion.classList.add('active');
      nextQuestion.style.display = 'block';
    }
  }
  
  // Habilitar botón anterior
  document.getElementById('prev-btn').disabled = false;
  
  // Actualizar barra de progreso
  updateProgressBar();
}

// Guardar respuesta actual
function saveCurrentResponse(question) {
  // Guardar selección actual del select si existe
  const select = question.querySelector('select');
  if (select && select.id) {
    window.respuestas[select.id] = select.value;
    console.log(`Guardando respuesta: ${select.id} = ${select.value}`);
  }
}

// Actualizar barra de progreso
function updateProgressBar(questionNum) {
  const progressBar = document.getElementById('progress-bar');
  if (!progressBar) return;
  
  if (!questionNum) {
    const currentQuestion = document.querySelector('.pregunta.active');
    if (!currentQuestion) return;
    
    const currentId = currentQuestion.id;
    const match = currentId.match(/pregunta-(\d+)(?:-(\w+))?/);
    
    if (!match) return;
    
    questionNum = parseInt(match[1]);
  }
  
  const questionType = document.querySelector('.pregunta.active')?.id.match(/pregunta-\d+(?:-(\w+))?/)?.[1];
  
  let totalQuestions, progress;
  
  if (questionType === 'experto') {
    totalQuestions = 9;
    // Ajustar para preguntas 1-3 comunes + 4-9 experto
    progress = questionNum <= 3 ? questionNum : 3 + (questionNum - 3);
  } else if (questionType === 'inexperto') {
    totalQuestions = 7;
    // Ajustar para preguntas 1-3 comunes + 4-7 inexperto
    progress = questionNum <= 3 ? questionNum : 3 + (questionNum - 3);
  } else {
    // Preguntas comunes 1-3
    totalQuestions = 9; // Usamos el más largo como referencia
    progress = questionNum;
  }
  
  const percentage = (progress / totalQuestions) * 100;
  progressBar.style.width = `${percentage}%`;
}

// Mostrar modal de finalización
function showCompletionModal() {
  const modal = document.getElementById('completion-modal');
  if (modal) {
    modal.style.display = 'flex';
    
    // Confetti effect
    launchConfetti();
  }
}

// Efecto de confeti
function launchConfetti() {
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '9999';
  document.body.appendChild(canvas);
  
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  const pieces = [];
  const numberOfPieces = 200;
  const colors = ['#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800', '#FF5722'];
  
  for (let i = 0; i < numberOfPieces; i++) {
    pieces.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height * -1,
      rotation: Math.random() * 360,
      size: Math.random() * (8 - 2) + 2,
      color: colors[Math.floor(Math.random() * colors.length)],
      velocity: {
        x: Math.random() * 6 - 3,
        y: Math.random() * 3 + 3
      }
    });
  }
  
  function update() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    pieces.forEach(piece => {
      piece.y += piece.velocity.y;
      piece.x += piece.velocity.x;
      piece.rotation += 2;
      
      if (piece.y > canvas.height) {
        piece.y = -piece.size;
        piece.x = Math.random() * canvas.width;
      }
      
      ctx.save();
      ctx.translate(piece.x, piece.y);
      ctx.rotate(piece.rotation * Math.PI / 180);
      ctx.fillStyle = piece.color;
      ctx.fillRect(-piece.size / 2, -piece.size / 2, piece.size, piece.size);
      ctx.restore();
    });
    
    requestAnimationFrame(update);
  }
  
  update();
  
  // Remover confeti después de 5 segundos
  setTimeout(() => {
    canvas.remove();
  }, 5000);
}

// Manejar envío del formulario al completar
window.finalizarTest = function() {
  // Recopilar todos los datos del test
  const testData = {
    // Datos de burbujas (estilos y marcas)
    estilos: window.testSelections.estilos || {},
    marcas: window.testSelections.marcas || {},
    
    // Datos de experiencia y rama correspondiente
    experiencia: document.getElementById('experiencia').value,
    
    // Datos comunes indistintamente de la rama
    uso: document.getElementById('experiencia').value === 'experto' 
      ? document.getElementById('uso_experto').value 
      : document.getElementById('uso').value,
    
    // Obtener el presupuesto del input numérico (más preciso)
    presupuesto: document.getElementById('presupuesto').value,
  };
  
  // Mostrar los datos en consola para debug
  console.log('Datos del test a enviar:', testData);
  
  // Enviar datos mediante fetch
  fetch('/guardar_test', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(testData)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Respuesta del servidor:', data);
    window.location.href = '/recomendaciones';
  })
  .catch(error => {
    console.error('Error al enviar datos:', error);
    alert('Error al procesar el test. Por favor intenta nuevamente.');
  });
};

// Función para guardar preferencias en la base de datos
async function guardarPreferenciasEnBD(datosTest) {
  try {
    // Crear FormData para enviar la solicitud
    const formData = new FormData();
    
    // Añadir datos de estilos
    formData.append('estilos', JSON.stringify(datosTest.estilos || {}));
    
    // Añadir datos de marcas
    formData.append('marcas', JSON.stringify(datosTest.marcas || {}));
    
    // Añadir experiencia
    formData.append('experiencia', datosTest.experiencia || 'Intermedio');
    
    // Otros datos relevantes del test
    if (datosTest.uso) formData.append('uso', datosTest.uso);
    if (datosTest.precio) formData.append('presupuesto', datosTest.precio);
    
    // Enviar solicitud al servidor
    const response = await fetch('/guardar-preferencias', {
      method: 'POST',
      body: formData
    });
    
    // Analizar respuesta
    const result = await response.json();
    
    return result;
  } catch (error) {
    console.error('Error al guardar preferencias:', error);
    return { success: false, message: error.message };
  }
}

// Exponer funciones globalmente
window.initBubbles = initBubbles;
window.initializeTest = initializeTest;
window.updateProgressBar = updateProgressBar;
window.reinitBubbles = reinitBubbles;
window.launchConfetti = launchConfetti;
window.cleanupAndInitializeBubbles = cleanupAndInitializeBubbles;
window.applyImpulseToBubbles = applyImpulseToBubbles;

// Función para recuperar el test si falla la inicialización
window.recuperarTest = function() {
  console.log("Intentando recuperar test...");
  
  // Verificar si existen los elementos necesarios
  const estilosCanvas = document.getElementById('estilos-canvas');
  
  if (!estilosCanvas) {
    console.error("No se encontró el contenedor para las burbujas");
    return false;
  }
  
  // Limpiar cualquier canvas o elemento existente
  estilosCanvas.innerHTML = '';
  
  // Reintentar inicialización
  try {
    // Asegurar disponibilidad de MagneticBubbles
    if (!window.MagneticBubbles) {
      console.error("MagneticBubbles no está disponible");
      return false;
    }
    
    // Inicializar burbujas manualmente
    if (typeof window.initBubbles === 'function') {
      window.initBubbles('estilos');
      return true;
    }
  } catch (error) {
    console.error("Error al recuperar test:", error);
  }
  
  return false;
};

// Nota: La inicialización ahora se maneja desde el HTML para garantizar el orden de carga
