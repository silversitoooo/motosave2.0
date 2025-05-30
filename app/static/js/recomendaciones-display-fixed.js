/**
 * Script para gestionar las recomendaciones de motos
 * Versión simplificada y optimizada (26-Mayo-2025)
 */

document.addEventListener("DOMContentLoaded", () => {
    console.log("🏍️ Inicializando gestor de recomendaciones...");
    
    // Obtener datos de recomendaciones de múltiples fuentes
    let motosRecomendadas = [];
    
    // 1. Intentar desde window.motosRecomendadas 
    if (window.motosRecomendadas && Array.isArray(window.motosRecomendadas) && window.motosRecomendadas.length > 0) {
        console.log("✅ Recomendaciones desde window.motosRecomendadas:", window.motosRecomendadas.length);
        motosRecomendadas = window.motosRecomendadas;
    } 
    // 2. Intentar desde elemento JSON embebido
    else {
        const jsonElement = document.getElementById('recommendations-data');
        if (jsonElement && jsonElement.textContent) {
            try {
                const data = JSON.parse(jsonElement.textContent);
                if (Array.isArray(data) && data.length > 0) {
                    console.log("✅ Recomendaciones desde elemento JSON:", data.length);
                    motosRecomendadas = data;
                }
            } catch (e) {
                console.error("❌ Error al parsear JSON:", e);
                console.log("📝 Contenido del elemento JSON:", jsonElement.textContent);
            }
        }
    }
    
    // DEBUG: Mostrar lo que tenemos
    console.log("📊 Datos finales para procesar:", motosRecomendadas);
    
    // Obtener contenedor
    const gridContainer = document.querySelector('.grid-container');
    if (!gridContainer) {
        console.error("❌ Contenedor .grid-container no encontrado");
        // Intentar encontrar contenedor alternativo
        const altContainer = document.querySelector('.recomendaciones-container') || 
                           document.querySelector('.container') ||
                           document.querySelector('#recomendaciones-grid');
        if (altContainer) {
            console.log("✅ Usando contenedor alternativo:", altContainer.className);
            altContainer.innerHTML = ''; // Limpiar
            processRecommendations(motosRecomendadas, altContainer);
            return;
        } else {
            console.error("❌ No se encontró ningún contenedor válido");
            return;
        }
    }
    
    // Limpiar contenedor principal
    gridContainer.innerHTML = '';
    
    // Procesar recomendaciones
    processRecommendations(motosRecomendadas, gridContainer);
});

function processRecommendations(motosRecomendadas, container) {
    // Si no hay recomendaciones, mostrar mensaje
    if (!motosRecomendadas || motosRecomendadas.length === 0) {
        console.warn("⚠️ No hay recomendaciones para mostrar");
                container.innerHTML = `
            <div class="no-recommendations">
                <i class="fas fa-exclamation-circle"></i>
                <h3>No hay recomendaciones disponibles</h3>
                <p>Por favor completa el test de preferencias para obtener recomendaciones personalizadas.</p>
                <a href="/test" class="nav-button">Hacer el test</a>
            </div>
        `;
        return;
    }
    
    console.log(`🎯 Procesando ${motosRecomendadas.length} recomendaciones`);
    
    // Renderizar cada moto
    motosRecomendadas.forEach((moto, index) => {
        console.log(`📝 Procesando moto ${index + 1}:`, moto);
        
        const motoCard = document.createElement('div');
        motoCard.className = 'moto-card';
        motoCard.style.opacity = "0";
        motoCard.style.transform = "translateY(20px)";
        motoCard.style.transition = "all 0.5s ease";
        
        // Extraer datos con diferentes formatos posibles
        let motoData = {};
        
        // Si la moto es un objeto directo
        if (typeof moto === 'object' && moto !== null) {
            motoData = {
                moto_id: moto.moto_id || moto.id || index,
                marca: moto.marca || 'Marca Desconocida',
                modelo: moto.modelo || 'Modelo Desconocido',
                precio: moto.precio || 0,
                año: moto.anio || moto.año || moto.anyo || 'N/D',
                cilindrada: moto.cilindrada || 'N/D',
                potencia: moto.potencia || 'N/D',
                tipo: moto.tipo || moto.estilo || 'N/D',
                imagen: moto.imagen || '/static/images/default-moto.jpg',
                score: moto.score || 0,
                reasons: moto.reasons || moto.razones || ['Recomendación personalizada'],
                url: moto.URL || moto.url || moto.link || '#' // Asegura que se use la URL correcta
            };
        }
        
        // Formatear valores para mostrar
        const precioFormateado = motoData.precio ? `€${Number(motoData.precio).toLocaleString()}` : 'Precio no disponible';
        const cilindradaFormateada = motoData.cilindrada !== 'N/D' ? `${motoData.cilindrada} cc` : 'N/D';
        const potenciaFormateada = motoData.potencia !== 'N/D' ? `${motoData.potencia} CV` : 'N/D';
        const scoreFormateado = typeof motoData.score === 'number' ? Math.round(motoData.score * 100) : 0;
        
        // Asegurar que reasons es un array
        let reasons = [];
        if (Array.isArray(motoData.reasons)) {
            reasons = motoData.reasons;
        } else if (typeof motoData.reasons === 'string') {
            reasons = [motoData.reasons];
        } else {
            reasons = ['Recomendación personalizada basada en tus preferencias'];
        }
        
        // Crear HTML de la tarjeta
        motoCard.innerHTML = `
            <div class="moto-image-container">
            <img src="${motoData.imagen}" 
             alt="${motoData.marca} ${motoData.modelo}" 
             class="moto-img" 
             onerror="this.src='/static/images/default-moto.jpg'; console.log('Error cargando imagen:', this.getAttribute('src'));">
            </div>
            
            <div class="moto-info">
            <h3 class="moto-title">${motoData.marca} ${motoData.modelo}</h3>
            
            <div class="moto-specs">
            <p><strong>Año:</strong> ${motoData.año}</p>
            <p><strong>Tipo:</strong> ${motoData.tipo}</p>
            <p><strong>Cilindrada:</strong> ${cilindradaFormateada}</p>
            <p><strong>Potencia:</strong> ${potenciaFormateada}</p>
            <p><strong>Precio:</strong> ${precioFormateado}</p>
            </div>
            
            <div class="match-score">
            <span class="score-label">Coincidencia:</span>
            <div class="score-bar">
            <div class="score-fill" style="width: ${scoreFormateado}%;"></div>
            </div>
            <span class="score-percentage">${scoreFormateado}%</span>
            </div>
            
            <div class="reasons-container">
            <h4>¿Por qué te recomendamos esta moto?</h4>
            <ul class="reasons-list">
            ${reasons.map(reason => `<li><i class="fas fa-check-circle"></i> ${reason}</li>`).join('')}
            </ul>
            </div>
            <div class="moto-actions">
            <button class="btn-moto-ideal" onclick="marcarComoIdeal('${motoData.moto_id}', '${motoData.marca}', '${motoData.modelo}')">
            <i class="fas fa-star"></i> Moto Ideal
            </button>
            <button class="btn-like" onclick="darLike('${motoData.moto_id}', '${motoData.marca}', '${motoData.modelo}')">
            <i class="fas fa-heart"></i> Like
            </button>
            <button class="btn-detalles" onclick="window.open('${motoData.url}', '_blank')">
            <i class="fas fa-info-circle"></i> Ver detalles
            </button>
            </div>
            </div>
        `;
        

        // Añadir al contenedor
        container.appendChild(motoCard);
        
        // Animación de entrada escalonada
        setTimeout(() => {
            motoCard.style.opacity = "1";
            motoCard.s
tyle.transform = "translateY(0)";
        }, index * 150);
    });
    
    console.log(`✅ ${motosRecomendadas.length} recomendaciones renderizadas correctamente`);
}

