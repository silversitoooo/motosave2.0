/**
 * EMERGENCY SCRIPT FOR MOTORCYCLE RECOMMENDATIONS DISPLAY
 * This is a simplified script with aggressive error handling to ensure recommendations always display
 */

document.addEventListener("DOMContentLoaded", function() {
    console.log("🚨 EMERGENCY RECOMMENDATIONS SCRIPT LOADING");
    
    // Function to log objects safely
    function logData(label, data) {
        console.log(`${label}:`, data);
        try {
            console.log(`${label} (JSON):`, JSON.stringify(data).substring(0, 200) + "...");
        } catch(e) {
            console.log(`Cannot stringify ${label}`);
        }
    }
    
    // Get recommendations data with multiple fallbacks
    function getRecommendationsData() {
        // Check for global variable
        if (window.motosRecomendadas && Array.isArray(window.motosRecomendadas) && window.motosRecomendadas.length > 0) {
            logData("Using window.motosRecomendadas", window.motosRecomendadas);
            return window.motosRecomendadas;
        }
        
        // Check for JSON element
        try {
            const jsonElement = document.getElementById('recommendations-data');
            if (jsonElement && jsonElement.textContent) {
                const data = JSON.parse(jsonElement.textContent);
                if (Array.isArray(data) && data.length > 0) {
                    logData("Using recommendations-data element", data);
                    return data;
                }
            }
        } catch (e) {
            console.error("Error parsing recommendations from element:", e);
        }
        
        // Scrape the page for any JSON data
        try {
            const scripts = document.querySelectorAll('script:not([src])');
            for (const script of scripts) {
                const content = script.textContent;
                if (content && content.includes('motosRecomendadas') && content.includes('[{')) {
                    const match = content.match(/motosRecomendadas\s*=\s*(\[.*?\]);/s);
                    if (match && match[1]) {
                        try {
                            const data = JSON.parse(match[1]);
                            if (Array.isArray(data) && data.length > 0) {
                                logData("Extracted from script tag", data);
                                return data;
                            }
                        } catch (parseErr) {
                            console.error("Failed to parse extracted data:", parseErr);
                        }
                    }
                }
            }
        } catch (e) {
            console.error("Error scraping for recommendations:", e);
        }
        
        // No data found
        console.error("NO RECOMMENDATIONS DATA FOUND");
        return [];
    }
    
    // Create emergency UI function
    function createEmergencyUI(container, motorcycles) {
        console.log(`Creating emergency UI for ${motorcycles.length} motorcycles`);
        
        if (!motorcycles || motorcycles.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; background-color: rgba(0,0,0,0.7); border-radius: 10px; border: 1px solid #f97316;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #f97316; margin-bottom: 20px;"></i>
                    <h3 style="color: #f97316; margin-bottom: 15px;">No hay recomendaciones disponibles</h3>
                    <p style="color: white; margin-bottom: 25px;">Por favor completa el test de preferencias para obtener recomendaciones personalizadas.</p>
                    <a href="/test" style="display: inline-block; background-color: #f97316; color: white; padding: 10px 25px; border-radius: 5px; text-decoration: none;">
                        Hacer el test
                    </a>
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        // Create cards for each motorcycle
        motorcycles.forEach((moto, index) => {
            console.log(`Processing motorcycle ${index + 1}:`, moto.marca, moto.modelo);
            
            // Handle missing data with fallbacks
            const marca = moto.marca || 'Marca desconocida';
            const modelo = moto.modelo || 'Modelo desconocido';
            const imagen = moto.imagen || '/static/images/default-moto.jpg';
            const tipo = moto.tipo || moto.estilo || 'N/D';
            const precio = moto.precio ? `€${moto.precio.toLocaleString()}` : 'Precio no disponible';
            const cilindrada = moto.cilindrada ? `${moto.cilindrada} cc` : 'N/D';
            const potencia = moto.potencia ? `${moto.potencia} CV` : 'N/D';
            const anio = moto.anio || moto.año || 'N/D';
            
            // Calculate score
            let scoreValue = 'N/D';
            let scoreWidth = '0%';
            if (typeof moto.score === 'number') {
                scoreValue = `${Math.round(moto.score * 100)}%`;
                scoreWidth = `${Math.round(moto.score * 100)}%`;
            }
            
            // Get reasons
            let reasons = [];
            if (Array.isArray(moto.reasons) && moto.reasons.length > 0) {
                reasons = moto.reasons;
            } else if (Array.isArray(moto.razones) && moto.razones.length > 0) {
                reasons = moto.razones;
            }
            
            if (reasons.length === 0) {
                reasons = ["Recomendación personalizada basada en tus preferencias"];
            }
            
            // Create card element
            const card = document.createElement('div');
            card.className = 'moto-card';
            card.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
            card.style.borderRadius = '10px';
            card.style.padding = '20px';
            card.style.margin = '15px';
            card.style.border = '1px solid #f97316';
            card.style.color = 'white';
            
            // Card content
            card.innerHTML = `
                <img src="${imagen}" alt="${marca} ${modelo}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 5px; margin-bottom: 15px;">
                <h3 style="color: #f97316; margin-bottom: 10px; font-size: 1.3rem;">${marca} ${modelo}</h3>
                <div style="margin-bottom: 10px;">
                    <span>${anio}</span> • 
                    <span>${potencia}</span>
                </div>
                <div style="margin-bottom: 15px;">
                    <p><strong>Coincidencia:</strong> ${scoreValue}</p>
                    <div style="height: 8px; background-color: rgba(255, 255, 255, 0.2); border-radius: 4px; overflow: hidden;">
                        <div style="height: 100%; width: ${scoreWidth}; background-color: #f97316; border-radius: 4px;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <p><strong>Tipo:</strong> ${tipo}</p>
                    <p><strong>Cilindrada:</strong> ${cilindrada}</p>
                    <p><strong>Precio:</strong> ${precio}</p>
                </div>
                <div>
                    <h4 style="color: #f97316; margin-bottom: 8px; font-size: 1rem;">Por qué te recomendamos esta moto:</h4>
                    <ul style="list-style-type: none; padding: 0; margin: 0;">
                        ${reasons.map(reason => `
                            <li style="margin-bottom: 5px;">
                                <i class="fas fa-check" style="color: #f97316; margin-right: 5px;"></i> 
                                ${reason}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
            
            // Add to container
            container.appendChild(card);
        });
    }
    
    // Main execution
    try {
        console.log("Starting emergency recommendations display");
        
        // Get the container
        const container = document.querySelector('.grid-container');
        if (!container) {
            console.error("Container not found!");
            return;
        }
        
        // Get recommendations
        const motorcycles = getRecommendationsData();
        
        // Create UI
        createEmergencyUI(container, motorcycles);
        
        console.log("Emergency display complete");
        
    } catch (e) {
        console.error("CRITICAL ERROR in emergency script:", e);
    }
});
