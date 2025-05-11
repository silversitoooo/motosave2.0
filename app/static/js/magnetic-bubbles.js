/**
 * Magnetic Bubbles - Un selector de burbujas interactivo inspirado en Magnetic/Apple Music
 * Para MotoMatch Test de Preferencias
 */

console.log('Cargando MagneticBubbles.js...');

class MagneticBubbles {
  constructor(containerId, items, options = {}) {
    // El elemento contenedor donde se mostrarán las burbujas
    this.container = document.getElementById(containerId);
    if (!this.container) throw new Error(`Contenedor con ID "${containerId}" no encontrado`);
      // Los elementos a mostrar como burbujas
    this.items = items || [];
    
    // Opciones configurables con valores por defecto
    this.options = {      minRadius: 40,              // Radio mínimo de las burbujas (era 30)
      maxRadius: 65,              // Radio máximo de las burbujas (era 55)      
      padding: 25,                // Espacio entre burbujas (aumentado para evitar traslape)
      dampening: 0.98,            // Factor de amortiguación para el movimiento (reducido para mantener más energía)
      attractionForce: 0,         // Fuerza de atracción al centro (0 para que floten libremente)
      repulsionForce: 0.6,        // Fuerza de repulsión entre burbujas (aumentada para mayor separación)
      colorPalette: [             // Paleta de colores: ahora gris para todas
        '#707070', '#707070', '#707070', '#707070', '#707070',
        '#707070', '#707070', '#707070', '#707070', '#707070'
      ],
      selectionLevels: 4,         // Niveles de selección (0 = no seleccionado, 1-4 = niveles)
      textColor: '#ffffff',       // Color del texto en las burbujas
      textFont: '14px Arial',     // Fuente del texto (era 12px)
      animationInterval: 16,      // Intervalo de animación (ms)
      initialImpulse: 3,          // Impulso inicial máximo
      ...options                  // Opciones personalizadas
    };
    
    // Estado interno
    this.bubbles = [];            // Array de burbujas
    this.mouse = { x: 0, y: 0, pressed: false };
    this.draggedBubble = null;    // Burbuja que se está arrastrando
    this.canvas = null;           // Canvas para dibujar
    this.ctx = null;              // Contexto de dibujo
    this.animationId = null;      // ID para gestionar animaciones
    this.selectedBubbles = {};    // Burbujas seleccionadas
    this.initialized = false;     // Estado de inicialización
    this.lastUpdate = Date.now(); // Último tiempo de actualización
    this.clickStartTime = 0;      // Tiempo en que inició el clic (para distinguir entre clic y arrastre)
    this.dragThreshold = 5;       // Distancia en píxeles para considerar un arrastre en lugar de un clic
    
    // Inicializar
    this._init();
  }
  
