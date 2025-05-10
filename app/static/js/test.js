// Datos
const estilos = ["cross", "custom", "eléctrica", "enduro", "infantil", "naked", "quad-atv", "scooter", "sport", "supermotard", "trail", "trial", "turismo"];
const marcas = ["AJP", "Adiva", "Aeon", "Alpina", "Aprilia", "Artemisa", "Astra", "Bajaj", "Benda", "Beta", "BH", "Bimoto", "BMW", "Brixton", "Bullit", "CFMoto", "Cleveland CycleWerks", "Ducati", "Energica", "GasGas", "Gilera", "Honda", "Husqvarna", "Indian", "Jawa", "Kawasaki", "KTM", "Kymco", "Lambretta", "Lifan", "Macbor", "Mash", "MCI", "Moto Morini", "Moto Guzzi", "Motron", "MV Agusta", "Neoway", "Norton", "Peugeot", "Piaggio", "Polaris", "Qooder", "Rieju", "Royal Enfield", "Sherco", "Suzuki", "SYM", "Tesla", "Triumph", "UM Motorcycles", "Urbet", "Vectrix", "Vespa", "Victory", "Voge", "Volta", "Vässla", "Wottan", "Xero", "Yadea", "Yamaha", "Zero Motorcycles", "Zitmuv", "Zontes"];

// Configuración del sistema de preguntas
let currentPregunta = 1;
const totalPreguntas = 10;
const respuestas = {
  estilos: {},
  marcas: {},
  uso: "",
  experiencia: "",
  cilindrada: "",
  año: "",
  potencia: "",
  torque: "",
  peso: "",
  presupuesto: ""
};

// Asegurarse de que Matter.js está disponible
if (typeof Matter === 'undefined') {
  console.error('Matter.js no está cargado correctamente');
}

// Inicializar motores físicos Matter.js - SOLO UNA VEZ
const Engine = Matter.Engine;
const Render = Matter.Render;
const World = Matter.World;
const Bodies = Matter.Bodies;
const Body = Matter.Body;
const Events = Matter.Events;
const Mouse = Matter.Mouse;
const MouseConstraint = Matter.MouseConstraint;

// Configurar física - UN SOLO MOTOR para todo
const engine = Engine.create({
  gravity: { x: 0, y: 0 }, // Sin gravedad para que floten
  enableSleeping: false // Mantener activos los cuerpos siempre
});
const world = engine.world;

// Objetos para rastrear círculos
const circulos = {
  estilos: [],
  marcas: []
};

// Configuración inicial de los renders
const renders = {};
let canvasDivs = {};

// Configuración de tamaño según el nivel de selección
const tamañoPorNivel = {
  0: 1.0, // Tamaño normal (no seleccionado)
  1: 1.3, // Nivel 1 (me gusta)
  2: 1.4, // Me gusta
  3: 1.6, // me gusta mucho
  4: 1.8  // me encanta
};

// Colores base
const colorPrincipal = '#f97316'; // Naranja principal

// Función para inicializar los canvasDivs
function inicializarCanvasDivs() {
  canvasDivs = {
    estilos: document.getElementById('estilos-canvas'),
    marcas: document.getElementById('marcas-canvas')
  };
  
  // Verificar que existen los elementos
  if (!canvasDivs.estilos) {
    console.error('El elemento con ID "estilos-canvas" no existe');
    return false;
  }
  
  if (!canvasDivs.marcas) {
    console.error('El elemento con ID "marcas-canvas" no existe');
    return false;
  }
  
  console.log('Canvas divs inicializados correctamente:');
  console.log('estilos-canvas:', canvasDivs.estilos);
  console.log('marcas-canvas:', canvasDivs.marcas);
  
  return true;
}  // Inicializar renders para cada canvas
function inicializarRenders() {
  if (!inicializarCanvasDivs()) return;
  
  Object.keys(canvasDivs).forEach(key => {
    const canvasDiv = canvasDivs[key];
    
    // Verificar si ya existe un render para este canvas
    if (renders[key] && renders[key].canvas) {
      // Limpiar el render existente
      Render.stop(renders[key]);
      canvasDiv.innerHTML = '';
    }
    
    // Obtener dimensiones del canvas
    const width = canvasDiv.clientWidth || canvasDiv.offsetWidth || 800;
    const height = canvasDiv.clientHeight || canvasDiv.offsetHeight || 400;
    
    console.log(`Dimensiones del div ${key}: ${width}x${height}`);
    
    // Crear render
    renders[key] = Render.create({
      element: canvasDiv,
      engine: engine,
      options: {
        width: width,
        height: height,
        wireframes: false,
        background: 'transparent',
        pixelRatio: window.devicePixelRatio || 1
      }
    });
    
    console.log(`Render creado para ${key} con dimensiones: ${renders[key].options.width}x${renders[key].options.height}`);
    
    // Inicialmente detenemos los renders, se activarán cuando sea necesario
    Render.run(renders[key]);
    
    // Asegurarse de que el canvas tenga el estilo correcto para recibir eventos
    if (renders[key].canvas) {
      renders[key].canvas.style.width = '100%';
      renders[key].canvas.style.height = '100%';
    }
  });
}


