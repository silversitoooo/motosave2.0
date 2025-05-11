/**
 * test_finalizacion.js
 * Script para manejar la finalización del test de preferencias
 * y enviar los datos al servidor.
 */

// Preparar confeti para el modal de finalización
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
  const colors = [
    '#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', 
    '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4CAF50', 
    '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800', '#FF5722'
  ];
  
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
  
  return true;
}

// Función para finalizar el test y enviar datos al servidor
function finalizarTest() {
  // Detener cualquier animación o proceso pendiente
  const listaIntervalos = ['estilosInterval', 'marcasInterval'];
  listaIntervalos.forEach(intervalo => {
    if (window[intervalo]) {
      clearInterval(window[intervalo]);
      window[intervalo] = null;
    }
  });
  
  // Detener Matter.js para liberar recursos
  if (typeof Matter !== 'undefined' && window.render) {
    Matter.Render.stop(window.render);
    
    if (window.engine) {
      Matter.Engine.clear(window.engine);
    }
  }
  
  // Recopilar todas las respuestas
  const datosTest = window.respuestas || {};
  console.log('Enviando datos del test:', datosTest);
  
  // Verificar datos mínimos
  if (!datosTest.estilos || Object.keys(datosTest.estilos).length === 0) {
    console.warn('Advertencia: No se seleccionaron estilos de moto');
  }
  
  if (!datosTest.marcas || Object.keys(datosTest.marcas).length === 0) {
    console.warn('Advertencia: No se seleccionaron marcas de moto');
  }
  
  // Crear un formulario oculto para enviar los datos
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '/recomendaciones';
  
  // Añadir los datos como campos ocultos
  for (const key in datosTest) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = key;
    
    // Si es un objeto, convertir a JSON
    if (typeof datosTest[key] === 'object') {
      input.value = JSON.stringify(datosTest[key]);
    } else {
      input.value = datosTest[key] || '';
    }
    
    form.appendChild(input);
  }
  
  // Añadir el formulario al documento y enviarlo
  document.body.appendChild(form);
  form.submit();
}

// Hacer la función disponible globalmente
window.finalizarTest = finalizarTest;
window.launchConfetti = launchConfetti;

// Al cargar el documento, verificar si hay datos de sesiones anteriores
document.addEventListener('DOMContentLoaded', function() {
  console.log('test_finalizacion.js cargado correctamente');
  
  // Si hay un botón de finalización, asegurarnos de que tenga el evento correcto
  const finishBtn = document.getElementById('finish-btn');
  if (finishBtn) {
    finishBtn.onclick = window.finalizarTest;
  }
});
