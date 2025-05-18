/**
 * Script auxiliar para inicializar las burbujas manualmente en la página de test
 * Este script soluciona el problema del "Error al cargar" de las burbujas
 */

// Variables globales para mejor control de estado
let canvasEstilosInicializado = false;
let canvasMarcasInicializado = false;
let ultimoCanvasActivo = null;
let esperandoRedimension = false;

// Ejecutar inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  console.log("Verificando inicialización de burbujas...");
  
  // Realizar un diagnóstico del estado actual
  diagnosticarEstadoActual();
  
  // Esperar un momento para asegurar que todos los scripts estén cargados
  setTimeout(inicializarSiNecesario, 500);
  
  // Agregar listener para redimensionamiento de ventana con mejor control
  window.addEventListener('resize', manejarRedimensionamientoWindow);
  
  // Agregar listeners a los botones de navegación
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  
  if (prevBtn) {
    prevBtn.addEventListener('click', function() {
      setTimeout(function() {
        verificarYRestaurarCanvas('navegación-prev');
      }, 150);
    });
  }
  
  if (nextBtn) {
    nextBtn.addEventListener('click', function() {
      setTimeout(function() {
        verificarYRestaurarCanvas('navegación-next');
      }, 150);
    });
  }
  
  // Configurar verificaciones periódicas del estado de los canvas
  setInterval(verificarEstadoCanvas, 2000);
});

// Mostrar diagnóstico de estado actual
function diagnosticarEstadoActual() {
  console.log("--- DIAGNÓSTICO DE BURBUJAS ---");
  console.log("MagneticBubbles disponible:", typeof window.MagneticBubbles === 'function');
  
  // Verificar canvas de estilos
  const estilosCanvas = document.getElementById('estilos-canvas');
  console.log("Canvas de estilos:", estilosCanvas ? "Encontrado" : "No encontrado");
  if (estilosCanvas) {
    console.log("  Dimensiones:", estilosCanvas.clientWidth + "x" + estilosCanvas.clientHeight);
    console.log("  Estilo de visualización:", window.getComputedStyle(estilosCanvas).display);
    console.log("  Contiene canvas:", estilosCanvas.querySelector('canvas') ? "Sí" : "No");
  }
  
  // Verificar canvas de marcas
  const marcasCanvas = document.getElementById('marcas-canvas');
  console.log("Canvas de marcas:", marcasCanvas ? "Encontrado" : "No encontrado");
  if (marcasCanvas) {
    console.log("  Dimensiones:", marcasCanvas.clientWidth + "x" + marcasCanvas.clientHeight);
    console.log("  Estilo de visualización:", window.getComputedStyle(marcasCanvas).display);
    console.log("  Contiene canvas:", marcasCanvas.querySelector('canvas') ? "Sí" : "No");
  }
  
  // Verificar instancias globales
  console.log("Instancia estilosBubbles:", window.estilosBubbles ? "Existe" : "No existe");
  console.log("Instancia marcasBubbles:", window.marcasBubbles ? "Existe" : "No existe");
  
  console.log("--- FIN DIAGNÓSTICO ---");
}

// Función para verificar y restaurar canvas después de navegar
function verificarYRestaurarCanvas(origen) {
  const preguntaActiva = document.querySelector('.pregunta.active');
  if (!preguntaActiva) return;
  
  const id = preguntaActiva.id;
  console.log(`Verificando canvas después de ${origen} en ${id}`);
  
  if (id === 'pregunta-1') {
    const estilosCanvas = document.getElementById('estilos-canvas');
    if (!estilosCanvas) return;
    
    const hayCanvas = estilosCanvas.querySelector('canvas');
    if (!hayCanvas || !canvasEstilosInicializado) {
      console.log(`Canvas de estilos necesita reinicialización después de ${origen}`);
      inicializarSoloEstilos();
    } else {
      // Forzar redimensionamiento para evitar problemas visuales
      ajustarTamanoCanvas('estilos', estilosCanvas);
    }
    
    ultimoCanvasActivo = 'estilos';
  } 
  else if (id === 'pregunta-2') {
    const marcasCanvas = document.getElementById('marcas-canvas');
    if (!marcasCanvas) return;
    
    const hayCanvas = marcasCanvas.querySelector('canvas');
    if (!hayCanvas || !canvasMarcasInicializado) {
      console.log(`Canvas de marcas necesita reinicialización después de ${origen}`);
      inicializarSoloMarcas();
    } else {
      // Forzar redimensionamiento para evitar problemas visuales
      ajustarTamanoCanvas('marcas', marcasCanvas);
    }
    
    ultimoCanvasActivo = 'marcas';
  }
}

