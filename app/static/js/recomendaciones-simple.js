/**
 * Script simplificado para recomendaciones de motos
 * Este script garantiza la visualización correcta de las recomendaciones
 * Versión con mayor debug (26-05-2025)
 */

document.addEventListener("DOMContentLoaded", () => {
    console.log("🔍 Inicializando script de recomendaciones simplificado (versión con mayor debug)...");
    
    // Función para debug
    function logJSON(obj, label) {
        try {
            console.log(`${label}:`, JSON.stringify(obj).substring(0, 500) + "...");
        } catch (e) {
            console.log(`${label}: Error al convertir a JSON`);
        }
    }
    
    // Debug para mostrar todos los datos DOM disponibles
    console.log("🔍 Contenido del elemento #recommendations-data:", 
        document.getElementById('recommendations-data') ? 
        document.getElementById('recommendations-data').textContent : 
        "No encontrado");
        
    console.log("🔍 Valor de window.motosRecomendadas:", window.motosRecomendadas);
    
    // Obtener datos de recomendaciones
    let motosRecomendadas = [];
    
    // Intentar obtener desde window.motosRecomendadas
    if (window.motosRecomendadas && Array.isArray(window.motosRecomendadas)) {
        motosRecomendadas = window.motosRecomendadas;
        console.log(`Encontradas ${motosRecomendadas.length} recomendaciones en window.motosRecomendadas`);
        if (motosRecomendadas.length > 0) {
            logJSON(motosRecomendadas[0], "Primera moto");
        }
    } 
    // Si no hay datos, intentar cargar desde elemento JSON
    else {
        const dataElement = document.getElementById('recommendations-data');
        if (dataElement) {
            try {
                motosRecomendadas = JSON.parse(dataElement.textContent);
                console.log(`Encontradas ${motosRecomendadas.length} recomendaciones en elemento JSON`);
            } catch (e) {
                console.error("Error al analizar JSON:", e);
            }
        }
    }
    
    // Obtener el contenedor
    const gridContainer = document.querySelector('.grid-container');
    if (!gridContainer) {
        console.error("No se encontró el contenedor .grid-container");
        return;
    }
    
    // Limpiar el contenedor
    gridContainer.innerHTML = '';
      // Si no hay recomendaciones
    if (!motosRecomendadas || !Array.isArray(motosRecomendadas) || motosRecomendadas.length === 0) {
        console.error("❌ NO SE ENCONTRARON RECOMENDACIONES VÁLIDAS");
        console.error("motosRecomendadas es:", motosRecomendadas);
        console.error("Tipo:", typeof motosRecomendadas);
        
        // Verificar si hay datos en la página para debug
        const allScripts = document.querySelectorAll('script');
        allScripts.forEach((script, index) => {
            if (script.textContent && script.textContent.includes('motosRecomendadas')) {
                console.log(`Script #${index} contiene datos:`, script.textContent.substring(0, 300) + '...');
            }
        });
        
        gridContainer.innerHTML = `
            <div class="no-recommendations">
                <i class="fas fa-exclamation-circle"></i>
                <h3>No se encontraron recomendaciones</h3>
                <p>Por favor completa el test de preferencias para obtener recomendaciones personalizadas.</p>
                <a href="/test" class="nav-button">Hacer el test</a>
            </div>
        `;
        return;
    }
    
    // Procesar cada recomendación
    motosRecomendadas.forEach((moto, index) => {
        console.log(`Procesando moto ${index+1}:`, moto.marca, moto.modelo);
        
        const motoCard = document.createElement('div');
        motoCard.className = 'moto-card';
        
        // Normalizar valores
        const precio = moto.precio ? `€${moto.precio.toLocaleString()}` : 'N/D';
        const año = moto.anio || moto.año || 'N/D';
        const cilindrada = moto.cilindrada ? `${moto.cilindrada} cc` : 'N/D';
        const potencia = moto.potencia ? `${moto.potencia} CV` : 'N/D';
        const score = moto.score ? `${Math.round(moto.score * 100)}%` : 'N/D';
        
        // Verificar reasons/razones
        let reasons = [];
        if (moto.reasons && Array.isArray(moto.reasons)) {
            reasons = moto.reasons;
        } else if (moto.razones && Array.isArray(moto.razones)) {
            reasons = moto.razones;
        }
        
        // Generar HTML
        motoCard.innerHTML = `
            <img src="${moto.imagen || '/static/images/default-moto.jpg'}" alt="${moto.marca} ${moto.modelo}" class="moto-img">
            <h3>${moto.marca} ${moto.modelo}</h3>
            <div class="moto-specs">
                <span class="specs-year">${año}</span>
                <span class="specs-divider">•</span>
                <span class="specs-power">${potencia}</span>
            </div>
            <div class="match-score">
                <span class="score-label">Coincidencia:</span>
                <span class="score-value">${score}</span>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${moto.score ? moto.score * 100 : 0}%;"></div>
                </div>
            </div>
            <div class="moto-details">
                <p><strong>Tipo:</strong> ${moto.tipo || moto.estilo || 'N/D'}</p>
                <p><strong>Cilindrada:</strong> ${cilindrada}</p>
                <p><strong>Precio:</strong> ${precio}</p>
            </div>
            <div class="reasons-container">
                <h4>Por qué te recomendamos esta moto:</h4>
                <ul class="reasons-list">
                    ${reasons.length > 0 
                        ? reasons.map(reason => `<li><i class="fas fa-check"></i> ${reason}</li>`).join('') 
                        : '<li><i class="fas fa-check"></i> Recomendación personalizada</li>'}
                </ul>
            </div>
        `;
        
        // Añadir al contenedor
        gridContainer.appendChild(motoCard);
    });
    
    console.log(`Renderizadas ${motosRecomendadas.length} recomendaciones correctamente`);
});
