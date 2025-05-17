/**
 * Magnetic Bubbles - Un selector de burbujas interactivo inspirado en Magnetic/Apple Music
 * Para MotoMatch Test de Preferencias
 */

console.log('Inicializando MagneticBubbles.js...');

class MagneticBubbles {
  constructor(canvas, options = {}) {
    console.log('Inicializando componente MagneticBubbles...', options);
    
    // Canvas y contexto
    this.canvas = typeof canvas === 'string' ? document.querySelector(canvas) : canvas;
    
    // Verificar si el canvas está disponible
    if (!this.canvas) {
      console.error('Canvas no encontrado. Asegúrate de que el elemento exista.');
      return;
    }
    
    try {
      this.ctx = this.canvas.getContext('2d');
    } catch (error) {
      console.error('Error al obtener el contexto del canvas:', error);
      // Mostrar mensaje de error en el canvas
      this.showErrorMessage();
      return;
    }
    
    if (!this.ctx) {
      console.error('No se pudo obtener el contexto 2D del canvas.');
      this.showErrorMessage();
      return;
    }
    
    // Configuración
    this.options = {
      width: options.width || this.canvas.parentElement.clientWidth || 300,
      height: options.height || 300,
      selectionMode: options.selectionMode || 'single', // 'single' o 'multiple'
      canvasBackground: options.canvasBackground || 'rgba(0, 0, 0, 0.1)',
      bubbleBaseColor: options.bubbleBaseColor || '#f97316',
      bubbleSelectedColor: options.bubbleSelectedColor || '#ea580c',
      textColor: options.textColor || '#ffffff',
      items: options.items || []
    };
    
    // Ajustar dimensiones del canvas
    this.canvas.width = this.options.width;
    this.canvas.height = this.options.height;
    
    // Estado y datos
    this.bubbles = [];
    this.selections = {};
    this.isAnimating = false;
    this.mousePosition = { x: 0, y: 0 };
    this.isDragging = false;
    
    // Inicializar
    console.log(`Configurando burbujas con ${this.options.items.length} elementos`);
    this.initializeData();
    this.setupEventListeners();
    this.startAnimation();
  }
  
  // Mensaje de error visual
  showErrorMessage() {
    if (!this.canvas) return;
    
    // Asegurar que el canvas tenga dimensiones
    if (!this.canvas.width) this.canvas.width = 300;
    if (!this.canvas.height) this.canvas.height = 150;
    
    try {
      const ctx = this.canvas.getContext('2d');
      if (ctx) {
        // Fondo
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Texto de error
        ctx.fillStyle = '#f97316';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Error al cargar. Reintentar', this.canvas.width/2, this.canvas.height/2);
        
        // Hacer que el canvas sea clickeable para reintentar
        this.canvas.style.cursor = 'pointer';
        this.canvas.addEventListener('click', () => {
          location.reload();
        });
      }
    } catch (e) {
      console.error('Error al mostrar mensaje de error en canvas:', e);
    }
  }
  
  // Inicializar datos
  initializeData() {
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const radius = Math.min(centerX, centerY) * 0.7;
    
    // Crear burbujas a partir de los items
    this.bubbles = this.options.items.map((item, index) => {
      // Distribuir en círculo
      const angle = (index / this.options.items.length) * Math.PI * 2;
      const distance = radius * 0.8;
      
      return {
        id: item.id,
        label: item.label,
        x: centerX + Math.cos(angle) * distance,
        y: centerY + Math.sin(angle) * distance,
        radius: 40 + Math.random() * 10,
        color: this.options.bubbleBaseColor,
        baseColor: this.options.bubbleBaseColor,
        selectedColor: this.options.bubbleSelectedColor,
        textColor: this.options.textColor,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        selected: false,
        selectionLevel: 0,
        value: item.value || 1.0
      };
    });
    
    console.log(`Inicializadas ${this.bubbles.length} burbujas`);
  }
  