// Función para crear círculos aleatorios - VERSIÓN MODIFICADA
function crearCirculos(tipo, lista) {
  console.log(`Iniciando creación de círculos para ${tipo}`);
  if (!canvasDivs[tipo]) {
    console.error(`Canvas para ${tipo} no encontrado`);
    return;
  }

  const canvas = canvasDivs[tipo];
  const width = canvas.offsetWidth || 800;
  const height = canvas.offsetHeight || 400;
  
  console.log(`Canvas dimensiones: ${width}x${height}`);

  // Limpiar TODOS los cuerpos del mundo antes de crear nuevos
  World.clear(world, false);
  
  // Reiniciar la lista de círculos para este tipo
  circulos[tipo] = [];

  // Limpiar el canvas para evitar residuos
  if (renders[tipo] && renders[tipo].canvas) {
    const ctx = renders[tipo].context;
    ctx.clearRect(0, 0, renders[tipo].canvas.width, renders[tipo].canvas.height);
  }

  // Determinar radio basado en el número de elementos
  const minRadius = 25;
  const maxRadius = 35;

  // Filtrar nombres válidos antes de procesar, y eliminar duplicados
  const nombresValidos = [...new Set(lista.filter(nombre => nombre && nombre.trim() !== ''))];
  console.log(`Procesando ${nombresValidos.length} nombres válidos para ${tipo}:`, nombresValidos);

  // Crear círculos SÓLO para los elementos que tienen un nombre válido
  nombresValidos.forEach((nombre, index) => {
    // Calcular un radio aleatorio pero proporcional al espacio disponible
    const radius = Math.floor(Math.random() * (maxRadius - minRadius) + minRadius);

    // Posición inicial dentro del canvas
    const x = Math.random() * (width - radius * 2) + radius;
    const y = Math.random() * (height - radius * 2) + radius;

    // Velocidad inicial aleatoria (incrementada para más movimiento)
    const vx = (Math.random() - 0.5) * 4; // Velocidad incrementada
    const vy = (Math.random() - 0.5) * 4; // Velocidad incrementada

    // Crear el cuerpo físico
    const circulo = Bodies.circle(x, y, radius, {
      restitution: 0.8,
      friction: 0.005,
      frictionAir: 0.01,
      render: {
        fillStyle: '#333333',
        strokeStyle: colorPrincipal,
        lineWidth: 2
      }
    });

    // Establecer velocidad inicial
    Body.setVelocity(circulo, { x: vx, y: vy });

    // Almacenar información adicional con el círculo
    const circuloInfo = {
      body: circulo,
      nombre: nombre,
      nivel: 0,
      radio: radius,
      radioOriginal: radius
    };

    circulo.label = 'circle'; // Asegura que no interfiera con renderizado
    circulo.circuloInfo = circuloInfo;

    // Añadir a la lista
    circulos[tipo].push(circuloInfo);

    // Añadir al mundo
    World.add(world, circulo);
  });

  // Verificar que se crearon exactamente la misma cantidad de círculos que nombres válidos
  console.log(`Creados ${circulos[tipo].length} círculos para ${nombresValidos.length} elementos válidos en la lista de ${tipo}`);

  // Actualizar los límites del mundo físico cada vez que se crean los círculos
  updateWorldBoundaries();
}
// Función para dibujar texto en círculos
function dibujarTextoEnCirculos() {
  // Para cada tipo de círculo (estilos, marcas)
  Object.keys(circulos).forEach(tipo => {
    if (renders[tipo] && renders[tipo].canvas) {
      const render = renders[tipo];
      const ctx = render.context;
      
      // Evento para dibujar texto después de cada renderizado
      Events.on(render, 'afterRender', function() {
        circulos[tipo].forEach(circuloInfo => {
          const body = circuloInfo.body;
          const pos = body.position;
          
          // Configurar estilo de texto
          ctx.font = '12px Arial';
          ctx.fillStyle = 'white';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          
          // Dibujar nombre dentro del círculo
          ctx.fillText(circuloInfo.nombre, pos.x, pos.y);
        });
      });
    }
  });
}

