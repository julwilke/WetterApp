/*
 * Bootstrap-ähnliche Initialisierung für WetterApp
 * Behandelt Responsive-Verhalten und DOM-Interaktionen
 */

// Nach Seiten-Load: Hover-Animationen initialisieren
document.addEventListener('DOMContentLoaded', function() {
    // Hover-Animationen für Elemente mit 'data-bss-hover-animate' Attribut
    var hoverAnimationTriggerList = [].slice.call(document.querySelectorAll('[data-bss-hover-animate]'));
    hoverAnimationTriggerList.forEach(function (elem) {
        elem.addEventListener('mouseenter', function(e) { 
            e.target.classList.add('animated', e.target.dataset.bssHoverAnimate); 
        });
        elem.addEventListener('mouseleave', function(e) { 
            e.target.classList.remove('animated', e.target.dataset.bssHoverAnimate); 
        });
    });
}, false);