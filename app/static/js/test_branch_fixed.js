/**
 * Controlador de bifurcación para el test de preferencias de motos
 * Maneja correctamente la visualización de preguntas técnicas vs. prácticas
 */

// Esperar a que el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Test branch controller loaded');
    
    // Elementos principales
    const interesaEspecificacionesSelect = document.getElementById('interesa_especificaciones');
    const ramaTecnicaPreguntas = document.querySelectorAll('.rama-tecnica');
    const ramaPracticaPreguntas = document.querySelectorAll('.rama-practica');
    
    console.log(`📋 Encontradas ${ramaTecnicaPreguntas.length} preguntas técnicas`);
    console.log(`📋 Encontradas ${ramaPracticaPreguntas.length} preguntas prácticas`);
    
    // Inicializar el estado (ocultar todas las preguntas de rama)
    function inicializarRamas() {
        console.log('🔄 Inicializando ramas...');
        
        // Inicialmente ocultar todas las preguntas de rama
        ramaTecnicaPreguntas.forEach(pregunta => {
            pregunta.classList.remove('active');
            pregunta.style.display = 'none';
            pregunta.setAttribute('data-hidden', 'true');
        });
        
        ramaPracticaPreguntas.forEach(pregunta => {
            pregunta.classList.remove('active');
            pregunta.style.display = 'none';
            pregunta.setAttribute('data-hidden', 'true');
        });
        
        // Si ya hay una selección, aplicarla
        if (interesaEspecificacionesSelect && interesaEspecificacionesSelect.value) {
            manejarCambioRama();
        }
    }
    
    // Configurar evento para el cambio de selección
    if (interesaEspecificacionesSelect) {
        console.log('🔌 Configurando evento para selector de rama');
        interesaEspecificacionesSelect.addEventListener('change', manejarCambioRama);
    }    // Función que maneja el cambio de rama
    function manejarCambioRama() {
        const seleccion = interesaEspecificacionesSelect.value;
        console.log(`🔀 Preparando rama: ${seleccion}`);
        
        if (!seleccion || seleccion === '') {
            // Si no hay selección, ocultar todas las preguntas de rama
            ramaTecnicaPreguntas.forEach(pregunta => {
                pregunta.classList.remove('active');
                pregunta.style.display = 'none';
                pregunta.setAttribute('data-hidden', 'true');
            });
            ramaPracticaPreguntas.forEach(pregunta => {
                pregunta.classList.remove('active');
                pregunta.style.display = 'none';
                pregunta.setAttribute('data-hidden', 'true');
            });
            return;
        }
        
        // PASO 1: Ocultar todas las preguntas de ambas ramas (pero NO la bifurcación)
        ramaTecnicaPreguntas.forEach(pregunta => {
            pregunta.classList.remove('active');
            pregunta.style.display = 'none';
        });
        ramaPracticaPreguntas.forEach(pregunta => {
            pregunta.classList.remove('active');
            pregunta.style.display = 'none';
        });
        
        // PASO 2: Configurar qué rama estará disponible para navegación
        if (seleccion === 'si') {
            // Preparar rama técnica (pero no mostrarla aún)
            ramaTecnicaPreguntas.forEach(pregunta => {
                pregunta.setAttribute('data-hidden', 'false');
            });
            ramaPracticaPreguntas.forEach(pregunta => {
                pregunta.setAttribute('data-hidden', 'true');
            });
            console.log(`✅ Rama técnica preparada (${ramaTecnicaPreguntas.length} preguntas disponibles)`);
            
        } else if (seleccion === 'no') {
            // Preparar rama práctica (pero no mostrarla aún)
            ramaPracticaPreguntas.forEach(pregunta => {
                pregunta.setAttribute('data-hidden', 'false');
            });
            ramaTecnicaPreguntas.forEach(pregunta => {
                pregunta.setAttribute('data-hidden', 'true');
            });
            console.log(`✅ Rama práctica preparada (${ramaPracticaPreguntas.length} preguntas disponibles)`);
        }
        
        // PASO 3: Mantener la pregunta de bifurcación visible y activa
        const preguntaBifurcacion = document.getElementById('pregunta-3');
        if (preguntaBifurcacion) {
            preguntaBifurcacion.classList.add('active');
            preguntaBifurcacion.style.display = 'block';
        }
        
        // PASO 4: Habilitar navegación pero NO cambiar de pregunta automáticamente
        document.querySelectorAll('.test-navigation').forEach(nav => {
            nav.classList.remove('hidden');
        });
        
        console.log(`✅ Rama ${seleccion} lista. Presiona 'Siguiente' para continuar.`);
    }
    
    // Sobrescribir la función de navegación del test original
    if (window.testState && typeof window.findNextVisibleStage === 'function') {
        console.log('🔄 Sobrescribiendo funciones de navegación existentes');
        
        // Guardar referencia a la función original
        const originalFindNextVisibleStage = window.findNextVisibleStage;
        const originalFindPreviousVisibleStage = window.findPreviousVisibleStage;
          // Sobrescribir findNextVisibleStage
        window.findNextVisibleStage = function(currentIndex) {
            console.log(`🔍 Buscando siguiente etapa visible después de ${currentIndex}`);
            
            // Si estamos en una bifurcación y hay una rama seleccionada
            if (interesaEspecificacionesSelect && interesaEspecificacionesSelect.value) {
                const ramaTecnicaActiva = interesaEspecificacionesSelect.value === 'si';
                const ramaPracticaActiva = interesaEspecificacionesSelect.value === 'no';
                
                const currentStage = window.testState.stageContainers[currentIndex];
                
                // CASO ESPECIAL: Si estamos en la pregunta de bifurcación (pregunta-3), ir a la primera pregunta de la rama
                if (currentStage && currentStage.id === 'pregunta-3') {
                    console.log(`🔀 Desde bifurcación hacia primera pregunta de rama`);
                    
                    if (ramaTecnicaActiva && ramaTecnicaPreguntas.length > 0) {
                        const primeraTecnica = ramaTecnicaPreguntas[0];
                        const indicePrimeraTecnica = Array.from(window.testState.stageContainers).indexOf(primeraTecnica);
                        console.log(`✅ Ir a primera pregunta técnica: ${indicePrimeraTecnica}`);
                        return indicePrimeraTecnica;
                    }
                    
                    if (ramaPracticaActiva && ramaPracticaPreguntas.length > 0) {
                        const primeraPractica = ramaPracticaPreguntas[0];
                        const indicePrimeraPractica = Array.from(window.testState.stageContainers).indexOf(primeraPractica);
                        console.log(`✅ Ir a primera pregunta práctica: ${indicePrimeraPractica}`);
                        return indicePrimeraPractica;
                    }
                }
                
                let nextIndex = currentIndex + 1;
                while (nextIndex < window.testState.stageContainers.length) {
                    const stage = window.testState.stageContainers[nextIndex];
                    
                    // Verificar si la pregunta está oculta por el atributo data-hidden
                    if (stage.hasAttribute('data-hidden')) {
                        console.log(`⏭️ Saltando pregunta oculta: ${stage.id}`);
                        nextIndex++;
                        continue;
                    }
                    
                    // Si es pregunta general (no de rama)
                    if (!stage.classList.contains('rama-tecnica') && !stage.classList.contains('rama-practica')) {
                        console.log(`✅ Encontrada siguiente pregunta general: ${nextIndex}`);
                        return nextIndex;
                    }
                    
                    // Si es técnica y está activa esa rama
                    if (stage.classList.contains('rama-tecnica') && ramaTecnicaActiva) {
                        console.log(`✅ Encontrada siguiente pregunta técnica: ${nextIndex}`);
                        return nextIndex;
                    }
                    
                    // Si es práctica y está activa esa rama
                    if (stage.classList.contains('rama-practica') && ramaPracticaActiva) {
                        console.log(`✅ Encontrada siguiente pregunta práctica: ${nextIndex}`);
                        return nextIndex;
                    }
                    
                    nextIndex++;
                }
                
                return -1; // No hay más etapas visibles
            }
            
            // Si no estamos en una bifurcación, usar la función original
            return originalFindNextVisibleStage(currentIndex);
        };
          // Sobrescribir findPreviousVisibleStage
        window.findPreviousVisibleStage = function(currentIndex) {
            console.log(`🔍 Buscando etapa previa visible antes de ${currentIndex}`);
            
            // Si estamos en una bifurcación y hay una rama seleccionada
            if (interesaEspecificacionesSelect && interesaEspecificacionesSelect.value) {
                const ramaTecnicaActiva = interesaEspecificacionesSelect.value === 'si';
                const ramaPracticaActiva = interesaEspecificacionesSelect.value === 'no';
                
                const currentStage = window.testState.stageContainers[currentIndex];
                
                // CASO ESPECIAL: Si estamos en la primera pregunta de una rama, volver a la bifurcación
                if (currentStage && 
                    (currentStage.classList.contains('rama-tecnica') || currentStage.classList.contains('rama-practica'))) {
                    
                    // Verificar si es la primera pregunta de la rama correspondiente
                    if (ramaTecnicaActiva && currentStage === ramaTecnicaPreguntas[0]) {
                        console.log(`🔙 Primera pregunta técnica, volviendo a bifurcación`);
                        // Buscar el índice de la pregunta de bifurcación (pregunta-3)
                        const preguntaBifurcacion = document.getElementById('pregunta-3');
                        if (preguntaBifurcacion) {
                            const bifurcacionIndex = Array.from(window.testState.stageContainers).indexOf(preguntaBifurcacion);
                            return bifurcacionIndex;
                        }
                    }
                    
                    if (ramaPracticaActiva && currentStage === ramaPracticaPreguntas[0]) {
                        console.log(`🔙 Primera pregunta práctica, volviendo a bifurcación`);
                        // Buscar el índice de la pregunta de bifurcación (pregunta-3)
                        const preguntaBifurcacion = document.getElementById('pregunta-3');
                        if (preguntaBifurcacion) {
                            const bifurcacionIndex = Array.from(window.testState.stageContainers).indexOf(preguntaBifurcacion);
                            return bifurcacionIndex;
                        }
                    }
                }
                
                let prevIndex = currentIndex - 1;
                while (prevIndex >= 0) {
                    const stage = window.testState.stageContainers[prevIndex];
                    
                    // Verificar si la pregunta está oculta por el atributo data-hidden
                    if (stage.hasAttribute('data-hidden')) {
                        console.log(`⏮️ Saltando pregunta oculta: ${stage.id}`);
                        prevIndex--;
                        continue;
                    }
                    
                    // Si es pregunta general (no de rama)
                    if (!stage.classList.contains('rama-tecnica') && !stage.classList.contains('rama-practica')) {
                        console.log(`✅ Encontrada etapa previa general: ${prevIndex}`);
                        return prevIndex;
                    }
                    
                    // Si es técnica y está activa esa rama
                    if (stage.classList.contains('rama-tecnica') && ramaTecnicaActiva) {
                        console.log(`✅ Encontrada etapa previa técnica: ${prevIndex}`);
                        return prevIndex;
                    }
                    
                    // Si es práctica y está activa esa rama
                    if (stage.classList.contains('rama-practica') && ramaPracticaActiva) {
                        console.log(`✅ Encontrada etapa previa práctica: ${prevIndex}`);
                        return prevIndex;
                    }
                    
                    prevIndex--;
                }
                
                return -1; // No hay etapas previas visibles
            }
            
            // Si no estamos en una bifurcación, usar la función original
            return originalFindPreviousVisibleStage(currentIndex);
        };
        
        // Sobrescribir getVisibleStagesCount
        const originalGetVisibleStagesCount = window.getVisibleStagesCount;
        window.getVisibleStagesCount = function() {
            console.log(`📊 Recalculando etapas visibles`);
            
            // Si estamos en una bifurcación y hay una rama seleccionada
            if (interesaEspecificacionesSelect && interesaEspecificacionesSelect.value) {
                const ramaTecnicaActiva = interesaEspecificacionesSelect.value === 'si';
                const ramaPracticaActiva = interesaEspecificacionesSelect.value === 'no';
                
                let count = 0;
                
                // Contar preguntas que no están ocultas
                window.testState.stageContainers.forEach(stage => {
                    if (stage.hasAttribute('data-hidden')) {
                        return; // Saltar preguntas ocultas
                    }
                    
                    // Preguntas generales
                    if (!stage.classList.contains('rama-tecnica') && !stage.classList.contains('rama-practica')) {
                        count++;
                    }
                    // Preguntas técnicas (si esa rama está activa)
                    else if (stage.classList.contains('rama-tecnica') && ramaTecnicaActiva) {
                        count++;
                    }
                    // Preguntas prácticas (si esa rama está activa)
                    else if (stage.classList.contains('rama-practica') && ramaPracticaActiva) {
                        count++;
                    }
                });
                
                console.log(`📊 Total de etapas visibles: ${count}`);
                return count;
            }
            
            // Si no estamos en una bifurcación, usar la función original
            return originalGetVisibleStagesCount();
        };
        
        // Sobrescribir navigateToNextStage
        const originalNavigateToNextStage = window.navigateToNextStage;
        window.navigateToNextStage = function() {
            console.log(`⏭️ Navegando a siguiente etapa`);
            
            const nextIndex = findNextVisibleStage(window.testState.currentStageIndex);
            if (nextIndex !== -1) {
                showStage(nextIndex);
                window.testState.currentStageIndex = nextIndex;
                updateProgressBar(nextIndex, getVisibleStagesCount());
            } else {
                console.log('🏁 Fin del test alcanzado');
                // Mostrar el botón finalizar si estamos en la última etapa
                document.getElementById('finalizarBtn').classList.remove('hidden');
            }
        };
          // Sobrescribir navigateToPreviousStage
        const originalNavigateToPreviousStage = window.navigateToPreviousStage;
        window.navigateToPreviousStage = function() {
            console.log(`⏮️ Navegando a etapa anterior`);
            
            const prevIndex = findPreviousVisibleStage(window.testState.currentStageIndex);
            if (prevIndex !== -1) {
                const prevStage = window.testState.stageContainers[prevIndex];
                
                // CASO ESPECIAL: Si volvemos a la pregunta de bifurcación, resetear estado
                if (prevStage && prevStage.id === 'pregunta-3') {
                    console.log(`🔙 Regresando a pregunta de bifurcación`);
                    
                    // Ocultar todas las preguntas de rama
                    ramaTecnicaPreguntas.forEach(pregunta => {
                        pregunta.classList.remove('active');
                        pregunta.style.display = 'none';
                    });
                    ramaPracticaPreguntas.forEach(pregunta => {
                        pregunta.classList.remove('active');
                        pregunta.style.display = 'none';
                    });
                    
                    // Mostrar la pregunta de bifurcación
                    prevStage.classList.add('active');
                    prevStage.style.display = 'block';
                } else {
                    // Navegación normal
                    showStage(prevIndex);
                }
                
                window.testState.currentStageIndex = prevIndex;
                updateProgressBar(prevIndex, getVisibleStagesCount());
                
                // Ocultar botón finalizar si retrocedemos
                const finalizarBtn = document.getElementById('finalizarBtn');
                if (finalizarBtn) {
                    finalizarBtn.classList.add('hidden');
                }
            }
        };        // Sobrescribir showStage para gestionar correctamente las ramas
        const originalShowStage = window.showStage;
        window.showStage = function(index) {
            console.log(`🎯 Mostrando etapa: ${index}`);
            
            // PASO 1: Ocultar TODAS las preguntas primero
            window.testState.stageContainers.forEach(stage => {
                stage.classList.remove('active');
                stage.style.display = 'none';
            });
            
            // PASO 2: Mostrar SOLO la etapa especificada
            const targetStage = window.testState.stageContainers[index];
            if (!targetStage) {
                console.error(`❌ No se encontró etapa en índice ${index}`);
                return;
            }
            
            // Mostrar la pregunta actual
            targetStage.classList.add('active');
            targetStage.style.display = 'block';
            console.log(`👁️ Mostrando pregunta: ${targetStage.id}`);
            
            // PASO 3: Gestión especial para ramas
            const esPreguntaTecnica = targetStage.classList.contains('rama-tecnica');
            const esPreguntaPractica = targetStage.classList.contains('rama-practica');
            
            // Asegurar que las preguntas de la rama no seleccionada permanezcan ocultas
            if (esPreguntaTecnica) {
                ramaPracticaPreguntas.forEach(p => {
                    p.classList.remove('active');
                    p.style.display = 'none';
                });
                console.log(`✅ Mostrando pregunta técnica: ${targetStage.id}`);
            }
            
            if (esPreguntaPractica) {
                ramaTecnicaPreguntas.forEach(p => {
                    p.classList.remove('active');
                    p.style.display = 'none';
                });
                console.log(`✅ Mostrando pregunta práctica: ${targetStage.id}`);
            }
            
            // Caso especial: si estamos navegando a la bifurcación, 
            // asegurar que las preguntas de rama no aparezcan
            if (targetStage.id === 'pregunta-3') {
                console.log('🔀 Mostrando pregunta de bifurcación');
                ramaTecnicaPreguntas.forEach(p => {
                    p.classList.remove('active');
                    p.style.display = 'none';
                });
                ramaPracticaPreguntas.forEach(p => {
                    p.classList.remove('active');
                    p.style.display = 'none';
                });
            }
            
            // IMPORTANTE: Asegurar que preguntas anteriores estén ocultas
            // para evitar que la pregunta 3 aparezca debajo de la 1 y 2
            const currentIndex = Array.from(window.testState.stageContainers).indexOf(targetStage);
            for (let i = 0; i < currentIndex; i++) {
                const prevQuestion = window.testState.stageContainers[i];
                prevQuestion.classList.remove('active');
                prevQuestion.style.display = 'none';
            }
        };
    }
    
    // Función para actualizar la barra de progreso
    function actualizarBarraProgreso() {
        if (window.testState && typeof window.updateProgressBar === 'function') {
            window.updateProgressBar(window.testState.currentStageIndex, window.getVisibleStagesCount());
        }
    }
    
    // Inicializar las ramas al cargar
    inicializarRamas();
});