/**
 * Script auxiliar para inicializar las burbujas manualmente en la página de test
 * Este script soluciona el problema del "Error al cargar" de las burbujas
 */

// Ejecutar inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  console.log("Verificando inicialización de burbujas...");
  // Esperar un momento para asegurar que todos los scripts estén cargados
  setTimeout(inicializarSiNecesario, 1500);
});

// Funciones de recuperación para casos en que las burbujas no se inicialicen correctamente
window.recuperarTest = function() {
  console.log("Ejecutando recuperación de test...");
  inicializarBurbujasManuales();
};

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
  
  // Verificar si los contenedores de burbujas existen
  const estilosCanvas = document.getElementById('estilos-canvas');
  const marcasCanvas = document.getElementById('marcas-canvas');
  
  if (!estilosCanvas || !marcasCanvas) {
    console.error("No se encontraron los contenedores para las burbujas");
    return;
  }
  
  // Verificar si ya hay canvas de burbujas inicializados
  const estilosInicializado = estilosCanvas.querySelector('canvas');
  const marcasInicializado = marcasCanvas.querySelector('canvas');
  
  if (!estilosInicializado || !marcasInicializado) {
    console.warn("Burbujas no inicializadas correctamente. Iniciando recuperación...");
    inicializarBurbujasManuales();
  } else {
    console.log("Las burbujas parecen estar correctamente inicializadas");
  }
}

// Cargar el script de MagneticBubbles manualmente si es necesario
function cargarScriptMagneticBubbles(callback) {
  const script = document.createElement('script');
  script.src = "/static/js/magnetic-bubbles.js?v=" + new Date().getTime();
  script.onload = function() {
    console.log("Script de MagneticBubbles cargado manualmente");
    if (callback) callback();
  };
  script.onerror = function() {
    console.error("Error al cargar MagneticBubbles manualmente");
  };
  document.head.appendChild(script);
}

// Inicialización manual de las burbujas
function inicializarBurbujasManuales() {
  console.log("Inicializando burbujas manualmente...");
  
  // Opciones para estilos
  const opcionesEstilos = [
    { id: 'naked', label: 'Naked', value: 1.0 },
    { id: 'sport', label: 'Deportiva', value: 1.0 },
    { id: 'touring', label: 'Touring', value: 1.0 },
    { id: 'trail', label: 'Trail/Adventure', value: 1.0 },
    { id: 'scooter', label: 'Scooter', value: 1.0 },
    { id: 'custom', label: 'Custom/Cruiser', value: 1.0 }
  ];
  
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
  
  // Inicializar objeto de respuestas global si no existe
  window.respuestas = window.respuestas || {
    estilos: {},
    marcas: {}
  };
  
  // Limpiar contenedores existentes
  const estilosCanvas = document.getElementById('estilos-canvas');
  const marcasCanvas = document.getElementById('marcas-canvas');
  
  if (estilosCanvas) {
    estilosCanvas.innerHTML = '';
    inicializarBurbuja('estilos', estilosCanvas, opcionesEstilos);
  }
  
  if (marcasCanvas) {
    marcasCanvas.innerHTML = '';
    inicializarBurbuja('marcas', marcasCanvas, opcionesMarcas);
  }
  
  // Ocultar botón de reintentar si existe
  const retryButton = document.getElementById('retry-button');
  if (retryButton) {
    retryButton.style.display = 'none';
  }
  
  // Actualizar el panel de debug si existe
  if (typeof window.updateDebugPanel === 'function') {
    window.updateDebugPanel();
  }
}

