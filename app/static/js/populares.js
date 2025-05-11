document.addEventListener("DOMContentLoaded", () => {
    // Aplicar efectos NeonGlass a las tarjetas
    const motoCards = document.querySelectorAll(".moto-card");
    
    // Animar entrada de tarjetas
    motoCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = "0";
            card.style.transform = "translateY(20px)";
            card.style.transition = "all 0.5s cubic-bezier(0.5, 1, 0.89, 1)";
            
            setTimeout(() => {
                card.style.opacity = "1";
                card.style.transform = "translateY(0)";
            }, 100);
        }, index * 150);
    });

    // Añadir efectos de brillo en hover
    motoCards.forEach(card => {
        // Crear elemento de brillo si no existe
        let shine = card.querySelector(".shine");
        if (!shine) {
            shine = document.createElement("div");
            shine.className = "shine";
            card.prepend(shine);
        }
        
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; // Posición X dentro de la tarjeta
            const y = e.clientY - rect.top;  // Posición Y dentro de la tarjeta
            
            // Calcular ángulos para el efecto de brillo
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const angleX = (y - centerY) / 10;
            const angleY = (centerX - x) / 10;
            
            // Aplicar transformación sutil
            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) translateZ(10px)`;
            
            // Efecto de brillo en la posición del ratón
            shine.style.opacity = "0.7";
            shine.style.left = `${x}px`;
            shine.style.top = `${y}px`;
        });
        
        // Restablecer al salir
        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(1000px) rotateX(0) rotateY(0) translateZ(0)";
            card.style.transition = "all 0.5s cubic-bezier(0.5, 1, 0.89, 1)";
            shine.style.opacity = "0";
        });
    });

    // Funcionalidad de los botones de like
    const botones = document.querySelectorAll(".like-btn");
    
    // Verificar si existe el objeto likedMotos en localStorage
    if (!localStorage.getItem('likedMotos')) {
        localStorage.setItem('likedMotos', JSON.stringify({}));
    }
    
    // Cargar estado de likes guardados
    const likedMotos = JSON.parse(localStorage.getItem('likedMotos'));
    
    // Aplicar estado guardado
    botones.forEach(btn => {
        const modelo = btn.dataset.modelo;
        if (likedMotos[modelo]) {
            btn.innerHTML = '<i class="fas fa-heart"></i> ¡Te gusta!';
            btn.classList.add("liked");
            btn.disabled = true;
            btn.style.boxShadow = "0 0 15px hsl(24, 90%, 50%), 0 0 30px hsl(24, 90%, 40%)";
        }
    });

    // Añadir comportamiento a botones
    botones.forEach(btn => {
        btn.addEventListener("click", () => {
            const modelo = btn.dataset.modelo;
            const likeCountSpan = btn.parentElement.querySelector(".like-count");
            const card = btn.closest(".moto-card");

            // Efecto en la tarjeta
            card.classList.add("liked");
            
            // Añadir efecto visual al hacer clic
            btn.classList.add("liked");
            
            // Efecto de pulso
            btn.style.transform = "scale(1.2)";
            setTimeout(() => {
                btn.style.transform = "scale(1)";
            }, 200);

            // Cambiar apariencia del botón
            btn.innerHTML = '<i class="fas fa-heart"></i> ¡Te gusta!';
            btn.disabled = true;
            
            // Efecto de brillo naranja            btn.style.boxShadow = "0 0 15px hsl(24, 90%, 50%), 0 0 30px hsl(24, 90%, 40%)";
            
            // Incrementar contador localmente
            const count = parseInt(likeCountSpan.textContent);
            likeCountSpan.textContent = count + 1;
            
            // Añadir efecto flotante con emojis
            addFloatingEmojis(card);
                        
            // Guardar el like en localStorage
            const likedMotos = JSON.parse(localStorage.getItem('likedMotos'));
            likedMotos[modelo] = true;
            localStorage.setItem('likedMotos', JSON.stringify(likedMotos));
            
            // Enviar like al servidor usando fetch
            fetch('/like_moto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ modelo: modelo })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`Like registrado para ${modelo}:`, data);
                    // Actualizar el contador con el valor real del servidor si es diferente
                    if (data.likes && data.likes !== parseInt(likeCountSpan.textContent)) {
                        likeCountSpan.textContent = data.likes;
                    }
                    // Muestra un mensaje de éxito 
                    showNotification(`¡Te gusta la ${modelo}!`);
                } else {
                    console.error("Error al registrar like:", data.message);
                    showNotification("No se pudo registrar tu like. Inténtalo de nuevo.", "error");
                }
            })
            .catch(error => {
                console.error("Error al registrar like:", error);
                // En caso de error de conexión, mantenemos el comportamiento local
                showNotification("No se pudo conectar con el servidor, pero tu like ha sido guardado localmente.", "warning");
            });
            
            // Animación para el contador
            const likeInfo = btn.parentElement.querySelector(".like-info");
            likeInfo.style.transform = "scale(1.1)";
            likeInfo.style.color = "hsl(24, 90%, 80%)";
            setTimeout(() => {
                likeInfo.style.transform = "scale(1)";
                likeInfo.style.transition = "all 0.5s cubic-bezier(0.5, 1, 0.89, 1)";
            }, 300);
        });
    });    // Funcionalidad para botón de recargar motos
    const reloadBtn = document.getElementById('reload-btn');
    if (reloadBtn) {
        reloadBtn.addEventListener('click', () => {
            // Añadir clase de animación
            reloadBtn.classList.add('pulse');
            reloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
            
            // Obtener el contenedor de la cuadrícula
            const gridContainer = document.querySelector('.grid-container');
            
            // Efecto de desvanecimiento en las tarjetas actuales
            const cards = document.querySelectorAll('.moto-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = "0";
                    card.style.transform = "translateY(-20px) scale(0.95)";
                }, index * 100);
            });
            
            // Simular carga y refrescar las tarjetas
            setTimeout(() => {                // Recargar la página con parámetro de aleatorización
                window.location.href = '/populares?shuffle=true';
                
                // En una implementación más avanzada:
                // - Podríamos usar fetch() para obtener nuevas motos del servidor
                // - Actualizar dinámicamente los elementos del DOM
                // - Mantener el estado de likes del usuario sin recargar la página
            }, 800);
        });
    }

    // Simulación de petición al servidor
    function simulateServerRequest(modelo) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: `Like para ${modelo} registrado con éxito`
                });
            }, 500);
        });
    }
      // Función para mostrar notificaciones
    function showNotification(message, type = 'success') {
        // Comprobar si ya existe una notificación y eliminarla
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Establecer colores según el tipo
        let bgColor, textColor;
        switch(type) {
            case 'error':
                bgColor = 'linear-gradient(90deg, hsl(0, 90%, 30%), hsl(0, 90%, 40%))';
                textColor = 'white';
                break;
            case 'warning':
                bgColor = 'linear-gradient(90deg, hsl(40, 90%, 30%), hsl(40, 90%, 40%))';
                textColor = 'white';
                break;
            case 'success':
            default:
                bgColor = 'linear-gradient(90deg, hsl(24, 90%, 30%), hsl(30, 90%, 40%))';
                textColor = 'white';
                break;
        }
        
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        
        // Añadir estilos inline para la notificación
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        notification.style.padding = '12px 20px';
        notification.style.background = bgColor;
        notification.style.color = textColor;
        notification.style.borderRadius = '8px';
        notification.style.boxShadow = '0 0 15px rgba(0, 0, 0, 0.5)';
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        notification.style.transition = 'all 0.3s ease-out';
        notification.style.zIndex = '1000';
        notification.style.fontWeight = 'bold';
        
        // Añadir al DOM
        document.body.appendChild(notification);
        
        // Activar la animación de entrada
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);
        
        // Eliminar después de 3 segundos
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(20px)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Efecto de color aleatorio (dentro del rango naranja) para los brillos
    function updateHues() {
        const hue1Base = 20; // Base naranja
        const hue2Base = 30; // Base naranja-amarillo
        
        // Pequeñas variaciones dentro del rango naranja
        const hue1 = hue1Base + (Math.random() * 10 - 5);
        const hue2 = hue2Base + (Math.random() * 10 - 5);
        
        document.documentElement.style.setProperty('--hue1', hue1);
        document.documentElement.style.setProperty('--hue2', hue2);
        
        setTimeout(updateHues, 5000); // Actualizar cada 5 segundos
    }
    
    // Iniciar efecto de variación de tonos
    updateHues();
    
    // Función para añadir emojis flotantes cuando se da like
    function addFloatingEmojis(element) {
        const emojis = ['❤️', '🔥', '👍', '😍', '🏍️'];
        const count = 7; // Cantidad de emojis a crear
        
        for (let i = 0; i < count; i++) {
            const emoji = document.createElement('div');
            emoji.className = 'floating-emoji';
            emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            
            // Posición inicial aleatoria dentro del elemento
            const rect = element.getBoundingClientRect();
            const startX = Math.random() * rect.width * 0.8 + rect.width * 0.1;
            
            // Estilos base
            emoji.style.position = 'absolute';
            emoji.style.left = `${startX}px`;
            emoji.style.bottom = '20%';
            emoji.style.fontSize = `${Math.random() * 10 + 15}px`;
            emoji.style.opacity = '1';
            emoji.style.pointerEvents = 'none';
            emoji.style.zIndex = '1000';
            emoji.style.transition = 'all 1s ease-out';
            
            // Añadir al elemento
            element.appendChild(emoji);
            
            // Iniciar animación
            setTimeout(() => {
                emoji.style.transform = `translateY(-${50 + Math.random() * 100}px) translateX(${Math.random() * 40 - 20}px) rotate(${Math.random() * 90 - 45}deg)`;
                emoji.style.opacity = '0';
                
                // Eliminar después de completar la animación
                setTimeout(() => {
                    emoji.remove();
                }, 1000);
            }, i * 100);
        }
    }

    // Añadir efecto de enfoque para resaltar la tarjeta activa
    function setupCardFocus() {
        const cards = document.querySelectorAll('.moto-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                // Reducir la opacidad de las otras tarjetas
                cards.forEach(otherCard => {
                    if (otherCard !== card) {
                        otherCard.style.opacity = '0.7';
                        otherCard.style.transform = 'scale(0.98)';
                    }
                });
                
                // Resaltar la tarjeta actual
                card.style.transform = 'scale(1.02) translateY(-5px)';
                card.style.boxShadow = '0 15px 25px rgba(0, 0, 0, 0.3), 0 0 15px hsl(var(--hue1), 90%, 40%, 0.8)';
                
                // Aumentar el brillo del badge
                const badge = card.querySelector('.popular-badge');
                if (badge) {
                    badge.style.animation = 'pulse 0.8s infinite';
                    badge.style.boxShadow = '0 0 15px rgba(255, 0, 0, 0.5)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                // Restaurar todas las tarjetas
                cards.forEach(otherCard => {
                    otherCard.style.opacity = '1';
                    otherCard.style.transform = 'scale(1)';
                    otherCard.style.boxShadow = '';
                    
                    // Restaurar el badge
                    const badge = otherCard.querySelector('.popular-badge');
                    if (badge) {
                        badge.style.animation = 'pulse 2s infinite';
                        badge.style.boxShadow = '0 0 10px rgba(255, 0, 0, 0.3)';
                    }
                });
            });
        });
    }
    
    // Inicializar el efecto de enfoque
    setupCardFocus();
});