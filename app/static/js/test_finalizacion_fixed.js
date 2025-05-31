/**
 * Controlador de finalización del test - Gestiona la transición final del test
 * y el envío de resultados al servidor para generar recomendaciones.
 * VERSIÓN CORREGIDA: Detecta rama técnica/práctica para captura apropiada de rangos
 */

// Función para finalizar el test y enviar resultados
function finalizarTest() {
    console.log("=== FINALIZANDO TEST ===");
    
    // FORZAR CAPTURA DE TODOS LOS SLIDERS SIN VERIFICAR VISIBILIDAD
    
    // Presupuesto - buscar sin verificar estado
    const presupuestoMinSlider = document.getElementById('presupuesto_min');
    const presupuestoMaxSlider = document.getElementById('presupuesto_max');
    if (presupuestoMinSlider && presupuestoMaxSlider) {
        window.testResults.presupuesto_min = parseInt(presupuestoMinSlider.value);
        window.testResults.presupuesto_max = parseInt(presupuestoMaxSlider.value);
        console.log("Presupuesto capturado:", window.testResults.presupuesto_min, window.testResults.presupuesto_max);
    }

    // Año - buscar sin verificar estado
    const anoMinSlider = document.getElementById('ano_min');
    const anoMaxSlider = document.getElementById('ano_max');
    if (anoMinSlider && anoMaxSlider) {
        window.testResults.ano_min = parseInt(anoMinSlider.value);
        window.testResults.ano_max = parseInt(anoMaxSlider.value);
        console.log("Año capturado:", window.testResults.ano_min, window.testResults.ano_max);
    }

    // Peso - buscar sin verificar estado
    const pesoMinSlider = document.getElementById('peso_min');
    const pesoMaxSlider = document.getElementById('peso_max');
    if (pesoMinSlider && pesoMaxSlider) {
        window.testResults.peso_min = parseInt(pesoMinSlider.value);
        window.testResults.peso_max = parseInt(pesoMaxSlider.value);
        console.log("Peso capturado:", window.testResults.peso_min, window.testResults.peso_max);
    }

    // Cilindrada - buscar sin verificar estado
    const cilindradaMinSlider = document.getElementById('cilindrada_min');
    const cilindradaMaxSlider = document.getElementById('cilindrada_max');
    if (cilindradaMinSlider && cilindradaMaxSlider) {
        window.testResults.cilindrada_min = parseInt(cilindradaMinSlider.value);
        window.testResults.cilindrada_max = parseInt(cilindradaMaxSlider.value);
        console.log("Cilindrada capturada:", window.testResults.cilindrada_min, window.testResults.cilindrada_max);
    }

    // Potencia - buscar sin verificar estado
    const potenciaMinSlider = document.getElementById('potencia_min');
    const potenciaMaxSlider = document.getElementById('potencia_max');
    if (potenciaMinSlider && potenciaMaxSlider) {
        window.testResults.potencia_min = parseInt(potenciaMinSlider.value);
        window.testResults.potencia_max = parseInt(potenciaMaxSlider.value);
        console.log("Potencia capturada:", window.testResults.potencia_min, window.testResults.potencia_max);
    }

    // Torque - buscar sin verificar estado
    const torqueMinSlider = document.getElementById('torque_min');
    const torqueMaxSlider = document.getElementById('torque_max');
    if (torqueMinSlider && torqueMaxSlider) {
        window.testResults.torque_min = parseInt(torqueMinSlider.value);
        window.testResults.torque_max = parseInt(torqueMaxSlider.value);
        console.log("Torque capturado:", window.testResults.torque_min, window.testResults.torque_max);
    }

    // FORZAR CAPTURA DE TODOS LOS SELECTS
    const allSelects = document.querySelectorAll('select');
    allSelects.forEach(select => {
        if (select.value && (select.name || select.id)) {
            const key = select.name || select.id;
            window.testResults[key] = select.value;
            console.log(`Select capturado: ${key} = ${select.value}`);
        }
    });

    console.log("=== DATOS FINALES CAPTURADOS ===", window.testResults);
    
    // DETECTAR RAMA SELECCIONADA AUTOMÁTICAMENTE
    const ramaSeleccionada = window.testResults.interesa_especificaciones || 'no';
    const esTecnica = ramaSeleccionada === 'si';
    
    // Preparar datos para enviar al servidor
    const testData = {
        // Datos básicos del test
        experiencia: window.testResults.experiencia,
        uso: window.testResults.uso,
        uso_previsto: window.testResults.uso_previsto,
        
        // RANGOS CUANTITATIVOS DIRECTOS (sin conversión)
        presupuesto_min: window.testResults.presupuesto_min,
        presupuesto_max: window.testResults.presupuesto_max,
        ano_min: window.testResults.ano_min,
        ano_max: window.testResults.ano_max,
        cilindrada_min: window.testResults.cilindrada_min,
        cilindrada_max: window.testResults.cilindrada_max,
        potencia_min: window.testResults.potencia_min,
        potencia_max: window.testResults.potencia_max,
        torque_min: window.testResults.torque_min,
        torque_max: window.testResults.torque_max,
        peso_min: window.testResults.peso_min,
        peso_max: window.testResults.peso_max,
        
        // Indicador de qué rama fue seleccionada
        interesa_especificaciones: ramaSeleccionada,
        rama_seleccionada: esTecnica ? 'tecnica' : 'practica',
        
        // PREFERENCIAS CATEGÓRICAS
        estilos: window.testResults.estilos || {},
        marcas: window.testResults.marcas || {},
        
        // Control
        reset_recommendation: 'true'
    };
    
    console.log(`Datos finales para enviar (rama ${esTecnica ? 'técnica' : 'práctica'}):`, JSON.stringify(testData, null, 2));
    
    // Crear formulario para enviar datos
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = "/guardar_test";
    form.style.display = 'none';
    
    // Agregar campos al formulario
    for (const key in testData) {
        if (testData.hasOwnProperty(key)) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            
            // Convertir objetos a JSON string
            if (typeof testData[key] === 'object') {
                input.value = JSON.stringify(testData[key]);
            } else {
                input.value = testData[key];
            }
            
            form.appendChild(input);
            console.log(`Campo: ${key} = ${input.value} (${typeof testData[key]})`);
        }
    }
    
    // Agregar formulario al documento y enviarlo
    document.body.appendChild(form);
    console.log("Enviando formulario con detección de rama técnica/práctica...");
    form.submit();
}

