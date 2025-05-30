/**
 * Script para manejar la página de motos populares (PageRank)
 * Versión restaurada - esencial para el funcionamiento
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔥 Inicializando página de motos populares...');
    
    // Configurar botones de like
    setupLikeButtons();
    
    // Configurar botón de actualizar ranking
    setupUpdateRankingButton();
    
    // Configurar efectos visuales
    setupVisualEffects();
});

function setupLikeButtons() {
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const modelo = this.getAttribute('data-modelo');
            const likeCountSpan = this.querySelector('.like-count');
            
            if (!modelo) {
                console.error('No se encontró el modelo de la moto');
                return;
            }
            
            // Incrementar contador localmente
            let currentLikes = parseInt(likeCountSpan.textContent) || 0;
            likeCountSpan.textContent = currentLikes + 1;
            
            // Enviar al servidor
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
                    if (data.likes && data.likes !== parseInt(likeCountSpan.textContent)) {
                        likeCountSpan.textContent = data.likes;
                    }
                    showNotification(`¡Te gusta la ${modelo}! Ranking actualizado.`);
                } else {
                    console.error("Error al registrar like:", data.message);
                    showNotification("No se pudo registrar tu like. Inténtalo de nuevo.", "error");
                }
            })
            .catch(error => {
                console.error("Error al registrar like:", error);
                showNotification("Error de conexión, pero tu like se guardó localmente.", "warning");
            });
        });
    });
}

function setupUpdateRankingButton() {
    const reloadBtn = document.getElementById('reload-btn');
    if (reloadBtn) {
        reloadBtn.addEventListener('click', function() {
            this.classList.add('pulse');
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando ranking...';
            
            // Efecto visual en las tarjetas
            const cards = document.querySelectorAll('.moto-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = "0";
                    card.style.transform = "translateY(-20px) scale(0.95)";
                }, index * 100);
            });
            
            // Recargar página
            setTimeout(() => {
                window.location.href = '/populares?update_ranking=true';
            }, 800);
        });
    }
}

function setupVisualEffects() {
    // Animación de entrada para las tarjetas
    const cards = document.querySelectorAll('.moto-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Estilos básicos
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        transition: all 0.3s ease;
    `;
    
    // Colores según tipo
    if (type === 'success') notification.style.background = '#2ecc71';
    else if (type === 'error') notification.style.background = '#e74c3c';
    else if (type === 'warning') notification.style.background = '#f39c12';
    
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}