  // Eventos
  setupEventListeners() {
    // Mouse/Touch eventos
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
    this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
    this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    
    // Touch eventos
    this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
    this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
    this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this));
    
    // Resize
    window.addEventListener('resize', this.handleResize.bind(this));
    
    console.log('Event listeners configurados');
  }
  
  // Manejo de eventos
  handleMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    this.mousePosition = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  }
  
  handleMouseDown(e) {
    this.isDragging = true;
    this.handleInteraction();
  }
  
  handleMouseUp() {
    this.isDragging = false;
  }
  
  handleMouseLeave() {
    this.isDragging = false;
  }
  
  handleTouchStart(e) {
    e.preventDefault();
    if (e.touches.length > 0) {
      const rect = this.canvas.getBoundingClientRect();
      this.mousePosition = {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top
      };
      this.isDragging = true;
      this.handleInteraction();
    }
  }
  
  handleTouchMove(e) {
    e.preventDefault();
    if (e.touches.length > 0) {
      const rect = this.canvas.getBoundingClientRect();
      this.mousePosition = {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top
      };
    }
  }
  
  handleTouchEnd() {
    this.isDragging = false;
  }
  
  handleResize() {
    // Actualizar dimensiones si es necesario
    if (this.canvas.parentElement) {
      this.options.width = this.canvas.parentElement.clientWidth;
      this.canvas.width = this.options.width;
      
      // Reposicionar burbujas
      const centerX = this.canvas.width / 2;
      const centerY = this.canvas.height / 2;
      const radius = Math.min(centerX, centerY) * 0.7;
      
      this.bubbles.forEach((bubble, index) => {
        const angle = (index / this.bubbles.length) * Math.PI * 2;
        const distance = radius * 0.8;
        
        bubble.x = centerX + Math.cos(angle) * distance;
        bubble.y = centerY + Math.sin(angle) * distance;
      });
    }
  }
  
  // Interacción con burbujas
  handleInteraction() {
    if (!this.isDragging) return;
    
    // Verificar qué burbuja fue clickeada
    const clickedBubble = this.bubbles.find(bubble => 
      Math.sqrt(
        Math.pow(this.mousePosition.x - bubble.x, 2) + 
        Math.pow(this.mousePosition.y - bubble.y, 2)
      ) < bubble.radius
    );
    
    if (clickedBubble) {
      if (this.options.selectionMode === 'single') {
        // Deseleccionar todas las demás
        this.bubbles.forEach(bubble => {
          bubble.selected = false;
          bubble.selectionLevel = 0;
        });
        
        // Seleccionar la actual
        clickedBubble.selected = true;
        clickedBubble.selectionLevel = 1.0;
        
      } else {
        // Modo múltiple: toggle o incrementar nivel
        if (!clickedBubble.selected) {
          clickedBubble.selected = true;
          clickedBubble.selectionLevel = 0.25;
        } else {
          // Incrementar nivel en 0.25 (hasta 1.0)
          clickedBubble.selectionLevel += 0.25;
          if (clickedBubble.selectionLevel > 1.0) {
            clickedBubble.selectionLevel = 0;
            clickedBubble.selected = false;
          }
        }
      }
      
      // Actualizar selecciones
      this.updateSelections();
      
      // Disparar evento
      this.dispatchSelectionChangedEvent();
    }
  }
  
  // Actualizar objeto de selecciones
  updateSelections() {
    this.selections = {};
    
    this.bubbles.filter(bubble => bubble.selected).forEach(bubble => {
      this.selections[bubble.id] = bubble.selectionLevel * bubble.value;
    });
    
    console.log('Selecciones actualizadas:', this.selections);
  }
  
  // Disparar evento de cambio de selección
  dispatchSelectionChangedEvent() {
    const event = new CustomEvent('selection-changed', {
      detail: {
        selections: this.selections
      }
    });
    
    this.canvas.dispatchEvent(event);
  }
  
  // Animación
  startAnimation() {
    if (this.isAnimating) return;
    
    this.isAnimating = true;
    this.animate();
  }
  
  stopAnimation() {
    this.isAnimating = false;
  }
  
  animate() {
    if (!this.isAnimating) return;
    
    // Limpiar canvas
    this.ctx.fillStyle = this.options.canvasBackground;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Actualizar y dibujar burbujas
    this.updateBubbles();
    this.drawBubbles();
    
    // Loop
    requestAnimationFrame(this.animate.bind(this));
  }
  
  // Actualizar posición y estado de las burbujas
  updateBubbles() {
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    
    this.bubbles.forEach(bubble => {
      // Movimiento natural
      bubble.x += bubble.vx;
      bubble.y += bubble.vy;
      
      // Gravedad hacia el centro
      const dx = centerX - bubble.x;
      const dy = centerY - bubble.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance > 10) {
        bubble.vx += (dx / distance) * 0.02;
        bubble.vy += (dy / distance) * 0.02;
      }
      
      // Repulsión del mouse
      const mouseDistance = Math.sqrt(
        Math.pow(this.mousePosition.x - bubble.x, 2) + 
        Math.pow(this.mousePosition.y - bubble.y, 2)
      );
      
      if (mouseDistance < 100) {
        const repulsionFactor = (100 - mouseDistance) / 500;
        const repulsionX = (bubble.x - this.mousePosition.x) * repulsionFactor;
        const repulsionY = (bubble.y - this.mousePosition.y) * repulsionFactor;
        
        bubble.vx += repulsionX;
        bubble.vy += repulsionY;
      }
      
      // Fricción
      bubble.vx *= 0.95;
      bubble.vy *= 0.95;
      
      // Límites
      const margin = bubble.radius;
      
      if (bubble.x - margin < 0 || bubble.x + margin > this.canvas.width) {
        bubble.vx *= -0.8;
        bubble.x = Math.max(margin, Math.min(this.canvas.width - margin, bubble.x));
      }
      
      if (bubble.y - margin < 0 || bubble.y + margin > this.canvas.height) {
        bubble.vy *= -0.8;
        bubble.y = Math.max(margin, Math.min(this.canvas.height - margin, bubble.y));
      }
      
      // Actualizar color según selección
      if (bubble.selected) {
        // Incrementar saturación basado en nivel de selección
        bubble.color = this.adjustColorSaturation(
          bubble.selectedColor, 
          0.5 + 0.5 * bubble.selectionLevel
        );
      } else {
        bubble.color = bubble.baseColor;
      }
    });
    
    // Colisión entre burbujas
    for (let i = 0; i < this.bubbles.length; i++) {
      for (let j = i + 1; j < this.bubbles.length; j++) {
        const bubble1 = this.bubbles[i];
        const bubble2 = this.bubbles[j];
        
        const dx = bubble2.x - bubble1.x;
        const dy = bubble2.y - bubble1.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const minDist = bubble1.radius + bubble2.radius;
        
        if (distance < minDist) {
          const angle = Math.atan2(dy, dx);
          const overlap = minDist - distance;
          
          // Separar
          const moveX = (overlap/2) * Math.cos(angle);
          const moveY = (overlap/2) * Math.sin(angle);
          
          bubble1.x -= moveX;
          bubble1.y -= moveY;
          bubble2.x += moveX;
          bubble2.y += moveY;
          
          // Intercambiar velocidades (simplificado)
          const temp = {vx: bubble1.vx, vy: bubble1.vy};
          bubble1.vx = bubble2.vx * 0.8;
          bubble1.vy = bubble2.vy * 0.8;
          bubble2.vx = temp.vx * 0.8;
          bubble2.vy = temp.vy * 0.8;
        }
      }
    }
  }
  
  // Dibujar las burbujas
  drawBubbles() {
    this.bubbles.forEach(bubble => {
      // Dibujar círculo
      this.ctx.beginPath();
      this.ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = bubble.color;
      this.ctx.fill();
      
      // Agregar brillo
      const gradient = this.ctx.createRadialGradient(
        bubble.x - bubble.radius * 0.3,
        bubble.y - bubble.radius * 0.3,
        bubble.radius * 0.05,
        bubble.x,
        bubble.y,
        bubble.radius
      );
      
      gradient.addColorStop(0, 'rgba(255, 255, 255, 0.35)');
      gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
      
      this.ctx.beginPath();
      this.ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = gradient;
      this.ctx.fill();
      
      // Dibujar texto
      this.ctx.fillStyle = bubble.textColor;
      this.ctx.font = 'bold 14px Arial';
      this.ctx.textAlign = 'center';
      this.ctx.textBaseline = 'middle';
      this.ctx.fillText(bubble.label, bubble.x, bubble.y);
      
      // Indicador de nivel para selecciones múltiples
      if (bubble.selected && this.options.selectionMode === 'multiple') {
        // Dibujar pequeños puntos para indicar nivel
        for (let i = 1; i <= 4; i++) {
          const isActive = bubble.selectionLevel >= (i * 0.25);
          this.ctx.beginPath();
          this.ctx.arc(
            bubble.x + bubble.radius * 0.7,
            bubble.y - bubble.radius * 0.7 + i * 8,
            3,
            0, Math.PI * 2
          );
          this.ctx.fillStyle = isActive ? '#ffffff' : 'rgba(255, 255, 255, 0.3)';
          this.ctx.fill();
        }
      }
    });
  }
  
  // Ajustar saturación de color
  adjustColorSaturation(hexColor, saturationFactor) {
    // Convertir hex a rgb
    const r = parseInt(hexColor.slice(1, 3), 16) / 255;
    const g = parseInt(hexColor.slice(3, 5), 16) / 255;
    const b = parseInt(hexColor.slice(5, 7), 16) / 255;
    
    // Encontrar máximo y mínimo
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    
    // Calcular luminosidad
    const l = (max + min) / 2;
    
    // Si es gris, no hay saturación
    if (max === min) {
      return hexColor;
    }
    
    // Calcular saturación
    let s = l > 0.5 ? 
      (max - min) / (2 - max - min) : 
      (max - min) / (max + min);
    
    // Ajustar saturación
    s = Math.min(1, s * saturationFactor);
    
    // Calcular matiz
    let h;
    if (max === r) {
      h = (g - b) / (max - min) + (g < b ? 6 : 0);
    } else if (max === g) {
      h = (b - r) / (max - min) + 2;
    } else {
      h = (r - g) / (max - min) + 4;
    }
    h /= 6;
    
    // Función para convertir HSL a RGB
    function hslToRgb(h, s, l) {
      let r, g, b;
      
      if (s === 0) {
        r = g = b = l;
      } else {
        const hue2rgb = (p, q, t) => {
          if (t < 0) t += 1;
          if (t > 1) t -= 1;
          if (t < 1/6) return p + (q - p) * 6 * t;
          if (t < 1/2) return q;
          if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
          return p;
        };
        
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;
        
        r = hue2rgb(p, q, h + 1/3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1/3);
      }
      
      return [
        Math.round(r * 255),
        Math.round(g * 255),
        Math.round(b * 255)
      ];
    }
    
    // Convertir de nuevo a RGB
    const rgb = hslToRgb(h, s, l);
    
    // Convertir a hex
    return '#' + rgb.map(c => {
      const hex = c.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }
  
  // Métodos públicos
  getSelections() {
    return this.selections;
  }
  
  reset() {
    this.bubbles.forEach(bubble => {
      bubble.selected = false;
      bubble.selectionLevel = 0;
    });
    
    this.selections = {};
    this.dispatchSelectionChangedEvent();
  }
  
  destroy() {
    this.stopAnimation();
    
    // Eliminar event listeners
    this.canvas.removeEventListener('mousemove', this.handleMouseMove);
    this.canvas.removeEventListener('mousedown', this.handleMouseDown);
    this.canvas.removeEventListener('mouseup', this.handleMouseUp);
    this.canvas.removeEventListener('mouseleave', this.handleMouseLeave);
    this.canvas.removeEventListener('touchstart', this.handleTouchStart);
    this.canvas.removeEventListener('touchmove', this.handleTouchMove);
    this.canvas.removeEventListener('touchend', this.handleTouchEnd);
    window.removeEventListener('resize', this.handleResize);
    
    console.log('MagneticBubbles destruido');
  }
}

// Exportar al contexto global para usarlo desde HTML
window.MagneticBubbles = MagneticBubbles;

// Confirmar disponibilidad
console.log('MagneticBubbles cargado y disponible globalmente');