// Variables para evitar múltiples instancias de mouseConstraint
const mouseConstraints = {};

// Configurar los eventos de mouse para cada render
function setupMouseInteraction(tipo) {
  console.log(`Configurando interacción del mouse para ${tipo}`);
  if (!renders[tipo] || !renders[tipo].canvas) {
    console.error(`Render para ${tipo} no inicializado correctamente`);
    return;
  }
  
  const canvas = renders[tipo].canvas;
  console.log(`Canvas encontrado para ${tipo}: ${canvas.width}x${canvas.height}`);
  
  // Eliminar mouse constraint anterior si existe
  if (mouseConstraints[tipo]) {
    World.remove(world, mouseConstraints[tipo]);
    delete mouseConstraints[tipo];
  }
  
  // Crear un nuevo mouse usando el canvas específico
  const mouse = Mouse.create(canvas);
  
  // Ajustar el escalado del mouse para que coincida con el canvas
  mouse.pixelRatio = window.devicePixelRatio || 1;
  
  const mouseConstraint = MouseConstraint.create(engine, {
    mouse: mouse,
    constraint: {
      stiffness: 0.2,
      render: {
        visible: true // Hacer visible la restricción del mouse
      }
    }
  });
  
  mouseConstraints[tipo] = mouseConstraint;
  World.add(world, mouseConstraint);
  
  console.log(`Mouse constraint creado para ${tipo}`);
  
  // Al hacer clic en un círculo
  Events.on(mouseConstraint, 'mousedown', (event) => {
    const mousePosition = event.mouse.position;
    const circulosActivos = circulos[tipo];
    
    console.log(`Click detectado en ${tipo}, posición: (${mousePosition.x}, ${mousePosition.y})`);
    
    circulosActivos.forEach(circuloInfo => {
      const body = circuloInfo.body;
      const dx = body.position.x - mousePosition.x;
      const dy = body.position.y - mousePosition.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < circuloInfo.radio) {
        console.log(`Click en círculo: ${circuloInfo.nombre}`);
        // Cambiar nivel de selección (0-4 y luego vuelve a 0)
        circuloInfo.nivel = (circuloInfo.nivel + 1) % 5;
        
        // Cambiar color según nivel
        const colors = ['#333333', '#444444', '#555555', '#666666', '#777777'];
        body.render.fillStyle = colors[circuloInfo.nivel];
        
        // Determinar el factor de escala para el círculo
        const escalaActual = body.circleRadius / circuloInfo.radioOriginal;
        let nuevaEscala = tamañoPorNivel[circuloInfo.nivel] / escalaActual;
        
        // Calcular nuevo radio basado en el nivel
        const nuevoRadio = circuloInfo.radioOriginal * tamañoPorNivel[circuloInfo.nivel];
        circuloInfo.radio = nuevoRadio;
        
        // Escalar el cuerpo físico correctamente
        Body.scale(body, nuevaEscala, nuevaEscala);
        
        // Actualizar respuestas 
        if (circuloInfo.nivel > 0) {
          respuestas[tipo][circuloInfo.nombre] = circuloInfo.nivel; // Guardamos el nivel de preferencia
        } else {
          delete respuestas[tipo][circuloInfo.nombre]; // Si el nivel es 0, eliminamos la preferencia
        }
        
        // Aplicar una fuerza para que el círculo se mueva al cambiar
        Body.applyForce(body, body.position, {
          x: (Math.random() - 0.5) * 0.1, // Mayor fuerza 
          y: (Math.random() - 0.5) * 0.1  // Mayor fuerza
        });
      }
    });
  });
  
  // Asegurarse de que el mouse se actualice con el movimiento
  Events.on(mouseConstraint, 'mousemove', () => {
    // Esto asegura que el mouse constraint esté activo
    console.log("Mouse moviendo");
  });
  
  // Desactivar el evento right click del navegador
  canvas.addEventListener('contextmenu', function(e) {
    e.preventDefault();
  });
  
  // Hacer que los círculos también se muevan al hacer clic en el fondo
  canvas.addEventListener('click', function(e) {
    // Aplicar fuerzas aleatorias a todos los círculos
    circulos[tipo].forEach(circuloInfo => {
      Body.applyForce(circuloInfo.body, circuloInfo.body.position, {
        x: (Math.random() - 0.5) * 0.05,
        y: (Math.random() - 0.5) * 0.05
      });
    });
  });
  
  // Actualizar el mouse del render
  renders[tipo].mouse = mouse;
}

