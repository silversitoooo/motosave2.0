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
    // Recopilar todos los datos del test
    var testData = window.testResults || {};
    
    // Añadir experiencia y presupuesto
    let experiencia = document.getElementById('experiencia').value || 'inexperto';
    testData.experiencia = experiencia;
    
    // Obtener presupuesto según la rama
    if (experiencia === 'inexperto') {
        testData.presupuesto = document.getElementById('presupuesto').value || '8000';
    } else {
        // Convertir rango de precio a valor
        let precioExperto = document.getElementById('precio-experto').value || 'medio';
        let valorPresupuesto = '8000'; // Valor por defecto
        switch (precioExperto) {
            case 'bajo': valorPresupuesto = '5000'; break;
            case 'medio_bajo': valorPresupuesto = '8000'; break;
            case 'medio': valorPresupuesto = '12000'; break;
            case 'alto': valorPresupuesto = '18000'; break;
            case 'muy_alto': valorPresupuesto = '25000'; break;
        }
        testData.presupuesto = valorPresupuesto;
    }
    
    // Obtener uso según la rama
    if (experiencia === 'inexperto') {
        testData.uso = document.getElementById('uso').value || '';
    } else {
        testData.uso = document.getElementById('uso_experto').value || '';
    }
    
    // NUEVO: Añadir flag de reset para forzar nueva recomendación
    testData.reset_recommendation = 'true';
    
    console.log("Datos finales del test:", testData);
    
    // Enviar datos mediante POST
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/guardar_test';  // Una nueva ruta específica para guardar
    
    // Añadir los datos como campos ocultos
    for (var key in testData) {
        if (testData.hasOwnProperty(key)) {
            var hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = testData[key];
            form.appendChild(hiddenField);
        }
    }
    
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