// Función para inicializar solo el canvas de estilos
function inicializarSoloEstilos() {
  const estilosCanvas = document.getElementById('estilos-canvas');
  if (!estilosCanvas) {
    console.error("No se encontró el contenedor para el canvas de estilos");
    return;
  }
  
  // Asegurarse de que el contenedor sea visible y tenga dimensiones
  estilosCanvas.style.display = 'block';
  estilosCanvas.style.minHeight = '300px';
  estilosCanvas.style.minWidth = '300px';
  
  // Guardar estado actual antes de reinicializar
  const estadoEstilos = (window.respuestas && window.respuestas.estilos) ? 
                         window.respuestas.estilos : {};
  
  // Opciones para estilos
  const opcionesEstilos = [
    { id: 'naked', label: 'Naked', value: 1.0 },
    { id: 'sport', label: 'Deportiva', value: 1.0 },
    { id: 'touring', label: 'Touring', value: 1.0 },
    { id: 'trail', label: 'Trail/Adventure', value: 1.0 },
    { id: 'scooter', label: 'Scooter', value: 1.0 },
    { id: 'custom', label: 'Custom/Cruiser', value: 1.0 }
  ];
  
  // Limpiar y reinicializar
  estilosCanvas.innerHTML = '';
  const bubbleInstance = inicializarBurbuja('estilos', estilosCanvas, opcionesEstilos);
  
  if (bubbleInstance) {
    canvasEstilosInicializado = true;
    
    // Restaurar selecciones previas con más robustez
    if (Object.keys(estadoEstilos).length > 0) {
      setTimeout(function() {
        // Asegurarse de tener los objetos globales
        window.respuestas = window.respuestas || {};
        window.testResults = window.testResults || {};
        
        // Restaurar selecciones tanto en respuestas como en testResults
        window.respuestas.estilos = estadoEstilos;
        window.testResults.estilos = estadoEstilos;
        
        // Intentar actualizar visualmente las selecciones en la instancia de burbujas
        try {
          if (bubbleInstance && typeof bubbleInstance.updateSelections === 'function') {
            bubbleInstance.updateSelections(estadoEstilos);
            console.log('Selecciones de estilos restauradas visualmente');
          }
        } catch (e) {
          console.warn('No se pudieron restaurar visualmente las selecciones de estilos:', e);
        }
      }, 200);
    }
  } else {
    console.error("No se pudo inicializar el canvas de estilos");
  }
  
  // Ocultar botón de reintentar si existe
  const retryButton = document.getElementById('retry-button');
  if (retryButton) {
    retryButton.style.display = 'none';
  }
}

