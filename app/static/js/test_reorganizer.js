// Reorganizador de preguntas para el test
// Este script asegura que las preguntas aparecen en el orden correcto

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Reorganizador de preguntas iniciado');
    
    // Función para reorganizar las preguntas en el DOM
    function reorganizarPreguntas() {
        const contenedor = document.querySelector('.test-questions');
        if (!contenedor) {
            console.error('❌ No se encontró el contenedor de preguntas');
            return;
        }
        
        // Obtener todas las preguntas
        const preguntas = Array.from(document.querySelectorAll('.pregunta'));
        if (preguntas.length === 0) {
            console.error('❌ No se encontraron preguntas para reorganizar');
            return;
        }
        
        console.log(`📋 Encontradas ${preguntas.length} preguntas para reorganizar`);
        
        // Ordenar las preguntas generales por su ID numérico
        const preguntasGenerales = preguntas.filter(p => 
            !p.classList.contains('rama-tecnica') && 
            !p.classList.contains('rama-practica')
        );
        
        preguntasGenerales.sort((a, b) => {
            const numA = parseInt(a.id.replace('pregunta-', ''));
            const numB = parseInt(b.id.replace('pregunta-', ''));
            return numA - numB;
        });
        
        console.log(`📋 Preguntas generales: ${preguntasGenerales.length}`);
        
        // Obtener las preguntas de rama
        const preguntasTecnicas = preguntas.filter(p => p.classList.contains('rama-tecnica'));
        const preguntasPracticas = preguntas.filter(p => p.classList.contains('rama-practica'));
        
        console.log(`📋 Preguntas técnicas: ${preguntasTecnicas.length}`);
        console.log(`📋 Preguntas prácticas: ${preguntasPracticas.length}`);
        
        // Primero limpiar el contenedor
        while (contenedor.firstChild) {
            contenedor.removeChild(contenedor.firstChild);
        }
        
        // Ahora agregar las preguntas en orden
        preguntasGenerales.forEach(pregunta => {
            contenedor.appendChild(pregunta);
        });
        
        // Agregar las preguntas de rama al final
        preguntasTecnicas.forEach(pregunta => {
            contenedor.appendChild(pregunta);
        });
        
        preguntasPracticas.forEach(pregunta => {
            contenedor.appendChild(pregunta);
        });
        
        console.log('✅ Preguntas reorganizadas exitosamente');
        
        // Asegurar que solo la primera pregunta está activa
        preguntas.forEach((pregunta, index) => {
            if (index === 0) {
                pregunta.classList.add('active');
                pregunta.style.display = 'block';
            } else {
                pregunta.classList.remove('active');
                pregunta.style.display = 'none';
            }
        });
    }
    
    // Ejecutar la reorganización
    setTimeout(reorganizarPreguntas, 100);
});
