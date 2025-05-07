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
            const shines = card.querySelectorAll(".shine");
            shines.forEach(shine => {
                shine.style.opacity = "0.7";
                shine.style.left = `${x}px`;
                shine.style.top = `${y}px`;
            });
        });
        
        // Restablecer al salir
        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(1000px) rotateX(0) rotateY(0) translateZ(0)";
            card.style.transition = "all 0.5s cubic-bezier(0.5, 1, 0.89, 1)";
            
            const shines = card.querySelectorAll(".shine");
            shines.forEach(shine => {
                shine.style.opacity = "0";
            });
        });
    });

    // Funcionalidad de los botones de like
    const botones = document.querySelectorAll(".like-btn");

    botones.forEach(btn => {
        btn.addEventListener("click", () => {
            const modelo = btn.dataset.modelo;
            const likeCountSpan = btn.parentElement.querySelector(".like-count");

            // Añadir efecto visual al hacer clic
            btn.classList.add("liked");
            
            // Efecto de pulso
            btn.style.transform = "scale(1.2)";
            setTimeout(() => {
                btn.style.transform = "scale(1)";
            }, 200);

            // Lógica para simular like (aquí deberías enviar la acción al servidor vía fetch o POST)
            btn.innerHTML = '<i class="fas fa-heart"></i> ¡Te gusta!';
            btn.disabled = true;
            
            // Efecto de brillo naranja
            btn.style.boxShadow = "0 0 15px hsl(24, 90%, 50%), 0 0 30px hsl(24, 90%, 40%)";
            
            // Incrementar contador localmente
            const count = parseInt(likeCountSpan.textContent);
            likeCountSpan.textContent = count + 1;
            
            // Animación para el contador
            const likeInfo = btn.parentElement.querySelector(".like-info");
            likeInfo.style.transform = "scale(1.1)";
            likeInfo.style.color = "hsl(24, 90%, 80%)";
            setTimeout(() => {
                likeInfo.style.transform = "scale(1)";
                likeInfo.style.transition = "all 0.5s cubic-bezier(0.5, 1, 0.89, 1)";
            }, 300);
        });
    });

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
});