// Función para inicializar solo el canvas de marcas
function inicializarSoloMarcas() {
  const marcasCanvas = document.getElementById('marcas-canvas');
  if (!marcasCanvas) {
    console.error("No se encontró el contenedor para el canvas de marcas");
    return;
  }
  
  // Asegurarse de que el contenedor sea visible y tenga dimensiones
  marcasCanvas.style.display = 'block';
  marcasCanvas.style.minHeight = '300px';
  marcasCanvas.style.minWidth = '300px';
  
  // Guardar estado actual antes de reinicializar
  const estadoMarcas = (window.respuestas && window.respuestas.marcas) ? 
                        window.respuestas.marcas : {};
  
  // Opciones para marcas
  const opcionesMarcas = [
    { id: 'honda', label: 'Honda', value: 1.0 },
    { id: 'yamaha', label: 'Yamaha', value: 1.0 },
    { id: 'suzuki', label: 'Suzuki', value: 1.0 },
    { id: 'kawasaki', label: 'Kawasaki', value: 1.0 },
    { id: 'ducati', label: 'Ducati', value: 1.0 },
    { id: 'bmw', label: 'BMW', value: 1.0 },
    { id: 'triumph', label: 'Triumph', value: 1.0 },
    { id: 'ktm', label: 'KTM', value: 1.0 }
  ];
  
  // Limpiar y reinicializar
  marcasCanvas.innerHTML = '';
  const bubbleInstance = inicializarBurbuja('marcas', marcasCanvas, opcionesMarcas);
  
  if (bubbleInstance) {
    canvasMarcasInicializado = true;
    
    // Restaurar selecciones previas con más robustez
    if (Object.keys(estadoMarcas).length > 0) {
      setTimeout(function() {
        // Asegurarse de tener los objetos globales
        window.respuestas = window.respuestas || {};
        window.testResults = window.testResults || {};
        
        // Restaurar selecciones tanto en respuestas como en testResults
        window.respuestas.marcas = estadoMarcas;
        window.testResults.marcas = estadoMarcas;
        
        // Intentar actualizar visualmente las selecciones en la instancia de burbujas
        try {
          if (bubbleInstance && typeof bubbleInstance.updateSelections === 'function') {
            bubbleInstance.updateSelections(estadoMarcas);
            console.log('Selecciones de marcas restauradas visualmente');
          }
        } catch (e) {
          console.warn('No se pudieron restaurar visualmente las selecciones de marcas:', e);
        }
      }, 200);
    }
  } else {
    console.error("No se pudo inicializar el canvas de marcas");
  }
  
  // Ocultar botón de reintentar si existe
  const retryButtonMarcas = document.getElementById('retry-button-marcas');
  if (retryButtonMarcas) {
    retryButtonMarcas.style.display = 'none';
  }
}

