/**
 * Script for displaying motorcycle recommendations
 * Fixed version (May 26, 2025)
 */
document.addEventListener("DOMContentLoaded", () => {
    console.log("🏍️ Initializing recommendations display system");
    
    // Debug function to log data
    function logData(message, data) {
        console.log(`${message}:`, data);
    }
    
    // Get the grid container
    const gridContainer = document.querySelector('.grid-container');
    if (!gridContainer) {
        console.error("❌ Error: Grid container not found");
        return;
    }
    
    // Get recommendations data
    let motorcycles = [];
    
    // Source 1: window.motosRecomendadas
    if (window.motosRecomendadas && Array.isArray(window.motosRecomendadas)) {
        motorcycles = window.motosRecomendadas;
        logData("Found recommendations in window.motosRecomendadas", motorcycles.length);
    }
    // Source 2: JSON element in DOM
    else if (document.getElementById('recommendations-data')) {
        try {
            const jsonText = document.getElementById('recommendations-data').textContent;
            motorcycles = JSON.parse(jsonText);
            logData("Loaded recommendations from DOM element", motorcycles.length);
        } catch (e) {
            console.error("Error parsing JSON:", e);
        }
    }
    
    // Display motorcycles
    displayMotorcycles(motorcycles);
    
    /**
     * Display motorcycle recommendations in the grid
     */
    function displayMotorcycles(motorcycles) {
        // Clear the container
        gridContainer.innerHTML = '';
        
        // Check if we have data
        if (!motorcycles || motorcycles.length === 0) {
            logData("No recommendations to display", {});
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
        
        logData(`Displaying ${motorcycles.length} motorcycles`, motorcycles);
        
        // Create a card for each motorcycle
        motorcycles.forEach((moto, index) => {
            // Create card element
            const motoCard = document.createElement('div');
            motoCard.className = 'moto-card';
            
            // Format values
            const precio = moto.precio ? `€${moto.precio.toLocaleString()}` : 'N/D';
            const año = moto.anio || moto.año || moto.anyo || 'N/D';
            const cilindrada = moto.cilindrada ? `${moto.cilindrada} cc` : 'N/D';
            const potencia = moto.potencia ? `${moto.potencia} CV` : 'N/D';
            const score = typeof moto.score === 'number' ? Math.round(moto.score * 100) : 0;
            
            // Get reasons from either property
            let reasons = [];
            if (Array.isArray(moto.reasons)) {
                reasons = moto.reasons;
            } else if (Array.isArray(moto.razones)) {
                reasons = moto.razones;
            }
            
            // Build card content
            motoCard.innerHTML = `
                <img src="${moto.imagen || '/static/images/default-moto.jpg'}" alt="${moto.marca} ${moto.modelo}" class="moto-img" 
                     onerror="this.src='/static/images/default-moto.jpg'">
                
                <h3>${moto.marca} ${moto.modelo}</h3>
                
                <div class="moto-specs">
                    <span class="specs-year">${año}</span>
                    <span class="specs-divider">•</span>
                    <span class="specs-power">${potencia}</span>
                </div>
                
                <div class="match-score">
                    <span class="score-label">Coincidencia:</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${score}%;"></div>
                    </div>
                    <span class="score-percentage">${score}%</span>
                </div>
                
                <div class="moto-details">
                    <p><strong>Tipo:</strong> ${moto.tipo || moto.estilo || 'N/D'}</p>
                    <p><strong>Cilindrada:</strong> ${cilindrada}</p>
                    <p><strong>Precio:</strong> ${precio}</p>
                </div>
                
                <div class="reasons-container">
                    <h4>Por qué te recomendamos esta moto:</h4>
                    <ul class="reasons-list">
                        ${reasons.length > 0 ? 
                            reasons.map(reason => `<li><i class="fas fa-check"></i> ${reason}</li>`).join('') : 
                            '<li><i class="fas fa-check"></i> Recomendación personalizada</li>'}
                    </ul>
                </div>
            `;
            
            // Add to grid
            gridContainer.appendChild(motoCard);
        });
        
        console.log(`✅ Successfully displayed ${motorcycles.length} recommendations`);
    }
});