// Función para actualizar límites del mundo
function updateWorldBoundaries() {
  // Eliminar paredes anteriores si existen
  const walls = world.bodies.filter(body => body.label === 'wall');
  walls.forEach(wall => World.remove(world, wall));
  
  // Crear nuevas paredes según la pregunta actual
  const tipo = currentPregunta === 1 ? 'estilos' : currentPregunta === 2 ? 'marcas' : null;
  
  if (tipo && canvasDivs[tipo]) {
    const canvasDiv = canvasDivs[tipo];
    const width = canvasDiv.offsetWidth;
    const height = canvasDiv.offsetHeight;
    
    // Crear las cuatro paredes
    const wallThickness = 50;
    const walls = [
      // Pared superior
      Bodies.rectangle(width / 2, -wallThickness / 2, width, wallThickness, {
        isStatic: true,
        render: { fillStyle: 'transparent' },
        label: 'wall'
      }),
      // Pared inferior
      Bodies.rectangle(width / 2, height + wallThickness / 2, width, wallThickness, {
        isStatic: true,
        render: { fillStyle: 'transparent' },
        label: 'wall'
      }),
      // Pared izquierda
      Bodies.rectangle(-wallThickness / 2, height / 2, wallThickness, height, {
        isStatic: true,
        render: { fillStyle: 'transparent' },
        label: 'wall'
      }),
      // Pared derecha
      Bodies.rectangle(width + wallThickness / 2, height / 2, wallThickness, height, {
        isStatic: true,
        render: { fillStyle: 'transparent' },
        label: 'wall'
      })
    ];
    
    walls.forEach(wall => {
      World.add(world, wall);
    });
  }
}

