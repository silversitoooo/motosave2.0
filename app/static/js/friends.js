document.addEventListener("DOMContentLoaded", () => {
    const botones = document.querySelectorAll(".friend-name");
    const popup = document.getElementById("popup");
    const closeBtn = document.getElementById("popup-close");
    const popupUsername = document.getElementById("popup-username");
    const popupMotosList = document.getElementById("popup-motos-list");
    
    botones.forEach(btn => {
        btn.addEventListener("click", () => {
            const username = btn.dataset.username;
            popupUsername.textContent = username;
            popupMotosList.innerHTML = "";
            
            const motoFavorita = window.motosLikes[username];
            
            if (!motoFavorita) {
                const emptyMessage = document.createElement("p");
                emptyMessage.textContent = "Este usuario aún no ha dado like a ninguna moto.";
                emptyMessage.style.textAlign = "center";
                emptyMessage.style.fontStyle = "italic";
                popupMotosList.appendChild(emptyMessage);
            } else {
                const li = document.createElement("li");
                const motoName = document.createElement("span");
                motoName.textContent = motoFavorita;
                
                const likeBtn = document.createElement("button");
                likeBtn.innerHTML = '<i class="fas fa-heart"></i> Me gusta';
                likeBtn.onclick = function() {
                    this.innerHTML = '<i class="fas fa-heart"></i> ¡Te gusta!';
                    this.style.backgroundColor = "#f97316";
                    this.style.color = "#fff";
                    this.disabled = true;
                    // Aquí puedes agregar la lógica para enviar el "like" al servidor
                };
                
                li.appendChild(motoName);
                li.appendChild(likeBtn);
                popupMotosList.appendChild(li);
            }
            
            popup.classList.remove("hidden");
        });
    });
    
    // Cerrar el popup
    closeBtn.addEventListener("click", () => {
        popup.classList.add("hidden");
    });
    
    popup.addEventListener("click", (e) => {
        if (e.target === popup) {
            popup.classList.add("hidden");
        }
    });
});