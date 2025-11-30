(function() {
  "use strict"; // Start of use strict

  var sidebar = document.querySelector('.sidebar');
  var sidebarToggles = document.querySelectorAll('#sidebarToggle, #sidebarToggleTop');
  
  if (sidebar) {
    
    // NOTE: bootstrap.Collapse dependency removed — keep a list for compatibility if needed
    var collapseElementList = [].slice.call(document.querySelectorAll('.sidebar .collapse'));
    var sidebarCollapseList = []; // we don't implement full collapse behavior; not used in template

    for (var toggle of sidebarToggles) {

      // Toggle the side navigation
      toggle.addEventListener('click', function(e) {
        document.body.classList.toggle('sidebar-toggled');
        sidebar.classList.toggle('toggled');

        if (sidebar.classList.contains('toggled')) {
          // If we later add collapsible sections, hide them here
          sidebarCollapseList.forEach(function(bsCollapse){ if (bsCollapse && typeof bsCollapse.hide === 'function') { bsCollapse.hide(); } });
        };
      });
    }

    // Close any open menu accordions when window is resized below 768px
    window.addEventListener('resize', function() {
      var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);

      if (vw < 768) {
        sidebarCollapseList.forEach(function(bsCollapse){ if (bsCollapse && typeof bsCollapse.hide === 'function') { bsCollapse.hide(); } });
      };
    });
  }

  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  
  // Support scrolling inside the sidebar without affecting the main content when using a fixed nav
  var fixedNavigation = document.querySelector('body.fixed-nav .sidebar');
  if (fixedNavigation) {
    fixedNavigation.addEventListener('wheel', function(e){
      var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
      if (vw > 768) {
        var delta = e.deltaY;
        this.scrollTop += delta; // scroll the sidebar itself
        e.preventDefault();
      }
    });
  }

  var scrollToTop = document.querySelector('.scroll-to-top');
  
  if (scrollToTop) {
    
    // Scroll to top button appear
    window.addEventListener('scroll', function() {
      var scrollDistance = window.pageYOffset;

      //check if user is scrolling up
      if (scrollDistance > 100) {
        scrollToTop.classList.add('show');
      } else {
        scrollToTop.classList.remove('show');
      }
    });

    // Smooth scroll when clicking the scroll-to-top button
    scrollToTop.addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

})(); // End of use strict

// Minimal dropdown handler to replace the bootstrap.js dropdown behaviour
(function(){
  // Toggle dropdowns when an element with [data-bs-toggle="dropdown"] is clicked
  document.addEventListener('click', function(e){
    const toggle = e.target.closest('[data-bs-toggle="dropdown"]');
    if (toggle) {
      e.preventDefault();
      const dropdown = toggle.closest('.dropdown');
      if (!dropdown) return;
      const shown = dropdown.classList.contains('show');
      // close all other dropdowns
      document.querySelectorAll('.dropdown.show').forEach(d => {
        if (d !== dropdown) {
          d.classList.remove('show');
          const t = d.querySelector('[data-bs-toggle="dropdown"]');
          if (t) t.setAttribute('aria-expanded', 'false');
        }
      });
      if (!shown) {
        dropdown.classList.add('show');
        toggle.setAttribute('aria-expanded', 'true');
      } else {
        dropdown.classList.remove('show');
        toggle.setAttribute('aria-expanded', 'false');
      }
    } else {
      // Click outside closes any open dropdown
      if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown.show').forEach(d => {
          d.classList.remove('show');
          const t = d.querySelector('[data-bs-toggle="dropdown"]');
          if (t) t.setAttribute('aria-expanded', 'false');
        });
      }
    }
  });
  // Close on ESC key
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') { document.querySelectorAll('.dropdown.show').forEach(d => { d.classList.remove('show'); const t = d.querySelector('[data-bs-toggle="dropdown"]'); if (t) t.setAttribute('aria-expanded', 'false'); }); } });
})();
