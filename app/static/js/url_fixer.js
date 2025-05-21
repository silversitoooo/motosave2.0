/* 
 * url_fixer.js - Corrige problemas comunes con las URLs en la aplicación MotoMatch
 * 
 * Este script arregla automáticamente problemas con url_for() en los templates
 * en caso de que haya inconsistencias entre los blueprints y las rutas.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('URL Fixer: Iniciando corrección de enlaces');
    
    // Mapa de destinos comunes
    const commonDestinations = {
        'dashboard': '/dashboard',
        'login': '/login',
        'register': '/register',
        'home': '/',
        'index': '/',
        'friends': '/friends',
        'test': '/test',
        'moto_ideal': '/moto_ideal',
        'populares': '/populares',
        'motos-recomendadas': '/motos-recomendadas'
    };
    
    // Arreglar enlaces rotos
    function fixBrokenLinks() {
        const links = document.querySelectorAll('a');
        console.log(`URL Fixer: Verificando ${links.length} enlaces`);
        
        links.forEach(link => {
            // Verificar si el enlace parece estar roto
            if (link.href.includes('None') || 
                link.href.includes('undefined') || 
                link.href.includes('%7B%7B') ||  // {{ codificado en URL
                link.href.includes('%7D%7D')) {  // }} codificado en URL
                
                console.log(`URL Fixer: Enlace roto detectado - ${link.href}`);
                
                // Tratar de deducir el destino correcto
                const text = link.textContent.toLowerCase().trim();
                const classes = Array.from(link.classList).join(' ').toLowerCase();
                
                // Buscar pistas en el texto
                for (const [keyword, url] of Object.entries(commonDestinations)) {
                    if (text.includes(keyword) || classes.includes(keyword)) {
                        link.href = url;
                        console.log(`URL Fixer: Corregido enlace a ${url} basado en el texto "${text}"`);
                        break;
                    }
                }
                
                // Si tiene un ícono, usar eso como pista
                const icon = link.querySelector('i, .fa, .fas, .far, .fab');
                if (icon && !link.href.startsWith('http')) {
                    const iconClasses = Array.from(icon.classList).join(' ').toLowerCase();
                    
                    if (iconClasses.includes('user') || iconClasses.includes('users')) {
                        link.href = '/friends';
                    } else if (iconClasses.includes('motorcycle')) {
                        link.href = '/populares';
                    } else if (iconClasses.includes('star')) {
                        link.href = '/moto_ideal';
                    } else if (iconClasses.includes('home') || iconClasses.includes('dashboard')) {
                        link.href = '/dashboard';
                    } else if (iconClasses.includes('brain') || iconClasses.includes('question')) {
                        link.href = '/test';
                    } else if (iconClasses.includes('thumbs-up') || iconClasses.includes('heart')) {
                        link.href = '/motos-recomendadas';
                    }
                }
            }
        });
    }
    
    // Arreglar formularios con problemas
    function fixBrokenForms() {
        const forms = document.querySelectorAll('form');
        console.log(`URL Fixer: Verificando ${forms.length} formularios`);
        
        forms.forEach(form => {
            if (form.action.includes('None') || 
                form.action.includes('undefined') || 
                form.action.includes('%7B%7B') || 
                form.action.includes('%7D%7D')) {
                
                console.log(`URL Fixer: Formulario roto detectado - ${form.action}`);
                
                // Intentar identificar el tipo de formulario
                if (form.querySelector('input[name="username"]') && form.querySelector('input[name="password"]')) {
                    if (form.querySelector('input[name="confirm_password"]')) {
                        form.action = '/register';
                    } else {
                        form.action = '/login';
                    }
                    console.log(`URL Fixer: Corregido formulario a ${form.action}`);
                } else if (form.querySelector('input[name="amigo"]')) {
                    if (form.querySelector('.add-friend-btn') || form.querySelector('[class*="add"]')) {
                        form.action = '/agregar_amigo';
                    } else if (form.querySelector('.remove-friend-btn') || form.querySelector('[class*="remove"]')) {
                        form.action = '/eliminar_amigo';
                    }
                    console.log(`URL Fixer: Corregido formulario a ${form.action}`);
                } else if (form.querySelector('input[name="moto_id"]') || form.querySelector('input[name="motoId"]')) {
                    form.action = '/set_ideal_moto';
                    console.log(`URL Fixer: Corregido formulario de moto ideal a ${form.action}`);
                } else if (form.querySelector('input[name="experiencia"]') || form.querySelector('select[name="experiencia"]')) {
                    form.action = '/guardar_test';
                    console.log(`URL Fixer: Corregido formulario de test a ${form.action}`);
                } else if (form.classList.contains('like-form') || form.classList.contains('moto-like')) {
                    form.action = '/like_moto';
                    console.log(`URL Fixer: Corregido formulario de like a ${form.action}`);
                }
            }
        });
    }
    
    // Corregir enlaces dinamizados con data-action
    function fixDynamicElements() {
        const dynamicElements = document.querySelectorAll('[data-action]');
        
        dynamicElements.forEach(el => {
            const action = el.getAttribute('data-action');
            if (!action || action.includes('{{') || action.includes('}}')) {
                const elClasses = Array.from(el.classList).join(' ').toLowerCase();
                
                if (elClasses.includes('like')) {
                    el.setAttribute('data-action', '/like_moto');
                } else if (elClasses.includes('ideal')) {
                    el.setAttribute('data-action', '/set_ideal_moto');
                }
            }
        });
    }
    
    // Ejecutar todas las correcciones
    fixBrokenLinks();
    fixBrokenForms();
    fixDynamicElements();
    
    console.log('URL Fixer: Correcciones completadas');
});
