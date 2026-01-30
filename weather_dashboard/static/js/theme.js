/*
 * WetterApp Theme - Navigation & UI-Verhalten
 * Behandelt Sidebar-Toggle, Dropdowns und Scroll-to-Top Funktionalität
 */

(function() {
  "use strict";

  // Sidebar Toggle Funktionalität
  var sidebar = document.querySelector('.sidebar');
  var sidebarToggles = document.querySelectorAll('#sidebarToggle, #sidebarToggleTop');
  
  if (sidebar && sidebarToggles.length > 0) {
    for (var toggle of sidebarToggles) {
      toggle.addEventListener('click', function(e) {
        document.body.classList.toggle('sidebar-toggled');
        sidebar.classList.toggle('toggled');
      });
    }

    // Sidebar auf Resize bei kleinen Bildschirmen einklappen
    window.addEventListener('resize', function() {
      var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
      if (vw < 768 && sidebar.classList.contains('toggled')) {
        sidebar.classList.remove('toggled');
        document.body.classList.remove('sidebar-toggled');
      }
    });
  }

  // Scroll-to-Top Button
  var scrollToTop = document.querySelector('.scroll-to-top');
  if (scrollToTop) {
    window.addEventListener('scroll', function() {
      if (window.pageYOffset > 100) {
        scrollToTop.classList.add('show');
      } else {
        scrollToTop.classList.remove('show');
      }
    });

    scrollToTop.addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();

// Dropdown Verhalten (ersetzt Bootstrap Dropdown Logik)
(function() {
  document.addEventListener('click', function(e) {
    const toggle = e.target.closest('[data-bs-toggle="dropdown"]');
    if (toggle) {
      e.preventDefault();
      const dropdown = toggle.closest('.dropdown');
      if (!dropdown) return;
      
      // Andere Dropdowns schließen
      document.querySelectorAll('.dropdown.show').forEach(d => {
        if (d !== dropdown) {
          d.classList.remove('show');
          const t = d.querySelector('[data-bs-toggle="dropdown"]');
          if (t) t.setAttribute('aria-expanded', 'false');
        }
      });
      
      // Toggle aktuelles Dropdown
      const shown = dropdown.classList.contains('show');
      if (!shown) {
        dropdown.classList.add('show');
        toggle.setAttribute('aria-expanded', 'true');
      } else {
        dropdown.classList.remove('show');
        toggle.setAttribute('aria-expanded', 'false');
      }
    } else {
      // Klick außerhalb schließt Dropdowns
      if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown.show').forEach(d => {
          d.classList.remove('show');
          const t = d.querySelector('[data-bs-toggle="dropdown"]');
          if (t) t.setAttribute('aria-expanded', 'false');
        });
      }
    }
  });
  
  // ESC-Taste schließt Dropdowns
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.dropdown.show').forEach(d => {
        d.classList.remove('show');
        const t = d.querySelector('[data-bs-toggle="dropdown"]');
        if (t) t.setAttribute('aria-expanded', 'false');
      });
    }
  });
})();