// AGREGAR EVENT LISTENER PARA EL BOTÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔧 Configurando botón de finalización...");
    
    // Buscar TODOS los posibles botones de finalización
    const botonesFinalizacion = [
        document.getElementById('ver-recomendaciones'),
        document.querySelector('.btn-finalizar'),
        document.querySelector('button[onclick*="finalizarTest"]'),
        document.querySelector('button[onclick*="finalizar"]'),
        document.querySelector('#finalizar-test'),
        document.querySelector('.finalizar-test')
    ];
    
    botonesFinalizacion.forEach(boton => {
        if (boton) {
            console.log("✅ Botón encontrado:", boton);
            
            // Limpiar eventos previos y agregar nuevo
            boton.removeEventListener('click', finalizarTest);
            boton.addEventListener('click', function(e) {
                e.preventDefault();
                console.log("🚀 Botón clickeado - ejecutando finalización...");
                finalizarTest();
            });
            
            // TAMBIÉN asegurar que el onclick funcione
            boton.onclick = function(e) {
                e.preventDefault();
                console.log("🚀 Onclick ejecutado - ejecutando finalización...");
                finalizarTest();
                return false;
            };
        }
    });
    
    // Si no encuentra botones, buscar por texto
    if (!botonesFinalizacion.some(b => b)) {
        const todosLosBotones = document.querySelectorAll('button');
        todosLosBotones.forEach(boton => {
            if (boton.textContent.toLowerCase().includes('recomend') || 
                boton.textContent.toLowerCase().includes('finalizar')) {
                console.log("✅ Botón encontrado por texto:", boton);
                boton.onclick = finalizarTest;
            }
        });
    }
});

// Exportar para uso global
window.finalizarTest = finalizarTest;

console.log("Módulo de finalización del test CORREGIDO (con detección de rama) cargado correctamente");