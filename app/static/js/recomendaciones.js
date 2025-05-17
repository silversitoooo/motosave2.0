// Procesamiento de los datos de recomendaciones
document.addEventListener("DOMContentLoaded", () => {
    console.log("Cargando recomendaciones...");
    
    // Verificar si los datos han sido cargados correctamente
    // Si hay un error en window.motosRecomendadas, intentar analizar desde data-recommendations
    let motosRecomendadas;
    try {
        if (typeof window.motosRecomendadas !== 'undefined') {
            motosRecomendadas = window.motosRecomendadas;
            console.log("Datos obtenidos desde window.motosRecomendadas");
        } else {
            console.warn("window.motosRecomendadas no está definido, intentando cargar desde dato embebido");
            // Intentamos cargar desde un atributo data
            const dataElement = document.getElementById('recommendations-data');
            if (dataElement) {
                try {
                    motosRecomendadas = JSON.parse(dataElement.textContent);
                    console.log("Datos cargados desde elemento recommendations-data");
                } catch (parseError) {
                    console.error("Error al analizar JSON:", parseError);
                    motosRecomendadas = [];
                }
            } else {
                console.error("No se encontró fuente de datos para recomendaciones");
                motosRecomendadas = [];
            }
        }
    } catch (e) {
        console.error("Error al cargar datos de recomendaciones:", e);
        motosRecomendadas = [];
    }
      // Referencia al contenedor de la cuadrícula
    const gridContainer = document.querySelector('.grid-container');
    
    if (!gridContainer) {
        console.error("No se encontró el contenedor de cuadrícula para mostrar las recomendaciones");
        return;
    }
    
    // Limpiar el contenedor (por si ya contiene elementos)
    gridContainer.innerHTML = '';
    
    // Si no hay recomendaciones o está vacío
    if (!motosRecomendadas || motosRecomendadas.length === 0) {
        console.warn("No se encontraron recomendaciones para mostrar");
        gridContainer.innerHTML = `
            <div class="no-recommendations">
                <i class="fas fa-exclamation-circle"></i>
                <h3>No hay recomendaciones disponibles</h3>
                <p>Por favor completa el test de preferencias para obtener recomendaciones personalizadas.</p>
                <a href="/test" class="nav-button">Hacer el test</a>
            </div>
        `;
        return;
    }
    
    // Generar el HTML para cada moto recomendada
    motosRecomendadas.forEach(moto => {
        // Verificar que todos los datos necesarios estén presentes
        console.log("Procesando moto:", moto);
        
        // Crear el elemento de la tarjeta
        const motoCard = document.createElement('div');
        motoCard.className = 'moto-card';
        
        // Razones formateadas como lista
        const reasonsList = moto.razones && moto.razones.length > 0 
            ? `<ul class="reasons-list">
                ${moto.razones.map(razon => `<li><i class="fas fa-check"></i> ${razon}</li>`).join('')}
               </ul>`
            : '<p>No hay razones específicas para esta recomendación.</p>';
            
        // Formato de puntuación
        const scorePercentage = Math.round((moto.score || 0) * 100);
        
        // Construir el HTML interno de la tarjeta
        motoCard.innerHTML = `
            <img src="${moto.imagen || '/static/images/moto-placeholder.jpg'}" 
                 alt="Imagen de ${moto.modelo}" 
                 class="moto-img"
                 onerror="this.onerror=null; this.src='/static/images/moto-placeholder.jpg';">
            <h3>${moto.modelo || 'Modelo desconocido'}</h3>
            <p><strong>Marca:</strong> ${moto.marca || 'Desconocida'}</p>
            <p><strong>Estilo:</strong> ${moto.estilo || 'N/A'}</p>
            <p><strong>Precio:</strong> Q${moto.precio ? moto.precio.toLocaleString() : 'Precio no disponible'}</p>
            <div class="match-score">
                <span class="score-label">Coincidencia:</span>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${scorePercentage}%;"></div>
                </div>
                <span class="score-percentage">${scorePercentage}%</span>
            </div>
            <div class="reasons-container">
                <h4>¿Por qué te la recomendamos?</h4>
                ${reasonsList}
            </div>
            <button class="favorita-btn" data-modelo="${moto.modelo}" data-id="${moto.moto_id || ''}">
                <i class="fas fa-star"></i> Marcar como Favorita
            </button>
        `;
        
        // Añadir la tarjeta al contenedor
        gridContainer.appendChild(motoCard);
    });
      // Configurar eventos para los botones de favoritos
    const botones = document.querySelectorAll(".favorita-btn");
    botones.forEach(boton => {
        boton.addEventListener("click", () => {
            // Remover selección previa
            botones.forEach(b => b.classList.remove("seleccionada"));
            
            // Marcar actual
            boton.classList.add("seleccionada");
            
            const modelo = boton.dataset.modelo;
            const motoId = boton.dataset.id;
            console.log(`Moto favorita seleccionada: ${modelo} (ID: ${motoId})`);
            
            // Recopilar razones de la moto seleccionada
            const moto = window.motosRecomendadas.find(m => m.modelo === modelo);
            const reasons = moto ? moto.razones : [];
            
            // Enviar al servidor
            fetch('/guardar_moto_ideal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'moto_id': motoId,
                    'reasons': JSON.stringify(reasons)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('¡Moto guardada como tu moto ideal!');
                } else {
                    alert('Error al guardar: ' + (data.error || 'Ocurrió un problema desconocido'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al comunicarse con el servidor');
            });
        });
    });
});