// Función para inicializar una burbuja específica
function inicializarBurbuja(tipo, contenedor, opciones) {
  if (!contenedor) {
    console.error(`Contenedor de ${tipo} no disponible`);
    return null;
  }
  
  // Verificar si MagneticBubbles está disponible
  if (typeof window.MagneticBubbles !== 'function') {
    console.error(`MagneticBubbles no está disponible como función al inicializar ${tipo}`);
    mostrarErrorEnCanvas(document.createElement('canvas'), "Error: Componente no disponible");
    
    // Intentar cargar el script de nuevo
    cargarScriptMagneticBubbles(function() {
      console.log("Script recargado, reintentando inicialización");
      setTimeout(() => inicializarBurbuja(tipo, contenedor, opciones), 200);
    });
    return null;
  }
  
  // Limpiar contenedor completamente antes de crear nuevo canvas
  contenedor.innerHTML = '';
  
  // Obtener dimensiones del contenedor
  let containerWidth = contenedor.clientWidth;
  let containerHeight = contenedor.clientHeight;
  
  // Asegurar dimensiones mínimas
  if (containerWidth < 300) containerWidth = 300;
  if (containerHeight < 300) containerHeight = 300;
  
  console.log(`Dimensiones del contenedor ${tipo}: ${containerWidth}x${containerHeight}`);
  
  // Crear nuevo canvas con dimensiones exactas del contenedor
  const canvas = document.createElement('canvas');
  canvas.id = `${tipo}-bubbles-canvas`;
  
  // Calcular la densidad de píxeles para mejorar la resolución
  const pixelRatio = window.devicePixelRatio || 1;
  
  // CRUCIAL: Configurar estilos para asegurar que los eventos lleguen al canvas
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.display = 'block';
  canvas.style.position = 'absolute';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.zIndex = '10'; // Asegurar que esté por encima
  canvas.style.touchAction = 'none';
  canvas.style.pointerEvents = 'auto'; // IMPORTANTE: permitir eventos de mouse
  
  // Preparar el contenedor y añadir el canvas - IMPORTANTE para interactividad
  contenedor.style.position = 'relative';
  contenedor.style.overflow = 'hidden';
  contenedor.style.pointerEvents = 'auto'; // Asegurar que el contenedor permita interacción
  contenedor.appendChild(canvas);
  
  // Ajustar dimensiones después de añadir al DOM
  setTimeout(() => {
    try {
      // Establecer dimensiones del canvas nativo con alta resolución
      canvas.width = containerWidth * pixelRatio;
      canvas.height = containerHeight * pixelRatio;
      
      console.log(`Canvas ${tipo} creado con dimensiones: ${canvas.width}x${canvas.height} (ratio: ${pixelRatio})`);
      
      // Configuraciones específicas según el tipo de burbuja
      let bubbleConfig = {
        items: opciones,
        selectionMode: 'multiple',
        canvasBackground: 'rgba(0, 0, 0, 0.8)', // Fondo oscuro consistente
        bubbleBaseColor: '#f97316',
        bubbleSelectedColor: '#ea580c',
        textColor: '#ffffff',
        width: containerWidth,
        height: containerHeight,
        pixelRatio: pixelRatio
      };
      
      // Ajustes específicos para las marcas (más burbujas, tamaño menor)
      if (tipo === 'marcas') {
        // Reducir tamaño de las burbujas para marcas (son más elementos)
        bubbleConfig.bubbleSizeFactor = 0.08; // Factor de tamaño más pequeño para marcas
        bubbleConfig.minDistance = 10; // Distancia mínima entre burbujas
        bubbleConfig.maxInitialVelocity = 2; // Velocidad inicial más baja para mejor control
        bubbleConfig.textScaleFactor = 0.8; // Texto ligeramente más pequeño
      } else {
        // Configuración para estilos (menos elementos, pueden ser más grandes)
        bubbleConfig.bubbleSizeFactor = 0.12; // Factor de tamaño normal para estilos
        bubbleConfig.textScaleFactor = 1.0; // Texto normal
      }
      
      // Crear instancia de burbujas
      const bubbleInstance = new window.MagneticBubbles(canvas, bubbleConfig);
      
      // Guardar referencia global para acceso fácil
      window[`${tipo}Bubbles`] = bubbleInstance;
      
      // IMPORTANTE: Verificar que se pueda hacer clic en el canvas
      canvas.addEventListener('click', function(e) {
        console.log(`Clic detectado en canvas de ${tipo}`);
      });
      
      // Configurar evento de selección
      canvas.addEventListener('selection-changed', function(e) {
        // Guardar selecciones en objeto global respuestas
        window.respuestas = window.respuestas || {};
        window.respuestas[tipo] = e.detail.selections;
        
        // Importante: También almacenar en testResults inmediatamente
        window.testResults = window.testResults || {};
        window.testResults[tipo] = e.detail.selections;
        
        console.log(`Selecciones de ${tipo} actualizadas:`, e.detail.selections);
        
        // Actualizar panel de depuración si existe
        if (typeof window.updateDebugPanel === 'function') {
          window.updateDebugPanel();
        }
      });
      
      console.log(`Burbujas de ${tipo} inicializadas correctamente`);
      
      return bubbleInstance;
    } catch (error) {
      console.error(`Error al inicializar burbujas para ${tipo}:`, error);
      mostrarErrorEnCanvas(canvas, "Error: " + error.message);
      return null;
    }
  }, 0);
  
  // Retornar null temporalmente - la instancia real se creará en el setTimeout
  return null;
}

// Verificar si las burbujas necesitan inicialización y en ese caso inicializarlas
function inicializarSiNecesario() {
  console.log("Comprobando si las burbujas están inicializadas...");
  
  // Verificar si MagneticBubbles está disponible
  if (typeof window.MagneticBubbles !== 'function') {
    console.error("ERROR CRÍTICO: MagneticBubbles no está definido. Intentando cargar manualmente...");
    cargarScriptMagneticBubbles(function() {
      inicializarBurbujasManuales();
    });
    return;
  }
  
  // Siempre inicializar ambos canvas para asegurar que estén disponibles
  inicializarBurbujasManuales();
}