// Función para inicializar una burbuja específica
function inicializarBurbuja(tipo, contenedor, opciones) {
  // Limpiar contenedor completamente antes de crear nuevo canvas
  contenedor.innerHTML = '';
  
  // Crear nuevo canvas con dimensiones adecuadas
  const canvas = document.createElement('canvas');
  canvas.id = `${tipo}-bubbles-canvas`;
  canvas.width = contenedor.clientWidth || 300;
  canvas.height = contenedor.clientHeight || 400;
  contenedor.appendChild(canvas);
  
  console.log(`Creando burbujas para ${tipo}... (Canvas: ${canvas.width}x${canvas.height})`);
  
  try {
    // Verificar si MagneticBubbles está disponible
    if (typeof window.MagneticBubbles !== 'function') {
      console.error(`MagneticBubbles no está disponible como función al inicializar ${tipo}`);
      mostrarErrorEnCanvas(canvas, "Error: Componente no disponible");
      
      // Intentar cargar el script de nuevo
      cargarScriptMagneticBubbles(function() {
        console.log("Script recargado, reintentando inicialización");
        inicializarBurbuja(tipo, contenedor, opciones);
      });
      return;
    }
    
    // Crear instancia de burbujas con opciones mejoradas
    const bubbleInstance = new window.MagneticBubbles(canvas, {
      items: opciones,
      selectionMode: 'multiple',
      canvasBackground: 'rgba(26, 26, 26, 0.2)', // Mayor contraste para mejor visibilidad
      bubbleBaseColor: '#f97316',
      bubbleSelectedColor: '#ea580c',
      width: canvas.width,
      height: canvas.height
    });
    
    // Guardar referencia global para acceso fácil
    window[`${tipo}Bubbles`] = bubbleInstance;
    
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
    
    // Verificar que la instancia tenga los métodos esperados
    if (!bubbleInstance.getSelections || !bubbleInstance.updateSelections) {
      console.warn(`La instancia de burbujas ${tipo} no tiene todos los métodos esperados`);
    }
    
    return bubbleInstance;
  } catch (error) {
    console.error(`Error al inicializar burbujas para ${tipo}:`, error);
    mostrarErrorEnCanvas(canvas, "Error: " + error.message);
    return null;
  }
}

// Función para mostrar error en el canvas
function mostrarErrorEnCanvas(canvas, mensaje) {
  try {
    const ctx = canvas.getContext('2d');
    if (ctx) {
      // Fondo
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Texto de error
      ctx.fillStyle = '#f97316';
      ctx.font = 'bold 16px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(mensaje, canvas.width/2, canvas.height/2);
      ctx.fillText('Haz clic para reintentar', canvas.width/2, canvas.height/2 + 30);
      
      // Hacer que el canvas sea clickeable para reintentar
      canvas.style.cursor = 'pointer';
      canvas.addEventListener('click', window.recuperarTest);
    }
  } catch (e) {
    console.error('Error al mostrar mensaje de error en canvas:', e);
  }
}

// Comprobar MagneticBubbles cada segundo para asegurar su disponibilidad
// Contadores e intervalos para comprobación proactiva
let comprobacionesRealizadas = 0;
let inicializacionesIntentos = 0;
const MAX_INTENTOS = 5;

// Verificación más agresiva para asegurar que las burbujas estén disponibles
const intervalComprobacion = setInterval(function() {
  comprobacionesRealizadas++;
  
  // Comprobar si MagneticBubbles está disponible
  if (typeof window.MagneticBubbles === 'function') {
    console.log("MagneticBubbles está disponible después de " + comprobacionesRealizadas + " comprobaciones");
    
    // Comprobar si las burbujas están inicializadas
    const estilosCanvas = document.getElementById('estilos-canvas');
    const hayCanvas = estilosCanvas && estilosCanvas.querySelector('canvas');
    
    if (!hayCanvas) {
      console.log("MagneticBubbles disponible pero burbujas no inicializadas. Ejecutando inicialización manual...");
      inicializarBurbujasManuales();
    } else {
      // Verificar que las burbujas estén funcionando correctamente
      const estilosFuncionales = window.estilosBubbles && typeof window.estilosBubbles.getSelections === 'function';
      if (!estilosFuncionales) {
        console.warn("Las burbujas existen pero no parecen funcionales. Reinicializando...");
        inicializarBurbujasManuales();
      } else {
        console.log("Burbujas verificadas y funcionales");
        clearInterval(intervalComprobacion);
      }
    }
  } else if (comprobacionesRealizadas >= 3) { // Reducir a 3 para ser más proactivos
    // Después de 3 intentos, intentar cargar el script manualmente
    console.error("MagneticBubbles sigue sin estar disponible. Intentando cargar el script manualmente...");
    cargarScriptMagneticBubbles(function() {
      inicializarBurbujasManuales();
      clearInterval(intervalComprobacion);
    });
  }
  
  // Limitar el número total de comprobaciones
  if (comprobacionesRealizadas >= 10) {
    console.warn("Demasiados intentos de comprobación. Parando verificación automática.");
    clearInterval(intervalComprobacion);
  }
}, 800); // Reducir a 800ms para ser más ágil

console.log("Script de recuperación de burbujas cargado y activo");
