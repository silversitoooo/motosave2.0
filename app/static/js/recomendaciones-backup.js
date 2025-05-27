<!-- Este script maneja correctamente las recomendaciones -->
window.addEventListener('DOMContentLoaded', function() {
    console.log('Script de reparación de recomendaciones cargado...');

    // Función para mostrar una alerta en la página
    function mostrarAlerta(mensaje, tipo = 'info') {
        const alertaDiv = document.createElement('div');
        alertaDiv.style.padding = '15px';
        alertaDiv.style.margin = '10px 0';
        alertaDiv.style.borderRadius = '5px';
        alertaDiv.style.color = 'white';
        alertaDiv.style.textAlign = 'center';
        
        if (tipo === 'error') {
            alertaDiv.style.backgroundColor = '#ff6b6b';
        } else if (tipo === 'success') {
            alertaDiv.style.backgroundColor = '#51cf66';
        } else {
            alertaDiv.style.backgroundColor = '#339af0';
        }
        
        alertaDiv.textContent = mensaje;
        
        // Insertar después del título
        const titulo = document.querySelector('h1.tituloFriends');
        if (titulo && titulo.parentNode) {
            titulo.parentNode.insertBefore(alertaDiv, titulo.nextSibling);
        } else {
            document.body.prepend(alertaDiv);
        }
    }

    // Obtener recomendaciones de motos
    let motosRecomendadas = [];
    
    // Intentar obtener desde window.motosRecomendadas
    if (window.motosRecomendadas && Array.isArray(window.motosRecomendadas)) {
        console.log('Recomendaciones encontradas en la variable global:', window.motosRecomendadas.length);
        motosRecomendadas = window.motosRecomendadas;
    } else {
        // Intentar obtener desde el elemento script
        const dataElement = document.getElementById('recommendations-data');
        if (dataElement) {
            try {
                const data = JSON.parse(dataElement.textContent);
                if (Array.isArray(data)) {
                    console.log('Recomendaciones recuperadas desde elemento JSON:', data.length);
                    motosRecomendadas = data;
                }
            } catch (e) {
                console.error('Error al parsear JSON de recomendaciones:', e);
                mostrarAlerta('Hubo un problema al cargar las recomendaciones', 'error');
            }
        }
    }
    
    // Verificar si tenemos recomendaciones
    if (motosRecomendadas.length === 0) {
        console.warn('No se encontraron recomendaciones');
        mostrarAlerta('No se encontraron recomendaciones para mostrar', 'error');
        return;
    }
    
    console.log('Recomendaciones disponibles:', motosRecomendadas.length);
    mostrarAlerta(`Se encontraron ${motosRecomendadas.length} recomendaciones`, 'success');
    
    // Obtener el contenedor donde mostrar las motos
    const gridContainer = document.querySelector('.grid-container');
    if (!gridContainer) {
        console.error('No se encontró el contenedor .grid-container');
        return;
    }
    
    // Limpiar el contenedor
    gridContainer.innerHTML = '';
    
    // Mostrar cada moto
    motosRecomendadas.forEach((moto, index) => {
        // Crear elemento de tarjeta
        const motoCard = document.createElement('div');
        motoCard.className = 'moto-card';
        
        // Formatear valores para mostrar
        const precio = moto.precio ? `€${moto.precio.toLocaleString()}` : 'N/D';
        const año = moto.año || moto.anio || 'N/D';
        const cilindrada = moto.cilindrada ? `${moto.cilindrada} cc` : 'N/D';
        const potencia = moto.potencia ? `${moto.potencia} CV` : 'N/D';
        const score = moto.score ? `${Math.round(moto.score * 100)}%` : 'N/D';
        
        // Contenido HTML de la tarjeta
        motoCard.innerHTML = `
            <img src="${moto.imagen || '/static/images/default-moto.jpg'}" alt="${moto.marca} ${moto.modelo}" class="moto-img">
            <h3>${moto.marca} ${moto.modelo}</h3>
            <p><strong>Tipo:</strong> ${moto.tipo || moto.estilo || 'N/D'}</p>
            <p><strong>Cilindrada:</strong> ${cilindrada}</p>
            <p><strong>Potencia:</strong> ${potencia}</p>
            <p><strong>Precio:</strong> ${precio}</p>
            <div class="match-score">
                <div class="score-label">Coincidencia: ${score}</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${moto.score * 100}%"></div>
                </div>
            </div>
            <div class="reasons-container">
                <h4>Por qué te recomendamos esta moto:</h4>
                <ul class="reasons-list">
                    ${moto.reasons && moto.reasons.length > 0 ? 
                        moto.reasons.map(reason => `<li><i class="fas fa-check"></i> ${reason}</li>`).join('') : 
                        '<li><i class="fas fa-check"></i> Recomendación personalizada</li>'}
                </ul>
            </div>
        `;
        
        // Añadir al contenedor
        gridContainer.appendChild(motoCard);
    });
});
