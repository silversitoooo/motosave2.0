/**
 * Script para gestionar las recomendaciones de motos
 * Este script asegura que se muestren las 6 mejores motos según los resultados del test
 */

document.addEventListener("DOMContentLoaded", () => {
    console.log("Inicializando gestor de recomendaciones...");
    
    // Intentar obtener datos de recomendaciones desde múltiples fuentes
    let motosRecomendadas = [];
    
    // Fuente 1: Variable global window.motosRecomendadas
    if (window.motosRecomendadas && Array.isArray(window.motosRecomendadas) && window.motosRecomendadas.length > 0) {
        console.log("Recomendaciones encontradas en window.motosRecomendadas:", window.motosRecomendadas.length);
        motosRecomendadas = window.motosRecomendadas;
    } else {
        console.log("No se encontraron recomendaciones en window.motosRecomendadas");
        
        // Fuente 2: Elemento JSON en la página
        const jsonElement = document.getElementById('recommendations-data');
        if (jsonElement) {
            try {
                const data = JSON.parse(jsonElement.textContent);
                if (Array.isArray(data) && data.length > 0) {
                    console.log("Recomendaciones encontradas en elemento HTML:", data.length);
                    motosRecomendadas = data;
                }
            } catch (e) {
                console.error("Error al analizar datos JSON:", e);
            }
        }
    }
    
    // Referencia al contenedor principal
    const gridContainer = document.querySelector('.grid-container');
    if (!gridContainer) {
        console.error("Contenedor de cuadrícula no encontrado");
        return;
    }
    
    // Limpiamos cualquier contenido previo
    gridContainer.innerHTML = '';
      // Si no hay recomendaciones, mostrar mensaje
    if (motosRecomendadas.length === 0) {
        gridContainer.innerHTML = `
            <div class="no-recommendations">
                <i class="fas fa-exclamation-circle"></i>
                <h3>No hay recomendaciones disponibles</h3>
                <p>Por favor completa el test de preferencias para obtener 6 recomendaciones personalizadas.</p>
                <a href="/test" class="nav-button">Hacer el test</a>
            </div>
        `;
        return;
    }// Renderizar directamente las 6 mejores recomendaciones en el formato de cuadrícula
    console.log("Motos recomendadas:", motosRecomendadas);
    console.log(`Mostrando ${motosRecomendadas.length} recomendaciones (esperadas: 6)`);
    
    motosRecomendadas.forEach((moto, index) => {
        console.log(`Moto ${index}:`, moto);
        const motoCard = document.createElement('div');
        motoCard.className = 'moto-card';
        
        // Usar opacity 0 inicialmente para animar entrada
        motoCard.style.opacity = "0";
        motoCard.style.transform = "translateY(20px)";
        
        // Formatear valores correctamente
        const precio = moto.precio ? `€${moto.precio.toLocaleString()}` : 'N/D';
        const año = moto.año || moto.anio || 'N/D';
        const cilindrada = moto.cilindrada ? `${moto.cilindrada} cc` : 'N/D';
        
        // Formatear potencia correctamente con unidad
        const potencia = moto.potencia ? `${moto.potencia} CV` : 'N/D';
        
        // Añadir el score de la recomendación (porcentaje de coincidencia)
        const score = moto.score ? `${Math.round(moto.score * 100)}%` : 'N/D';
        
        motoCard.innerHTML = `
            <img src="${moto.imagen || '/static/images/default-moto.jpg'}" alt="${moto.marca} ${moto.modelo}" class="moto-img">
            <h3>${moto.marca} ${moto.modelo}</h3>
            <div class="moto-specs">
                <span class="specs-year">${año}</span>
                <span class="specs-divider">•</span>
                <span class="specs-power">${potencia}</span>
            </div>
            <div class="moto-score">
                <span class="score-label">Coincidencia:</span>
                <span class="score-value">${score}</span>
                <div class="score-bar" style="width: ${moto.score ? moto.score * 100 : 0}%;"></div>
            </div>
            <div class="moto-details">
                <p><strong>Tipo:</strong> ${moto.tipo || moto.estilo || 'N/D'}</p>
                <p><strong>Cilindrada:</strong> ${cilindrada}</p>
                <p><strong>Precio:</strong> ${precio}</p>
            </div>
            <div class="action-buttons">
                <button class="like-btn" data-moto-id="${moto.moto_id || moto.id}">
                    <i class="fas fa-heart"></i> Me gusta
                    <span class="like-count">${moto.likes || 0}</span>
                </button>
                <button class="ideal-btn" data-moto-id="${moto.moto_id || moto.id}">
                    <i class="fas fa-star"></i> Mi moto ideal
                </button>
            </div>
        `;
        
        gridContainer.appendChild(motoCard);
        
        // Animar entrada con retardo
        setTimeout(() => {
            motoCard.style.opacity = "1";
            motoCard.style.transform = "translateY(0)";
        }, index * 100);
    });
    
    // Configurar listener para botones de like
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const motoId = this.getAttribute('data-moto-id');
            const likeCountElement = this.querySelector('.like-count');
            
            // Hacer la petición AJAX para dar like
            fetch('/like_moto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ moto_id: motoId })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Actualizar el contador de likes
                    likeCountElement.textContent = data.likes;
                    
                    // Añadir clase para indicar que el usuario ha dado like
                    this.classList.add('liked');
                    
                    // Mostrar mensaje de éxito
                    showNotification('¡Like registrado!', 'success');
                } else {
                    showNotification(data.message || 'No se pudo registrar el like', 'error');
                }
            })
            .catch(error => {
                console.error('Error al dar like:', error);
                showNotification('Error al procesar la petición', 'error');
            });
        });
    });
      // Configurar listener para botones de moto ideal
    document.querySelectorAll('.ideal-btn').forEach(btn => {        btn.addEventListener('click', function() {
            const motoId = this.getAttribute('data-moto-id');
            console.log("Botón moto ideal clickeado, ID:", motoId);
            
            // Verificar si el ID es válido
            if (!motoId || motoId === 'undefined') {
                alert("Error: No se pudo identificar la moto. Por favor, intenta de nuevo.");
                console.error("ID de moto inválido:", motoId);
                return;
            }

            // Hacer la petición AJAX para marcar como moto ideal
            fetch('/set_ideal_moto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ moto_id: motoId })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Mostrar mensaje de éxito
                    showNotification('¡Moto ideal guardada! Redirigiendo...', 'success');
                    
                    // Redireccionar a la página de moto ideal después de un breve retardo
                    setTimeout(() => {
                        window.location.href = '/moto_ideal';
                    }, 1500);
                } else {
                    showNotification(data.message || 'No se pudo guardar tu moto ideal', 'error');
                }
            })
            .catch(error => {
                console.error('Error al guardar moto ideal:', error);
                showNotification('Error al procesar la petición', 'error');
            });
        });
    });
    
    // Función para mostrar notificaciones
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Mostrar la notificación
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Ocultar y eliminar la notificación después de un tiempo
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
});
