/**
 * Helpers para manejar sliders numéricos y su captura de datos.
 * Este archivo contiene utilidades para garantizar la correcta captura
 * de valores numéricos de sliders en el test.
 */

const SliderManager = {
  /**
   * Inicializa un par de sliders para rango (mínimo y máximo)
   * 
   * @param {Object} options - Opciones de configuración
   * @param {string} options.minSliderId - ID del slider mínimo
   * @param {string} options.maxSliderId - ID del slider máximo
   * @param {string} options.minDisplayId - ID del elemento que muestra el valor mínimo
   * @param {string} options.maxDisplayId - ID del elemento que muestra el valor máximo
   * @param {string} options.progressId - ID del elemento que muestra el progreso visual
   * @param {Function} options.formatFn - Función para formatear los valores (opcional)
   * @param {Object} options.defaults - Valores por defecto {min, max}
   * @param {Object} options.storage - Objetos para almacenar los valores {testResults, respuestas}
   * @param {string} options.storageKey - Nombre base para almacenar los valores ('presupuesto', 'cilindrada', etc)
   */
  initRangeSlider: function(options) {
    // Elementos DOM
    const minSlider = document.getElementById(options.minSliderId);
    const maxSlider = document.getElementById(options.maxSliderId);
    const minDisplay = document.getElementById(options.minDisplayId);
    const maxDisplay = document.getElementById(options.maxDisplayId);
    const rangeProgress = document.getElementById(options.progressId);
    
    if (!minSlider || !maxSlider) {
      console.error(`Sliders no encontrados: ${options.minSliderId}, ${options.maxSliderId}`);
      return;
    }
    
    // Formatear función
    const formatValue = options.formatFn || ((v) => `Q${v.toLocaleString()}`);
    
    // Función para actualizar visualización
    function updateRangeDisplay() {
      // Obtener valores actuales como números
      let minVal = parseInt(minSlider.value, 10);
      let maxVal = parseInt(maxSlider.value, 10);
      
      // Asegurar validez
      if (isNaN(minVal)) minVal = options.defaults.min;
      if (isNaN(maxVal)) maxVal = options.defaults.max;
      
      // Asegurar que min <= max
      if (minVal > maxVal) {
        if (minSlider === document.activeElement) {
          maxVal = Math.min(minVal + 1000, parseInt(maxSlider.max, 10));
          maxSlider.value = maxVal;
        } else {
          minVal = Math.max(maxVal - 1000, parseInt(minSlider.min, 10));
          minSlider.value = minVal;
        }
      }
      
      // Actualizar displays
      if (minDisplay) minDisplay.textContent = formatValue(minVal);
      if (maxDisplay) maxDisplay.textContent = formatValue(maxVal);
      
      // Actualizar barra de progreso
      if (rangeProgress) {
        const minPercent = ((minVal - parseInt(minSlider.min, 10)) / 
                          (parseInt(minSlider.max, 10) - parseInt(minSlider.min, 10))) * 100;
        const maxPercent = ((maxVal - parseInt(minSlider.min, 10)) / 
                          (parseInt(maxSlider.max, 10) - parseInt(minSlider.min, 10))) * 100;
                          
        rangeProgress.style.left = `${minPercent}%`;
        rangeProgress.style.width = `${maxPercent - minPercent}%`;
      }
      
      // Guardar valores como NÚMEROS en los objetos de estado
      const minKey = `${options.storageKey}_min`;
      const maxKey = `${options.storageKey}_max`;
      
      // Guardar valores en el estado
      if (options.storage.testResults) {
        options.storage.testResults[minKey] = minVal;
        options.storage.testResults[maxKey] = maxVal;
      }
      
      if (options.storage.respuestas) {
        options.storage.respuestas[minKey] = minVal;
        options.storage.respuestas[maxKey] = maxVal;
      }
      
      // Guardar en localStorage para recuperación
      try {
        localStorage.setItem(minKey, minVal.toString());
        localStorage.setItem(maxKey, maxVal.toString());
      } catch (e) {
        console.warn("Error guardando en localStorage:", e);
      }
      
      // Guardar como data attributes para acceso directo
      minSlider.dataset.currentValue = minVal;
      maxSlider.dataset.currentValue = maxVal;
      
      return { min: minVal, max: maxVal };
    }
    
    // Eventos
    minSlider.addEventListener('input', updateRangeDisplay);
    maxSlider.addEventListener('change', updateRangeDisplay);
    maxSlider.addEventListener('input', updateRangeDisplay);
    minSlider.addEventListener('change', updateRangeDisplay);
    
    // Restaurar valores guardados
    try {
      const savedMin = localStorage.getItem(`${options.storageKey}_min`);
      const savedMax = localStorage.getItem(`${options.storageKey}_max`);
      
      if (savedMin) minSlider.value = savedMin;
      if (savedMax) maxSlider.value = savedMax;
    } catch (e) {
      console.warn("Error restaurando valores:", e);
    }
    
    // Inicializar visualización
    updateRangeDisplay();
    
    return {
      updateDisplay: updateRangeDisplay,
      getCurrentValues: () => ({
        min: parseInt(minSlider.value, 10),
        max: parseInt(maxSlider.value, 10)
      })
    };
  },
  
  /**
   * Captura valores de los sliders definidos en la página
   * @returns {Object} Todos los valores numéricos capturados
   */
  captureAllSliderValues: function() {
    const result = {};
    
    // Buscar todos los sliders numéricos
    document.querySelectorAll('input[type="range"][data-capture="true"]').forEach(slider => {
      if (slider.id && slider.dataset.currentValue) {
        result[slider.id] = parseInt(slider.dataset.currentValue, 10);
      } else if (slider.id) {
        result[slider.id] = parseInt(slider.value, 10);
      }
    });
    
    return result;
  }
};

// Exponer globalmente
window.SliderManager = SliderManager;
console.log("Módulo de gestión de sliders numéricos cargado");