// Inicializar la navegación entre preguntas
function initNavigation() {
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const progressBar = document.getElementById('progress-bar');
  
  if (!prevBtn || !nextBtn || !progressBar) {
    console.error('Elementos de navegación no encontrados');
    return;
  }
  
  // Actualizar barra de progreso
  function updateProgress() {
    const percentage = ((currentPregunta - 1) / totalPreguntas) * 100;
    progressBar.style.width = `${percentage}%`;
  }
    // Cambiar a la siguiente pregunta
  nextBtn.addEventListener('click', () => {
    // Buscar la pregunta actual
    const preguntaActual = document.getElementById(`pregunta-${currentPregunta}`);
    if (!preguntaActual) {
      console.error(`Elemento pregunta-${currentPregunta} no encontrado`);
      return;
    }
    
    console.log(`Cambiando de pregunta ${currentPregunta} a ${currentPregunta + 1}`);
    
    const tipo = preguntaActual.dataset.type;
    const key = preguntaActual.dataset.key;
    
    if (tipo === 'select') {
      const select = document.getElementById(key);
      if (select) {
        respuestas[key] = select.value;
      }
    }
    
    // Ocultar pregunta actual
    preguntaActual.classList.remove('active');
    
    // Detener render actual si es de tipo círculos
    if (tipo === 'circles' && renders[key]) {
      Render.stop(renders[key]);
    }
    
    // Incrementar contador
    currentPregunta++;
    
    // Preparar la siguiente pregunta si es la de las marcas
    if (currentPregunta === 2) {
      console.log('Preparando pregunta de marcas...');
      // Crear los círculos para la pregunta de marcas
      crearCirculos('marcas', marcas);
      // Configurar interacción del mouse para marcas
      setupMouseInteraction('marcas');
      // Actualizar límites para marcas
      updateWorldBoundaries();
    }
    
    if (currentPregunta > totalPreguntas) {
      // Mostrar modal de finalización
      const modal = document.getElementById('completion-modal');
      if (modal) {
        modal.style.display = 'flex';
        createConfetti();
      } else {
        console.error('Modal de finalización no encontrado');
      }
      return;
    }
    
    // Mostrar nueva pregunta
    const nuevaPregunta = document.getElementById(`pregunta-${currentPregunta}`);
    if (!nuevaPregunta) {
      console.error(`Elemento pregunta-${currentPregunta} no encontrado`);
      return;
    }
    
    nuevaPregunta.classList.add('active');
    
    // Si la nueva pregunta es de tipo círculos, iniciar su render
    if (nuevaPregunta.dataset.type === 'circles') {
      const tipoNuevo = nuevaPregunta.dataset.key;
      updateWorldBoundaries();
      if (renders[tipoNuevo]) {
        Render.run(renders[tipoNuevo]);
      }
    }
    
    // Actualizar estado de botones
    prevBtn.disabled = false;
    if (currentPregunta === totalPreguntas) {
      nextBtn.innerHTML = 'Finalizar <i class="fas fa-check"></i>';
    } else {
      nextBtn.innerHTML = 'Siguiente <i class="fas fa-arrow-right"></i>';
    }
    
    // Actualizar barra de progreso
    updateProgress();
  });
  
  // Cambiar a la pregunta anterior
  prevBtn.addEventListener('click', () => {
    // Buscar la pregunta actual
    const preguntaActual = document.getElementById(`pregunta-${currentPregunta}`);
    if (!preguntaActual) {
      console.error(`Elemento pregunta-${currentPregunta} no encontrado`);
      return;
    }
    
    const tipo = preguntaActual.dataset.type;
    const key = preguntaActual.dataset.key;
    
    // Detener render actual si es de tipo círculos
    if (tipo === 'circles' && renders[key]) {
      Render.stop(renders[key]);
    }
    
    preguntaActual.classList.remove('active');
    
    // Decrementar contador
    currentPregunta--;
    
    // Mostrar pregunta anterior
    const preguntaAnterior = document.getElementById(`pregunta-${currentPregunta}`);
    if (!preguntaAnterior) {
      console.error(`Elemento pregunta-${currentPregunta} no encontrado`);
      return;
    }
    
    preguntaAnterior.classList.add('active');
      // Si la pregunta anterior es de tipo círculos, volver a crear los círculos e iniciar su render
    if (preguntaAnterior.dataset.type === 'circles') {
      const tipoAnterior = preguntaAnterior.dataset.key;
      
      // Si regresamos a la pregunta 1, volver a crear los círculos de estilos
      if (currentPregunta === 1) {
        crearCirculos('estilos', estilos);
        setupMouseInteraction('estilos');
      }
      
      updateWorldBoundaries();
      if (renders[tipoAnterior]) {
        Render.run(renders[tipoAnterior]);
      }
    }
    
    // Actualizar estado de botones
    prevBtn.disabled = currentPregunta === 1;
    nextBtn.innerHTML = 'Siguiente <i class="fas fa-arrow-right"></i>';
    
    // Actualizar barra de progreso
    updateProgress();
  });
  
  // Configurar botón de finalización
  const finishBtn = document.getElementById('finish-btn');
  if (finishBtn) {
    finishBtn.addEventListener('click', () => {
      // Enviar los datos al servidor
      const formData = new FormData();
      
      // Convertir las respuestas a formato JSON
      formData.append('respuestas', JSON.stringify(respuestas));
      
      fetch('/guardar_preferencias', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          window.location.href = '/recomendaciones';
        } else {
          alert('Error al guardar tus preferencias. Por favor, intenta nuevamente.');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente.');
      });
    });
  }
}

// Función para crear efecto de confeti
function createConfetti() {
  const modal = document.getElementById('completion-modal');
  if (!modal) {
    console.error('Modal de finalización no encontrado');
    return;
  }
  
  const modalRect = modal.getBoundingClientRect();
  
  for (let i = 0; i < 100; i++) {
    const confetti = document.createElement('div');
    confetti.classList.add('confetti');
    
    // Colores aleatorios para el confeti
    const colors = ['#f97316', '#fb923c', '#fdba74', '#fed7aa', '#ff4500'];
    confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    
    // Posición inicial aleatoria
    confetti.style.left = `${Math.random() * 100}%`;
    
    // Tamaño aleatorio
    const size = Math.random() * 8 + 5;
    confetti.style.width = `${size}px`;
    confetti.style.height = `${size}px`;
    
    // Velocidad de caída y rotación aleatoria
    confetti.style.animationDuration = `${Math.random() * 3 + 2}s`;
    confetti.style.animationDelay = `${Math.random() * 3}s`;
    
    modal.appendChild(confetti);
    
    // Eliminar el confeti después de la animación
    setTimeout(() => {
      if (confetti.parentNode === modal) {
        confetti.remove();
      }
    }, 5000);
  }
}

