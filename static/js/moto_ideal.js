document.addEventListener('DOMContentLoaded', function() {
    // Verificar si hay datos de moto ideal
    const motoContainer = document.getElementById('moto-ideal-container');
    const noMotoContainer = document.getElementById('no-moto-container');
    
    // Si hay elemento de moto ideal con datos, mostrarlos
    if (motoContainer && motoContainer.dataset.hasMoto === 'true') {
        if (noMotoContainer) {
            noMotoContainer.style.display = 'none';
        }
        motoContainer.style.display = 'block';
    }
    // Si no hay moto ideal, mostrar mensaje alternativo
    else {
        if (motoContainer) {
            motoContainer.style.display = 'none';
        }
        if (noMotoContainer) {
            noMotoContainer.style.display = 'block';
        }
    }
    
    // Manejar botón "Cambiar mi moto ideal"
    const changeButton = document.getElementById('change-moto-button');
    if (changeButton) {
        changeButton.addEventListener('click', function() {
            window.location.href = '/test?dest=moto_ideal';
        });
    }
    
    // Manejar botón "Encontrar mi moto ideal"
    const findButton = document.getElementById('find-moto-button');
    if (findButton) {
        findButton.addEventListener('click', function() {
            window.location.href = '/test?dest=moto_ideal';
        });
    }
});