// Cargar el script de MagneticBubbles manualmente si es necesario
function cargarScriptMagneticBubbles(callback) {
  const script = document.createElement('script');
  script.src = "/static/js/magnetic-bubbles.js?v=" + new Date().getTime(); // Evitar caché
  script.onload = function() {
    console.log("Script de MagneticBubbles cargado manualmente");
    if (callback) callback();
  };
  script.onerror = function() {
    console.error("Error al cargar MagneticBubbles manualmente");
  };
  document.head.appendChild(script);
}

// Inicialización manual de las burbujas (inicializa ambos canvas)
function inicializarBurbujasManuales() {
  console.log("Inicializando burbujas manualmente...");
  
  // Inicializar estilos si existe el contenedor
  const estilosCanvas = document.getElementById('estilos-canvas');
  if (estilosCanvas) {
    inicializarSoloEstilos();
  }
  
  // Inicializar marcas si existe el contenedor
  const marcasCanvas = document.getElementById('marcas-canvas');
  if (marcasCanvas) {
    inicializarSoloMarcas();
  }
  
  // Actualizar el panel de debug si existe
  if (typeof window.updateDebugPanel === 'function') {
    window.updateDebugPanel();
  }
}

// Función para manejar redimensionamiento de ventana con protección contra llamadas múltiples
function manejarRedimensionamientoWindow() {
  if (esperandoRedimension) return;
  
  esperandoRedimension = true;
  setTimeout(function() {
    console.log("Ventana redimensionada, ajustando canvas actualmente visible...");
    
    // Determinar qué canvas está actualmente visible
    const pregunta1 = document.getElementById('pregunta-1');
    const pregunta2 = document.getElementById('pregunta-2');
    
    if (pregunta1 && pregunta1.classList.contains('active')) {
      const estilosCanvas = document.getElementById('estilos-canvas');
      if (estilosCanvas) {
        ajustarTamanoCanvas('estilos', estilosCanvas);
      }
    } else if (pregunta2 && pregunta2.classList.contains('active')) {
      const marcasCanvas = document.getElementById('marcas-canvas');
      if (marcasCanvas) {
        ajustarTamanoCanvas('marcas', marcasCanvas);
      }
    }
    
    esperandoRedimension = false;
  }, 300);
}

/**
 * Ajusta el tamaño del canvas con manejo mejorado para zoom y redimensionamiento
 */
function ajustarTamanoCanvas(tipo, canvasElement) {
  if (!canvasElement) return false;
  
  // Capturar dimensiones del contenedor padre
  const container = canvasElement.parentElement;
  if (!container) return false;
  
  const rect = container.getBoundingClientRect();
  let width = rect.width;
  let height = rect.height;
  
  // Asegurar dimensiones mínimas para evitar desaparición
  width = Math.max(width, 300);  // mínimo 300px de ancho
  height = Math.max(height, 300); // mínimo 300px de alto
  
  console.log(`Ajustando canvas ${tipo} a: ${width}x${height}`);
  
  // Establecer dimensiones del canvas
  canvasElement.width = width;
  canvasElement.height = height;
  
  // También establecer dimensiones vía CSS para mantener consistencia
  canvasElement.style.width = width + 'px';
  canvasElement.style.height = height + 'px';
  
  return true;
}

/**
 * Función mejorada para redimensionar canvas de burbujas
 */