// Inicializar simulación física para el fondo
function initPhysicsBackground() {
  const container = document.getElementById('physics-container');
  if (!container) {
    console.error('Contenedor de física de fondo no encontrado');
    return;
  }
  
  // Crear un motor de física separado para el fondo
  const bgEngine = Engine.create();
  const bgWorld = bgEngine.world;
  
  const bgRender = Render.create({
    element: container,
    engine: bgEngine,
    options: {
      width: container.offsetWidth,
      height: container.offsetHeight,
      wireframes: false,
      background: 'transparent'
    }
  });
  

  
  // Agregar paredes invisibles
  const walls = [
    Bodies.rectangle(container.offsetWidth / 2, -10, container.offsetWidth, 20, { isStatic: true }),
    Bodies.rectangle(container.offsetWidth / 2, container.offsetHeight + 10, container.offsetWidth, 20, { isStatic: true }),
    Bodies.rectangle(-10, container.offsetHeight / 2, 20, container.offsetHeight, { isStatic: true }),
    Bodies.rectangle(container.offsetWidth + 10, container.offsetHeight / 2, 20, container.offsetHeight, { isStatic: true })
  ];
  
  World.add(bgWorld, walls);
  
  // Ejecutar el motor y el render

  Engine.run(bgEngine);
  Render.run(bgRender);
  
  // Ajustar el tamaño del render al cambiar el tamaño de la ventana
  window.addEventListener('resize', () => {
    bgRender.options.width = container.offsetWidth;
    bgRender.options.height = container.offsetHeight;
    Render.setPixelRatio(bgRender, window.devicePixelRatio || 1);
    
    // Actualizar posición de las paredes
    walls[0].position.x = container.offsetWidth / 2;
    walls[1].position.x = container.offsetWidth / 2;
    walls[1].position.y = container.offsetHeight + 10;
    walls[2].position.y = container.offsetHeight / 2;
    walls[3].position.x = container.offsetWidth + 10;
    walls[3].position.y = container.offsetHeight / 2;
  });
  
  return { engine: bgEngine, render: bgRender };
}

// Función principal de inicialización
function init() {
  try {
    console.log('Iniciando sistema...');
    
    // Verificamos que Matter.js esté disponible
    if (typeof Matter === 'undefined') {
      console.error('Error: Matter.js no está cargado');
      alert('Error al cargar la librería de física. Por favor, recarga la página.');
      return;
    }
    
    // Reiniciar el mundo para asegurar que esté limpio
    World.clear(world, false);
    
    // Inicializar renders
    inicializarRenders();
    
    // Añadir función para dibujar texto en círculos
    dibujarTextoEnCirculos();
    
    // Actualizar paredes del mundo físico
    updateWorldBoundaries();
    
    // Inicializar círculos para la primera pregunta
    crearCirculos('estilos', estilos);
    
    // Configurar interacciones para la primera pregunta
    setupMouseInteraction('estilos');
    
    // Inicializar navegación
    initNavigation();
    
    // Iniciar el render para la primera pregunta
    const primeraPregunta = document.getElementById('pregunta-1');
    if (primeraPregunta && primeraPregunta.dataset.type === 'circles') {
      const tipo = primeraPregunta.dataset.key;
      if (renders[tipo]) {
        Render.run(renders[tipo]);
        console.log(`Render activado para ${tipo}`);
      }
    }
    
    // Iniciar el motor de física principal
    Engine.run(engine);
    
    // Inicializar fondo con física (motor independiente) - esto debe ir después
    initPhysicsBackground();
    
    // Dar un impulso inicial a todos los círculos para que se muevan
    circulos['estilos'].forEach(circuloInfo => {
      Body.applyForce(circuloInfo.body, circuloInfo.body.position, {
        x: (Math.random() - 0.5) * 0.1,
        y: (Math.random() - 0.5) * 0.1
      });
    });
    
    console.log('Sistema inicializado correctamente');
  } catch (error) {
    console.error('Error al inicializar el sistema:', error);
    alert('Ha ocurrido un error al inicializar el test. Por favor, recarga la página.');
  }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', init);

// Sugerencia CSS para asegurar altura mínima en #marcas-canvas:
// #marcas-canvas { height: 300px; }