  /**
   * Inicializa el componente
   */
  _init() {
    try {
      // Crear el canvas
      this.canvas = document.createElement('canvas');
      this.canvas.style.width = '100%';
      this.canvas.style.height = '100%';
      this.canvas.style.display = 'block';
      this.container.appendChild(this.canvas);
      
      // Ajustar tamaño del canvas al contenedor
      this._resizeCanvas();
      
      // Obtener el contexto de dibujo
      this.ctx = this.canvas.getContext('2d');
      if (!this.ctx) {
        throw new Error("No se pudo obtener el contexto 2D del canvas");
      }
      
      // Crear las burbujas
      this._createBubbles();
      
      // Configurar eventos
      this._setupEvents();
      
      // Iniciar la animación
      this._startAnimation();
      
      this.initialized = true;
      console.log('MagneticBubbles inicializado: ', this.bubbles.length, 'burbujas creadas');
    } catch (error) {
      console.error('Error al inicializar MagneticBubbles:', error);
      // Intentar mostrar un mensaje visual de error en el canvas
      if (this.canvas && this.ctx) {
        this.ctx.fillStyle = '#f97316';
        this.ctx.font = '14px Arial';
        this.ctx.fillText('Error al inicializar las burbujas interactivas', 20, 30);
        this.ctx.fillText('Por favor, recarga la página', 20, 50);
      }
    }
  }
    /**
   * Crea las burbujas iniciales
   */
  _createBubbles() {
    // Limpiar burbujas existentes
    this.bubbles = [];
    
    // Calcular distribución en cuadrícula para posición inicial
    const itemCount = this.items.length;
    const gridSize = Math.ceil(Math.sqrt(itemCount));
    
    // Calcular el tamaño de cada celda de la cuadrícula
    const cellWidth = this.canvas.width / gridSize;
    const cellHeight = this.canvas.height / gridSize;
    
    // Calcular radio máximo efectivo (incluyendo padding)
    const maxRadiusWithPadding = this.options.maxRadius + this.options.padding;
    
    // Asegurar que las celdas son lo suficientemente grandes para las burbujas
    const minCellDimension = Math.min(cellWidth, cellHeight);
    
    // Ajustar el radio si es necesario para evitar solapamientos
    const adjustedMaxRadius = Math.min(
      this.options.maxRadius,
      minCellDimension / 2 - this.options.padding
    );
    
    const adjustedMinRadius = Math.min(
      this.options.minRadius,
      adjustedMaxRadius * 0.7
    );
    
    // Crear una burbuja por cada ítem
    this.items.forEach((item, idx) => {
      // Calcular posición en la cuadrícula
      const row = Math.floor(idx / gridSize);
      const col = idx % gridSize;
      
      // Calcular el centro de la celda
      const cellCenterX = (col + 0.5) * cellWidth;
      const cellCenterY = (row + 0.5) * cellHeight;
      
      // Añadir una variación aleatoria más pequeña para evitar solapamientos
      const variationFactor = 0.3; // Reducido de 0.4-0.5 a 0.3
      const x = cellCenterX + (Math.random() * 2 - 1) * variationFactor * (cellWidth / 2 - maxRadiusWithPadding);
      const y = cellCenterY + (Math.random() * 2 - 1) * variationFactor * (cellHeight / 2 - maxRadiusWithPadding);
      
      // Radio aleatorio dentro del rango ajustado
      const radius = Math.random() * (adjustedMaxRadius - adjustedMinRadius) 
                    + adjustedMinRadius;
                    
      // Color aleatorio de la paleta
      const color = this.options.colorPalette[idx % this.options.colorPalette.length];
      
      // Velocidad inicial aleatoria (más suave)
      const velX = (Math.random() * 2 - 1) * this.options.initialImpulse * 0.7;
      const velY = (Math.random() * 2 - 1) * this.options.initialImpulse * 0.7;
      
      // Crear la burbuja
      this.bubbles.push({
        id: idx,
        x: x,
        y: y,
        radius: radius,
        originalRadius: radius, // Guardar radio original para animaciones
        color: color,
        text: item,
        vx: velX,
        vy: velY,
        selected: 0, // 0 = no seleccionado
        startX: 0,   // Posición inicial al comenzar un arrastre
        startY: 0    // Posición inicial al comenzar un arrastre
      });
    });
  }
    /**
   * Configura los eventos de interacción
   */
  _setupEvents() {
    // Evento de redimensión
    window.addEventListener('resize', () => {
      this._resizeCanvas();
      this._repositionBubbles();
    });
    
    // Eventos de ratón/táctil
    this.canvas.addEventListener('mousedown', (e) => this._handleMouseDown(e));
    this.canvas.addEventListener('touchstart', (e) => this._handleTouchStart(e));
    
    this.canvas.addEventListener('mousemove', (e) => this._handleMouseMove(e));
    this.canvas.addEventListener('touchmove', (e) => this._handleTouchMove(e), { passive: false });
    
    this.canvas.addEventListener('mouseup', () => this._handleMouseUp());
    this.canvas.addEventListener('touchend', () => this._handleMouseUp());
    this.canvas.addEventListener('mouseleave', () => this._handleMouseUp());
    
    // Aplicar impulso aleatorio al hacer clic en área vacía
    this.canvas.addEventListener('click', (e) => {
      const mousePos = this._getMousePos(e);
      const clickedBubble = this._findBubbleAtPosition(mousePos.x, mousePos.y);
      
      if (!clickedBubble) {
        // Clic en área vacía, aplicar impulso aleatorio a todas las burbujas
        this._applyRandomImpulse();
      }
    });
  }
    /**
   * Inicia la animación de las burbujas
   */
  _startAnimation() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    
    const animate = () => {
      // Actualizar posiciones
      this._updatePositions();
      
      // Dibujar en el canvas
      this._render();
      
      // Continuar animación
      this.animationId = requestAnimationFrame(animate);
    };
    
