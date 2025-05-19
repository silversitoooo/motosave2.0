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
    
    // MODIFICACIÓN: Renderizar directamente en el formato de cuadrícula sin mostrar imágenes grandes primero
    // Crear tarjetas de motos directamente en el contenedor de cuadrícula
    motosRecomendadas.forEach((moto, index) => {
        // Crear tarjeta para cada moto recomendada con tamaño controlado
        const motoCard = document.createElement('div');
        motoCard.className = 'moto-card';
        motoCard.setAttribute('data-moto-id', moto.moto_id);
        
        // Formatear el precio correctamente
        const precio = moto.precio ? `€${moto.precio.toLocaleString()}` : 'N/D';
        
        // Asegurar que los valores de año y cilindrada se muestren correctamente
        const año = moto.año || moto.anio || 'N/D';
        const cilindrada = moto.cilindrada ? `${moto.cilindrada} cc` : 'N/D';
        
        // Formatear la potencia (CV) correctamente con unidad
        const potencia = moto.potencia ? `${moto.potencia} CV` : 'N/D';
        
        // Añadir el score de la recomendación (porcentaje de coincidencia)
        const score = moto.score ? `${Math.round(moto.score * 100)}%` : 'N/D';
        
        // HTML interno de la tarjeta con imagen de tamaño controlado y nuevos campos
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
                <button class="like-btn" data-moto-id="${moto.moto_id}">
                    <i class="fas fa-heart"></i> Me gusta
                    <span class="like-count">${moto.likes || 0}</span>
                </button>
                <button class="ideal-btn" data-moto-id="${moto.moto_id}">
                    <i class="fas fa-star"></i> Mi moto ideal
                </button>
            </div>
        `;
        
        // Añadir la tarjeta al contenedor
        gridContainer.appendChild(motoCard);
        
        // Animar entrada con un pequeño retraso incremental para efecto visual
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
                body: JSON.stringify({ moto_id: motoId }),
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
    document.querySelectorAll('.ideal-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const motoId = this.getAttribute('data-moto-id');
            
            // Hacer la petición AJAX para marcar como moto ideal
            fetch('/set_ideal_moto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ moto_id: motoId }),
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
    
    // Añadir un botón para volver arriba
    const backToTopBtn = document.createElement('button');
    backToTopBtn.className = 'back-to-top-btn';
    backToTopBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    document.body.appendChild(backToTopBtn);
    
    // Mostrar/ocultar botón según el scroll
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });
    
    // Acción del botón para volver arriba
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});