// Funciones para manejar acciones de las motos
function marcarComoIdeal(motoId, marca, modelo) {
    console.log(`⭐ Marcando moto ${motoId} (${marca} ${modelo}) como ideal`);
    
    // Confirmar acción
    if (!confirm(`¿Estás seguro de que quieres marcar la ${marca} ${modelo} como tu moto ideal?`)) {
        return;
    }
    
    // Enviar solicitud al servidor
    fetch('/marcar_moto_ideal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            moto_id: motoId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`¡${marca} ${modelo} ha sido marcada como tu moto ideal!`);
            // Cambiar el estilo del botón para indicar que está seleccionada
            const button = document.querySelector(`button[onclick*="${motoId}"][onclick*="marcarComoIdeal"]`);
            if (button) {
                button.innerHTML = '<i class="fas fa-star"></i> ¡Moto Ideal!';
                button.classList.add('btn-ideal-selected');
                button.disabled = true;
            }
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error al marcar como ideal:', error);
        alert('Error al marcar la moto como ideal. Intenta de nuevo.');
    });
}

function darLike(motoId, marca, modelo) {
    console.log(`❤️ Dando like a moto ${motoId} (${marca} ${modelo})`);
    
    // Enviar solicitud al servidor
    fetch('/dar_like_moto', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            moto_id: motoId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`¡Has dado like a la ${marca} ${modelo}!`);
            // Cambiar el estilo del botón para indicar que se dio like
            const button = document.querySelector(`button[onclick*="${motoId}"][onclick*="darLike"]`);
            if (button) {
                button.innerHTML = '<i class="fas fa-heart"></i> ¡Con Like!';
                button.classList.add('btn-like-selected');
                button.onclick = () => quitarLike(motoId, marca, modelo);
            }
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error al dar like:', error);
        alert('Error al dar like. Intenta de nuevo.');
    });
}

function quitarLike(motoId, marca, modelo) {
    console.log(`💔 Quitando like de moto ${motoId} (${marca} ${modelo})`);
    
    // Enviar solicitud al servidor
    fetch('/quitar_like_moto', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            moto_id: motoId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Has quitado el like de la ${marca} ${modelo}`);
            // Restaurar el botón original
            const button = document.querySelector(`button[onclick*="${motoId}"][onclick*="quitarLike"]`);
            if (button) {
                button.innerHTML = '<i class="fas fa-heart"></i> Like';
                button.classList.remove('btn-like-selected');
                button.onclick = () => darLike(motoId, marca, modelo);
            }
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error al quitar like:', error);
        alert('Error al quitar like. Intenta de nuevo.');
    });
}

function verDetalles(motoId) {
    console.log(`📋 Viendo detalles de moto ${motoId}`);
    // Redirigir a página de detalles
    window.location.href = `/moto-detail/${motoId}`;
}