    animate();
    
    // Aplicar impulso aleatorio periódicamente para mantener el movimiento
    // Más frecuente pero menor intensidad para un movimiento más constante
    setInterval(() => this._applyRandomImpulse(0.4), 2000);
    // Y ocasionalmente un impulso más fuerte
    setInterval(() => this._applyRandomImpulse(1.0), 8000);
  }
  /**
   * Actualiza las posiciones de las burbujas en cada frame
   */
  _updatePositions() {
    const now = Date.now();
    const dt = (now - this.lastUpdate) / 16; // normalizar a ~60fps
    this.lastUpdate = now;
    
    // Actualizar cada burbuja
    this.bubbles.forEach((bubble) => {
      // Si el ratón está arrastrando esta burbuja, no actualizar su posición aquí
      if (this.draggedBubble === bubble) {
        return;
      }
      
      // Aplicar repulsión entre burbujas
      this._applyBubbleRepulsion(bubble, dt);
      
      // Aplicar ligero movimiento aleatorio para mantenerlas flotando
      if (Math.random() < 0.05) {
        bubble.vx += (Math.random() - 0.5) * 0.5;
        bubble.vy += (Math.random() - 0.5) * 0.5;
      }
      
      // Amortiguación
      bubble.vx *= this.options.dampening;
      bubble.vy *= this.options.dampening;
      
      // Actualizar posición
      bubble.x += bubble.vx * dt;
      bubble.y += bubble.vy * dt;
      
      // Rebote en los bordes
      this._handleEdgeCollisions(bubble);
    });
  }  /**
   * Aplica repulsión entre burbujas para evitar solapamientos
   */
  _applyBubbleRepulsion(bubble, dt) {
    this.bubbles.forEach((other) => {
      if (bubble === other) return;
      
      const dx = other.x - bubble.x;
      const dy = other.y - bubble.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const minDistance = bubble.radius + other.radius + this.options.padding;
      
      if (distance < minDistance) {
        // Calcular vector de dirección normalizado
        const nx = dx / distance || 0; // Evitar división por cero
        const ny = dy / distance || 0; // Evitar división por cero
        
        // Fuerza de repulsión inversamente proporcional a la distancia
        // Aumentamos el exponente para que la fuerza sea más fuerte cuando están muy cerca
        const force = this.options.repulsionForce * Math.pow((minDistance - distance) / minDistance, 3.0);
        
        // Si están demasiado cerca, aplicar una corrección directa de posición más agresiva
        if (distance < minDistance * 0.95) {
          const correctionFactor = (minDistance - distance) * 0.2;
          bubble.x -= nx * correctionFactor;
          bubble.y -= ny * correctionFactor;
          other.x += nx * correctionFactor;
          other.y += ny * correctionFactor;
          
          // Añadir velocidad en dirección opuesta para más energía en la separación
          const energyBoost = 0.3;
          bubble.vx -= nx * energyBoost;
          bubble.vy -= ny * energyBoost;
          other.vx += nx * energyBoost;
          other.vy += ny * energyBoost;
        }
        
        // Aplicar fuerza de repulsión más fuerte cuando están cerca
        const scaledForce = force * dt * 3.5;
        bubble.vx -= nx * scaledForce;
        bubble.vy -= ny * scaledForce;
        other.vx += nx * scaledForce;
        other.vy += ny * scaledForce;
      }
    });
  }
    /**
   * Maneja las colisiones con los bordes del canvas
   */
  _handleEdgeCollisions(bubble) {
    // Coeficiente de restitución (rebote)
    const bounceFactor = -0.95;
    // Umbral mínimo de velocidad para asegurar rebotes visibles
    const minVelocity = 0.8;
    
    // Rebote en el borde derecho
    if (bubble.x + bubble.radius > this.canvas.width) {
      bubble.x = this.canvas.width - bubble.radius;
      // Asegurar que la velocidad post-rebote sea suficiente para un buen efecto visual
      bubble.vx = Math.max(Math.abs(bubble.vx * bounceFactor), minVelocity) * Math.sign(bounceFactor);
      // Aplicar pequeño impulso en la dirección Y para hacer el movimiento más interesante
      bubble.vy += (Math.random() - 0.5) * 0.5;
    }
    
    // Rebote en el borde izquierdo
    if (bubble.x - bubble.radius < 0) {
      bubble.x = bubble.radius;
      bubble.vx = Math.max(Math.abs(bubble.vx * bounceFactor), minVelocity) * Math.sign(-bounceFactor);
      bubble.vy += (Math.random() - 0.5) * 0.5;
    }
    
    // Rebote en el borde inferior
    if (bubble.y + bubble.radius > this.canvas.height) {
      bubble.y = this.canvas.height - bubble.radius;
      bubble.vy = Math.max(Math.abs(bubble.vy * bounceFactor), minVelocity) * Math.sign(bounceFactor);
      bubble.vx += (Math.random() - 0.5) * 0.5;
    }
    
    // Rebote en el borde superior
    if (bubble.y - bubble.radius < 0) {
      bubble.y = bubble.radius;
      bubble.vy = Math.max(Math.abs(bubble.vy * bounceFactor), minVelocity) * Math.sign(-bounceFactor);
      bubble.vx += (Math.random() - 0.5) * 0.5;
    }
  }
  
  /**
   * Dibuja las burbujas en el canvas
   */
  _render() {
    // Limpiar el canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Dibujar cada burbuja
    this.bubbles.forEach(bubble => {
      this._drawBubble(bubble);
    });
  }
    /**
   * Dibuja una burbuja individual
   */
  _drawBubble(bubble) {
    this.ctx.save();
    
    // Dibujar círculo
    this.ctx.beginPath();
    this.ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);
    
    // Color de relleno gris para todas las burbujas
    let fillColor = bubble.color;
    
    // Modificar color según el nivel de selección
    if (bubble.selected > 0) {
      // Aumentar brillo según nivel de selección
      fillColor = this._adjustBrightness(bubble.color, 0.15 * bubble.selected);
    }
    
    this.ctx.fillStyle = fillColor;
    this.ctx.fill();
    
    // Borde naranja para todas las burbujas
    if (bubble.selected > 0) {
      this.ctx.strokeStyle = '#FFC107'; // Amarillo para seleccionados
      this.ctx.lineWidth = 3;
    } else {
      this.ctx.strokeStyle = '#f97316'; // Naranja para no seleccionados
      this.ctx.lineWidth = 2;
    }
    this.ctx.stroke();
    
    // Texto
    this.ctx.fillStyle = this.options.textColor;
    this.ctx.font = this.options.textFont;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    
    // Sombra para mejor legibilidad
    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.7)';
    this.ctx.shadowBlur = 4;
    this.ctx.shadowOffsetX = 1;
    this.ctx.shadowOffsetY = 1;
    
    this.ctx.fillText(bubble.text, bubble.x, bubble.y);
    this.ctx.restore();
  }
  
  /**
   * Ajusta el tamaño del canvas al contenedor
   */
  _resizeCanvas() {
    const rect = this.container.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }
    /**
   * Reposiciona las burbujas al cambiar el tamaño
   */
  _repositionBubbles() {
    if (this.bubbles.length === 0) return;
    
    // Calcular factor de escala
    const gridSize = Math.ceil(Math.sqrt(this.bubbles.length));
    const cellWidth = this.canvas.width / gridSize;
    const cellHeight = this.canvas.height / gridSize;
    
    // Calcular radio máximo efectivo (incluyendo padding)
    const maxRadiusWithPadding = Math.max(...this.bubbles.map(b => b.radius)) + this.options.padding;
    
    // Reposicionar burbujas
    this.bubbles.forEach((bubble, idx) => {
      const row = Math.floor(idx / gridSize);
      const col = idx % gridSize;
      
      // Calcular el centro de la celda
      const cellCenterX = (col + 0.5) * cellWidth;
      const cellCenterY = (row + 0.5) * cellHeight;
      
      // Aplicar variación más controlada para evitar solapamientos
      const variationFactor = 0.25; // Factor de variación reducido
      
      // Nueva posición
      bubble.x = cellCenterX + (Math.random() * 2 - 1) * variationFactor * (cellWidth / 2 - maxRadiusWithPadding);
      bubble.y = cellCenterY + (Math.random() * 2 - 1) * variationFactor * (cellHeight / 2 - maxRadiusWithPadding);
      
      // Resetear velocidades
      bubble.vx = (Math.random() * 2 - 1) * 0.5;
      bubble.vy = (Math.random() * 2 - 1) * 0.5;
    });
  }
    /**
   * Manejo de eventos del ratón
   */
  _handleMouseDown(e) {
    this.mouse.pressed = true;
    const mousePos = this._getMousePos(e);
    this.mouse.x = mousePos.x;
    this.mouse.y = mousePos.y;
    
    // Guardar el tiempo de inicio del clic para diferenciar clics de arrastres
    this.clickStartTime = Date.now();
    this.clickStartPos = { x: mousePos.x, y: mousePos.y };
    
    // Buscar si hay una burbuja en esta posición
    const clickedBubble = this._findBubbleAtPosition(mousePos.x, mousePos.y);
    
    if (clickedBubble) {
      // Guardar la burbuja que potencialmente se arrastrará
      this.draggedBubble = clickedBubble;
      // Guardar la posición inicial de la burbuja
      this.draggedBubble.startX = this.draggedBubble.x;
      this.draggedBubble.startY = this.draggedBubble.y;
    }
  }
  
  _handleTouchStart(e) {
    e.preventDefault();
    if (e.touches.length > 0) {
      const touch = e.touches[0];
      const touchPos = this._getTouchPos(touch);
      this._handleMouseDown({
        clientX: touchPos.x,
        clientY: touchPos.y
      });
    }
  }
    _handleMouseMove(e) {
    const mousePos = this._getMousePos(e);
    this.mouse.x = mousePos.x;
    this.mouse.y = mousePos.y;
    
    // Si hay una burbuja seleccionada para arrastrar y el mouse está presionado
    if (this.mouse.pressed && this.draggedBubble) {
      // Calcular la distancia que se ha movido desde el inicio del clic
      const dx = mousePos.x - this.clickStartPos.x;
      const dy = mousePos.y - this.clickStartPos.y;
      const moveDistance = Math.sqrt(dx * dx + dy * dy);
      
      // Si se ha movido más del umbral, consideramos que es un arrastre
      if (moveDistance > this.dragThreshold) {
        // Actualizar la posición de la burbuja arrastrada directamente
        this.draggedBubble.x = this.draggedBubble.startX + dx;
        this.draggedBubble.y = this.draggedBubble.startY + dy;
        
        // Reiniciar velocidades durante el arrastre
        this.draggedBubble.vx = 0;
        this.draggedBubble.vy = 0;
      }
    }
  }
  
  _handleTouchMove(e) {
    e.preventDefault();
    if (e.touches.length > 0) {
      const touch = e.touches[0];
      const touchPos = this._getTouchPos(touch);
      this._handleMouseMove({
        clientX: touchPos.x,
        clientY: touchPos.y
      });
    }
  }
    _handleMouseUp() {
    // Si hay una burbuja arrastrada
    if (this.draggedBubble) {
      // Verificar si fue un clic (evento rápido) o un arrastre
      const clickDuration = Date.now() - this.clickStartTime;
      const dx = this.mouse.x - this.clickStartPos.x;
      const dy = this.mouse.y - this.clickStartPos.y;
      const moveDistance = Math.sqrt(dx * dx + dy * dy);
      
      // Si fue un clic (corto y sin movimiento significativo)
      if (clickDuration < 300 && moveDistance < this.dragThreshold) {
        this._toggleBubbleSelection(this.draggedBubble);
      } 
      // Si fue un arrastre, dar un pequeño impulso en la dirección del movimiento
      else if (moveDistance >= this.dragThreshold) {
        // Dar un pequeño impulso en la dirección del movimiento
        this.draggedBubble.vx = dx * 0.1;
        this.draggedBubble.vy = dy * 0.1;
      }
      
      // Liberar la burbuja arrastrada
      this.draggedBubble = null;
    }
    
    this.mouse.pressed = false;
  }
  
  /**
   * Obtiene la posición del ratón relativa al canvas
   */
  _getMousePos(e) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left) * (this.canvas.width / rect.width),
      y: (e.clientY - rect.top) * (this.canvas.height / rect.height)
    };
  }
  
  /**
   * Obtiene la posición de un toque táctil relativa al canvas
   */
  _getTouchPos(touch) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: (touch.clientX - rect.left) * (this.canvas.width / rect.width),
      y: (touch.clientY - rect.top) * (this.canvas.height / rect.height)
    };
  }
  
  /**
   * Busca una burbuja en una posición específica
   */
  _findBubbleAtPosition(x, y) {
    // Buscar de atrás hacia adelante para que las burbujas delanteras tengan prioridad
    for (let i = this.bubbles.length - 1; i >= 0; i--) {
      const bubble = this.bubbles[i];
      const dx = bubble.x - x;
      const dy = bubble.y - y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance <= bubble.radius) {
        return bubble;
      }
    }
    return null;
  }
  
  /**
   * Alterna la selección de una burbuja
   */
  _toggleBubbleSelection(bubble) {
    // Incrementar el nivel de selección (0-4, cíclico)
    bubble.selected = (bubble.selected + 1) % (this.options.selectionLevels + 1);
    
    // Ajustar tamaño según selección
    const scaleFactor = 1.0 + (bubble.selected * 0.1);
    bubble.radius = bubble.originalRadius * scaleFactor;
    
    // Guardar selección en el objeto
    if (bubble.selected > 0) {
      this.selectedBubbles[bubble.text] = bubble.selected;
    } else {
      delete this.selectedBubbles[bubble.text];
    }
    
    // Notificar el cambio
    this._notifySelectionChanged();
    
    // Aplicar un pequeño impulso
    bubble.vx += (Math.random() - 0.5) * 3;
    bubble.vy += (Math.random() - 0.5) * 3;
  }
  
  /**
   * Notifica cambios en la selección
   */
  _notifySelectionChanged() {
    // Crear evento personalizado
    const event = new CustomEvent('selection-changed', {
      detail: {
        selections: { ...this.selectedBubbles }
      }
    });
    
    // Disparar evento en el contenedor
    this.container.dispatchEvent(event);
    
    console.log('Selección actualizada:', this.selectedBubbles);
  }
  
  /**
   * Aplica un impulso aleatorio a todas las burbujas
   */  _applyRandomImpulse(strength = 1.0) {
    this.bubbles.forEach(bubble => {
      // Aplicar impulsos más fuertes 
      bubble.vx += (Math.random() * 2 - 1) * 5 * strength;
      bubble.vy += (Math.random() * 2 - 1) * 5 * strength;
      
      // Asegurar que la velocidad total tiene un mínimo para mantener el movimiento interesante
      const speed = Math.sqrt(bubble.vx * bubble.vx + bubble.vy * bubble.vy);
      if (speed < 2.0 * strength) {
        const scaleFactor = 2.0 * strength / Math.max(0.1, speed);
        bubble.vx *= scaleFactor;
        bubble.vy *= scaleFactor;
      }
    });
  }
  
  /**
   * Ajusta el brillo de un color hexadecimal
   */
  _adjustBrightness(hex, factor) {
    // Convertir hex a RGB
    let r = parseInt(hex.substring(1, 3), 16);
    let g = parseInt(hex.substring(3, 5), 16);
    let b = parseInt(hex.substring(5, 7), 16);
    
    // Aumentar valores RGB
    r = Math.min(255, Math.round(r * (1 + factor)));
    g = Math.min(255, Math.round(g * (1 + factor)));
    b = Math.min(255, Math.round(b * (1 + factor)));
    
    // Convertir de vuelta a hex
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }
  
  // ===== MÉTODOS PÚBLICOS =====
  
  /**
   * Obtiene las selecciones actuales
   */
  getSelections() {
    return { ...this.selectedBubbles };
  }
  
  /**
   * Restablece las selecciones
   */
  resetSelections() {
    this.selectedBubbles = {};
    this.bubbles.forEach(bubble => {
      bubble.selected = 0;
      bubble.radius = bubble.originalRadius;
    });
    this._notifySelectionChanged();
  }
  
  /**
   * Establece selecciones específicas
   */
  setSelections(selections = {}) {
    this.resetSelections();
    
    this.bubbles.forEach(bubble => {
      if (selections[bubble.text]) {
        bubble.selected = selections[bubble.text];
        
        // Ajustar tamaño según selección
        const scaleFactor = 1.0 + (bubble.selected * 0.1);
        bubble.radius = bubble.originalRadius * scaleFactor;
        
        // Guardar en selecciones
        this.selectedBubbles[bubble.text] = bubble.selected;
      }
    });
    
    this._notifySelectionChanged();
  }
  
  /**
   * Aplica un impulso aleatorio a todas las burbujas (método público)
   */
  applyImpulse(strength = 1.0) {
    this._applyRandomImpulse(strength);
  }
  /**
   * Destructor: limpia eventos y detiene animaciones
   */
  destroy() {
    try {
      // Detener animación
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
      
      // Limpiar referencias
      this.bubbles = [];
      this.selectedBubbles = {};
      this.draggedBubble = null;
      this.mouse = { x: 0, y: 0, pressed: false };
      
      // Eliminar eventos si el canvas existe
      if (this.canvas) {
        // Asegurar que limpiamos todos los event listeners
        if (this.canvas.parentNode) {
          const newCanvas = this.canvas.cloneNode(false);
          if (this.canvas.parentNode) {
            this.canvas.parentNode.replaceChild(newCanvas, this.canvas);
          }
        }
        
        // Limpiar el canvas antes de eliminarlo
        if (this.ctx) {
          this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
          this.ctx = null;
        }
        
        // Eliminar canvas del DOM si aún está presente
        if (this.canvas.parentNode) {
          this.canvas.parentNode.removeChild(this.canvas);
        }
        
        this.canvas = null;
      }
      
      // Eliminar referencia al contenedor
      this.container = null;
      
      console.log('MagneticBubbles destruido correctamente');
      this.initialized = false;
    } catch (error) {
      console.error('Error al destruir MagneticBubbles:', error);
    }
  }
}

// Exportar al contexto global para usarlo desde HTML
window.MagneticBubbles = MagneticBubbles;

// Confirmar disponibilidad
console.log('MagneticBubbles está disponible en el contexto global:', !!window.MagneticBubbles);

// Notificar cuando el script haya terminado de cargarse
document.dispatchEvent(new CustomEvent('magnetic-bubbles-loaded'));
