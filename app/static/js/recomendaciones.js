document.addEventListener("DOMContentLoaded", () => {
    const botones = document.querySelectorAll(".favorita-btn");

    botones.forEach(boton => {
        boton.addEventListener("click", () => {
            // Remover selección previa
            botones.forEach(b => b.classList.remove("seleccionada"));

            // Marcar actual
            boton.classList.add("seleccionada");

            const modelo = boton.dataset.modelo;
            console.log(`Moto favorita seleccionada: ${modelo}`);

            // Aquí podrías enviar al servidor (con fetch):
            // fetch('/seleccionar_favorita', { method: 'POST', body: JSON.stringify({ modelo }) })
        });
    });
});