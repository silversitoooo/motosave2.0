document.addEventListener("DOMContentLoaded", () => {
    // Preview de la imagen
    const imagenInput = document.getElementById('imagen');
    const previewContainer = document.querySelector('.moto-image');
    
    // Solo si existe el input y el contenedor de vista previa
    if (imagenInput && previewContainer) {
        imagenInput.addEventListener('change', () => {
            const url = imagenInput.value.trim();
            
            // Si ya existe una imagen de moto ideal mostrada
            if (previewContainer.querySelector('img')) {
                // Actualiza la URL de la imagen existente
                if (url && isValidUrl(url)) {
                    const img = previewContainer.querySelector('img');
                    img.src = url;
                    img.classList.remove('imagen-error');
                    
                    // Muestra mensaje de éxito temporal
                    showNotification('Imagen actualizada correctamente', 'success');
                } else if (url) {
                    showNotification('URL de imagen inválida', 'error');
                    const img = previewContainer.querySelector('img');
                    img.classList.add('imagen-error');
                }
            } 
            // Si estamos creando por primera vez
            else if (url && isValidUrl(url) && !document.querySelector('.moto-display')) {
                // Crea una vista previa temporal
                showImagePreview(url);
            }
        });
    }
    
    // Validaciones del formulario
    const form = document.querySelector('.moto-form form');
    if (form) {
        form.addEventListener('submit', (e) => {
            const url = imagenInput.value.trim();
            if (url && !isValidUrl(url)) {
                e.preventDefault();
                showNotification('Por favor, ingresa una URL de imagen válida', 'error');
                imagenInput.focus();
            }
        });
    }
    
    // Función para validar URL
    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    // Función para mostrar una vista previa de la imagen
    function showImagePreview(url) {
        // Si no existe un contenedor de vista previa, creamos uno temporal
        const tempPreview = document.createElement('div');
        tempPreview.classList.add('image-preview-temp');
        tempPreview.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.9);
            padding: 20px;
            border-radius: 10px;
            z-index: 1000;
            box-shadow: 0 0 20px rgba(249, 115, 22, 0.5);
            max-width: 80%;
            text-align: center;
        `;
        
        // Imagen
        const img = document.createElement('img');
        img.src = url;
        img.style.cssText = `
            max-width: 100%;
            max-height: 70vh;
            border-radius: 5px;
            margin-bottom: 15px;
        `;
        
        // Mensaje
        const message = document.createElement('p');
        message.textContent = 'Vista previa de la imagen';
        message.style.cssText = `
            color: white;
            margin-bottom: 15px;
        `;
        
        // Botón para cerrar
        const closeBtn = document.createElement('button');
        closeBtn.textContent = 'Cerrar';
        closeBtn.style.cssText = `
            background: #f97316;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
        `;
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(tempPreview);
        });
        
        // Añadir elementos al contenedor
        tempPreview.appendChild(message);
        tempPreview.appendChild(img);
        tempPreview.appendChild(closeBtn);
        
        // Añadir al cuerpo del documento
        document.body.appendChild(tempPreview);
        
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            if (document.body.contains(tempPreview)) {
                document.body.removeChild(tempPreview);
            }
        }, 5000);
    }
    
    // Función para mostrar notificaciones
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.classList.add('notification', `notification-${type}`);
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s ease, fadeOut 0.5s ease 2.5s forwards;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        
        if (type === 'success') {
            notification.style.background = 'rgba(16, 185, 129, 0.9)';
        } else if (type === 'error') {
            notification.style.background = 'rgba(239, 68, 68, 0.9)';
        } else {
            notification.style.background = 'rgba(59, 130, 246, 0.9)';
        }
        
        // Añadir keyframes para las animaciones
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Eliminar después de 3 segundos
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 3000);
    }
    
    // Añadir efectos visuales
    addVisualEffects();
    
    function addVisualEffects() {
        // Efecto de brillo para la imagen
        const motoImage = document.querySelector('.moto-image img');
        if (motoImage) {
            motoImage.addEventListener('mousemove', (e) => {
                const { left, top, width, height } = motoImage.getBoundingClientRect();
                const x = (e.clientX - left) / width;
                const y = (e.clientY - top) / height;
                
                motoImage.style.filter = `brightness(1.2) drop-shadow(${(x - 0.5) * 10}px ${(y - 0.5) * 10}px 15px rgba(249, 115, 22, 0.3))`;
                motoImage.style.transform = `perspective(800px) rotateY(${(x - 0.5) * 10}deg) rotateX(${(y - 0.5) * -10}deg) scale(1.02)`;
            });
            
            motoImage.addEventListener('mouseleave', () => {
                motoImage.style.filter = '';
                motoImage.style.transform = '';
                motoImage.style.transition = 'all 0.5s ease';
            });
        }
        
        // Efecto de enfoque para inputs
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.style.transform = 'scale(1.02)';
                input.parentElement.style.transition = 'transform 0.3s ease';
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.style.transform = 'scale(1)';
            });
        });
    }
});
