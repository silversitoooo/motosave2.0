/**
 * Script para gestionar las recomendaciones de motos
 * Este script asegura que se muestren las 4 mejores motos según los resultados del test
 */

document.addEventListener("DOMContentLoaded", () => {
    console.log("Inicializando gestor de recomendaciones...");
    
    // Intentar obtener datos de recomendaciones desde múltiples fuentes
    let motosRecomendadas = [];
    
    // Fuente 1: Variable global window.motosRecomendadas
    if (window.motosRecomendadas && Array.isArray(window.motosRecomendadas) && window.motosRecomendadas.length > 0) {
        console.log("Recomendaciones encontradas en window.motosRecomendadas:", window.motosRecomendadas.length);
        motosRecomendadas = window.motosRecomendadas;
    } else {
        console.log("No se encontraron recomendaciones en window.motosRecomendadas");
        
        // Fuente 2: Elemento JSON en la página
        const jsonElement = document.getElementById('recommendations-data');
        if (jsonElement) {
            try {
                const jsonData = JSON.parse(jsonElement.textContent);
                if (Array.isArray(jsonData) && jsonData.length > 0) {
                    motosRecomendadas = jsonData;
                    console.log("Recomendaciones cargadas desde elemento JSON:", motosRecomendadas.length);
                }
            } catch (error) {
                console.error("Error al parsear datos JSON de recomendaciones:", error);
            }
        }
        
        // Fuente 3: Buscar en otro elemento de datos
        if (motosRecomendadas.length === 0) {
            const altJsonElement = document.querySelector('[data-recommendations]');
            if (altJsonElement) {
                try {
                    const jsonData = JSON.parse(altJsonElement.getAttribute('data-recommendations'));
                    if (Array.isArray(jsonData) && jsonData.length > 0) {
                        motosRecomendadas = jsonData;
                        console.log("Recomendaciones cargadas desde atributo data:", motosRecomendadas.length);
                    }
                } catch (error) {
                    console.error("Error al parsear datos de atributo:", error);
                }
            }
        }
    }
    
    // Limitar a máximo 4 motos recomendadas
    motosRecomendadas = motosRecomendadas.slice(0, 4);
    
    console.log(`Mostrando ${motosRecomendadas.length} recomendaciones de motos`);
    
    // Buscar el contenedor - intentando diferentes IDs por compatibilidad
    let recomendacionesContainer = document.getElementById('recomendaciones-container');
    
    if (!recomendacionesContainer) {
        // Intentar con IDs alternativos que podrían existir
        const alternativeIds = ['motos-recomendadas', 'recommendations-container', 'resultados-container'];
        for (const id of alternativeIds) {
            const container = document.getElementById(id);
            if (container) {
                recomendacionesContainer = container;
                console.log(`Contenedor encontrado con ID alternativo: ${id}`);
                break;
            }
        }
        
        // Si aún no se encuentra, buscar por clase
        if (!recomendacionesContainer) {
            const containerByClass = document.querySelector('.recomendaciones-grid, .recommendations-container');
            if (containerByClass) {
                recomendacionesContainer = containerByClass;
                console.log('Contenedor encontrado por clase');
            }
        }
    }
      // Si todavía no tenemos contenedor, crear uno
    if (!recomendacionesContainer) {
        console.warn("No se encontró contenedor de recomendaciones, creando uno nuevo");
        recomendacionesContainer = document.createElement('div');
        recomendacionesContainer.id = 'recomendaciones-container';
        recomendacionesContainer.className = 'recomendaciones-grid';
        
        // Buscar un lugar adecuado para insertarlo
        const mainContainer = document.querySelector('.main-container, main, .content-section');
        if (mainContainer) {
            // Si hay un título h1 o h2, insertar después de él
            const header = mainContainer.querySelector('h1, h2');
            if (header) {
                header.parentNode.insertBefore(recomendacionesContainer, header.nextSibling);
            } else {
                // De lo contrario, añadir al principio del contenedor principal
                mainContainer.prepend(recomendacionesContainer);
            }
        } else {
            // Si no hay contenedor principal, añadir al body
            document.body.appendChild(recomendacionesContainer);
        }
    }
    
    // Limpiar contenedor
    recomendacionesContainer.innerHTML = '';
    
    // Si no hay recomendaciones, mostrar mensaje
    if (motosRecomendadas.length === 0) {
        recomendacionesContainer.innerHTML = `
            <div class="no-recomendaciones">
                <i class="fas fa-exclamation-circle"></i>
                <h3>No se encontraron recomendaciones</h3>
                <p>Por favor, completa el test de preferencias para recibir recomendaciones personalizadas.</p>
                <a href="/test" class="btn btn-primary">Hacer test</a>
            </div>
        `;
        return;
    }
    
    // Generar HTML para cada moto recomendada
    motosRecomendadas.forEach((moto, index) => {
        // Manejar datos nulos o indefinidos
        const segurosEstandarizar = (obj, prop, defaultValue) => {
            if (!obj || obj[prop] === undefined || obj[prop] === null) {
                return defaultValue;
            }
            return obj[prop];
        };
        
        // Calcular porcentaje de coincidencia (si no existe, usar un valor predeterminado basado en la posición)
        const matchPercent = segurosEstandarizar(moto, 'match_percent', Math.max(95 - (index * 5), 75));
        
        // Crear elemento para la moto
        const motoElement = document.createElement('div');
        motoElement.className = 'recomendacion-card';
        motoElement.innerHTML = `
            <div class="recomendacion-header">
                <span class="match-percent">${matchPercent}% coincidencia</span>
                <h3>${segurosEstandarizar(moto, 'marca', 'Marca')} ${segurosEstandarizar(moto, 'modelo', 'Modelo')}</h3>
            </div>
            <div class="recomendacion-image">
                <img src="${segurosEstandarizar(moto, 'imagen', '/static/img/moto-placeholder.jpg')}" 
                     alt="${segurosEstandarizar(moto, 'marca', 'Moto')} ${segurosEstandarizar(moto, 'modelo', 'recomendada')}">
            </div>
            <div class="recomendacion-details">
                <div class="detail-row">
                    <span class="detail-label">Cilindrada:</span>
                    <span class="detail-value">${segurosEstandarizar(moto, 'cilindrada', 'N/A')} cc</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Potencia:</span>
                    <span class="detail-value">${segurosEstandarizar(moto, 'potencia', 'N/A')} HP</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Estilo:</span>
                    <span class="detail-value">${segurosEstandarizar(moto, 'estilo', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Precio:</span>
                    <span class="detail-value">Q${
                        typeof moto.precio === 'number' ? 
                        moto.precio.toLocaleString() : 
                        segurosEstandarizar(moto, 'precio', 'N/A')
                    }</span>
                </div>
            </div>
            <div class="recomendacion-footer">
                <a href="/motos/${segurosEstandarizar(moto, 'id', '')}" class="btn-ver-mas">Ver detalles</a>
                <a href="/concesionarios?moto=${segurosEstandarizar(moto, 'id', '')}" class="btn-concesionarios">Concesionarios</a>
            </div>
        `;
        
        // Añadir al contenedor
        recomendacionesContainer.appendChild(motoElement);
    });
      // Comprobar si tenemos la cantidad esperada de recomendaciones
    if (motosRecomendadas.length < 4) {
        console.warn(`Solo se encontraron ${motosRecomendadas.length} recomendaciones, se esperaban 4`);
        
        // Añadir una nota informativa si hay menos de 3 recomendaciones
        if (motosRecomendadas.length < 3) {
            const infoNote = document.createElement('div');
            infoNote.className = 'info-note';
            infoNote.innerHTML = `
                <p>Basado en tus preferencias, te mostramos ${motosRecomendadas.length} recomendación(es). 
                   Puedes <a href="/test">ajustar tus preferencias</a> para obtener más opciones.</p>
            `;
            
            // Añadir antes del primer elemento hijo o al principio si no tiene hijos
            if (recomendacionesContainer.firstChild) {
                recomendacionesContainer.insertBefore(infoNote, recomendacionesContainer.firstChild);
            } else {
                recomendacionesContainer.appendChild(infoNote);
            }
        }
    }
    
    console.log(`Se han mostrado ${motosRecomendadas.length} recomendaciones`);
    
    // Añadir evento para cargar más recomendaciones si es necesario
    if (motosRecomendadas.length > 0) {
        // Si existe un botón para cargar más, configurarlo
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', function() {
                // Solicitar más recomendaciones vía AJAX (si tienes una API para esto)
                fetch('/api/recommendations/more')
                    .then(response => response.json())
                    .then(data => {
                        if (data && data.length > 0) {
                            // Renderizar las nuevas recomendaciones
                            data.forEach(moto => {
                                // Reutilizar el código de renderizado...
                            });
                        } else {
                            alert('No hay más recomendaciones disponibles');
                            this.style.display = 'none'; // Ocultar botón
                        }
                    })
                    .catch(error => {
                        console.error('Error al cargar más recomendaciones:', error);
                    });
            });
        }
    }
});