function redimensionarCanvasBurbujas() {
  console.log("Ejecutando redimensionarCanvasBurbujas");
  const estilosCanvas = document.getElementById('estilos-canvas');
  const marcasCanvas = document.getElementById('marcas-canvas');
  
  // Guardar el estado actual de las burbujas
  let estadoEstilos = null;
  let estadoMarcas = null;
  
  if (window.estilosBubbles && typeof window.estilosBubbles.getSelections === 'function') {
    estadoEstilos = window.estilosBubbles.getSelections();
    console.log("Estado estilos guardado:", estadoEstilos);
  }
  
  if (window.marcasBubbles && typeof window.marcasBubbles.getSelections === 'function') {
    estadoMarcas = window.marcasBubbles.getSelections();
    console.log("Estado marcas guardado:", estadoMarcas);
  }
  
  // Inicializar canvas visibles según la pestaña activa
  const pregunta1 = document.getElementById('pregunta-1');
  const pregunta2 = document.getElementById('pregunta-2');
  
  if (pregunta1 && pregunta1.classList.contains('active') && estilosCanvas) {
    console.log("Reinicializando canvas de estilos por redimensión");
    // Reiniciar el canvas completamente
    estilosCanvas.innerHTML = '';
    
    if (ajustarTamanoCanvas('estilos', estilosCanvas)) {
      inicializarSoloEstilos();
      
      // Restaurar estado después de inicializar
      if (estadoEstilos && Object.keys(estadoEstilos).length > 0) {
        setTimeout(() => {
          try {
            if (window.estilosBubbles && typeof window.estilosBubbles.updateSelections === 'function') {
              window.estilosBubbles.updateSelections(estadoEstilos);
              console.log("Selecciones de estilos restauradas después de redimensionar");
            }
          } catch (e) {
            console.error("Error al restaurar selecciones de estilos:", e);
          }
        }, 200);
      }
    }
  }
  
  if (pregunta2 && pregunta2.classList.contains('active') && marcasCanvas) {
    console.log("Reinicializando canvas de marcas por redimensión");
    // Reiniciar el canvas completamente
    marcasCanvas.innerHTML = '';
    
    if (ajustarTamanoCanvas('marcas', marcasCanvas)) {
      inicializarSoloMarcas();
      
      // Restaurar estado después de inicializar
      if (estadoMarcas && Object.keys(estadoMarcas).length > 0) {
        setTimeout(() => {
          try {
            if (window.marcasBubbles && typeof window.marcasBubbles.updateSelections === 'function') {
              window.marcasBubbles.updateSelections(estadoMarcas);
              console.log("Selecciones de marcas restauradas después de redimensionar");
            }
          } catch (e) {
            console.error("Error al restaurar selecciones de marcas:", e);
          }
        }, 200);
      }
    }
  }
}

// Agregar detección mejorada de zoom del navegador
(function() {
  let lastWidth = window.innerWidth;
  let lastHeight = window.innerHeight;
  
  // Verificar cambios de tamaño de ventana que podrían indicar zoom
  function checkZoom() {
    const widthChange = Math.abs(lastWidth - window.innerWidth);
    const heightChange = Math.abs(lastHeight - window.innerHeight);
    
    // Si el cambio es significativo, podría ser zoom o rotación del dispositivo
    if (widthChange > 20 || heightChange > 20) {
      console.log("Cambio significativo de dimensiones detectado, posible zoom");
      setTimeout(redimensionarCanvasBurbujas, 300);
      
      // Actualizar dimensiones de referencia
      lastWidth = window.innerWidth;
      lastHeight = window.innerHeight;
    }
  }
  
  // Escuchar eventos relevantes para detectar cambios
  window.addEventListener('resize', debounce(checkZoom, 200));
  window.addEventListener('orientationchange', function() {
    setTimeout(redimensionarCanvasBurbujas, 500);
  });
  
  // Función de debounce para evitar múltiples llamadas rápidas
  function debounce(func, wait) {
    let timeout;
    return function() {
      const context = this, args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), wait);
    };
  }
})();

// Funciones de recuperación para casos en que las burbujas no se inicialicen correctamente
window.recuperarTest = function() {
  console.log("Ejecutando recuperación de test...");
  inicializarBurbujasManuales();
};

console.log("Script de recuperación de burbujas cargado correctamente");
