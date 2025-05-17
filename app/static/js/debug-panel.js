// Panel de diagnóstico para ayudar a depurar los problemas
document.addEventListener('DOMContentLoaded', function() {
  // Crear panel de diagnóstico
  const debugPanel = document.createElement('div');
  debugPanel.id = 'debug-panel';
  debugPanel.style.cssText = `
    position: fixed;
    bottom: 10px;
    right: 10px;
    background: rgba(0,0,0,0.8);
    color: white;
    padding: 10px;
    border-radius: 5px;
    font-size: 12px;
    z-index: 9999;
    max-width: 300px;
    max-height: 150px;
    overflow: auto;
    border: 1px solid #f97316;
  `;
  
  // Añadir contenido inicial
  debugPanel.innerHTML = `
    <div><strong>Estado de scripts:</strong> Verificando...</div>
    <div><strong>MagneticBubbles:</strong> <span id="debug-magnetic">No cargado</span></div>
    <div><strong>Burbujas:</strong> <span id="debug-bubbles">No inicializadas</span></div>
    <div><strong>Selecciones:</strong> <span id="debug-selections">Vacías</span></div>
    <button id="debug-toggle" style="margin-top:5px;background:#f97316;border:none;color:white;padding:3px 8px;border-radius:3px;">Ocultar</button>
  `;
  
  // Añadir al cuerpo
  document.body.appendChild(debugPanel);
  
  // Manejar visibilidad
  document.getElementById('debug-toggle').addEventListener('click', function() {
    if (this.textContent === 'Ocultar') {
      debugPanel.style.height = '20px';
      debugPanel.style.overflow = 'hidden';
      this.textContent = 'Mostrar';
    } else {
      debugPanel.style.height = 'auto';
      debugPanel.style.maxHeight = '150px';
      debugPanel.style.overflow = 'auto';
      this.textContent = 'Ocultar';
    }
  });
    // Función para actualizar estado
  window.updateDebugPanel = function() {
    const magneticStatus = typeof window.MagneticBubbles === 'function' ? 'Cargado ✅' : 'No disponible ❌';
    document.getElementById('debug-magnetic').textContent = magneticStatus;
    document.getElementById('debug-magnetic').style.color = magneticStatus.includes('✅') ? '#4ade80' : '#f43f5e';
    
    const bubblesInitialized = (window.estilosBubbles || window.marcasBubbles) ? 'Inicializadas ✅' : 'No inicializadas ❌';
    document.getElementById('debug-bubbles').textContent = bubblesInitialized;
    document.getElementById('debug-bubbles').style.color = bubblesInitialized.includes('✅') ? '#4ade80' : '#f43f5e';
    
    const selecciones = window.respuestas || {};
    const tieneSelecciones = 
      Object.keys(selecciones.estilos || {}).length > 0 || 
      Object.keys(selecciones.marcas || {}).length > 0;
    
    const selectionStatus = tieneSelecciones ? 'Con datos ✅' : 'Vacías ❌';
    document.getElementById('debug-selections').textContent = selectionStatus;
    document.getElementById('debug-selections').style.color = selectionStatus.includes('✅') ? '#4ade80' : '#f43f5e';
    
    // Añadir detalles específicos de las selecciones si hay datos
    if (tieneSelecciones) {
      const selectionDetails = [];
      
      if (Object.keys(selecciones.estilos || {}).length > 0) {
        selectionDetails.push(`Estilos: ${Object.keys(selecciones.estilos).length}`);
      }
      
      if (Object.keys(selecciones.marcas || {}).length > 0) {
        selectionDetails.push(`Marcas: ${Object.keys(selecciones.marcas).length}`);
      }
      
      if (selectionDetails.length > 0) {
        document.getElementById('debug-selections').textContent += ` (${selectionDetails.join(', ')})`;
      }
    }
  };
  
  // Actualizar cada segundo
  setInterval(window.updateDebugPanel, 1000);
});
