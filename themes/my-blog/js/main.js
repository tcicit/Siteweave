document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.sidebar-nav');
    if (!sidebar) return;

    const items = sidebar.querySelectorAll('li');
    items.forEach(item => {
        const subMenu = item.querySelector('ul, .dropdown-content');
        if (subMenu) {
            item.classList.add('has-submenu');

            // Toggle-Button nur erstellen, wenn noch keiner existiert
            if (item.querySelector('.menu-toggle')) return;
            
            const toggle = document.createElement('span');
            toggle.className = 'menu-toggle';
            toggle.innerHTML = '❯'; 
            item.insertBefore(toggle, item.firstChild);

            // Klick-Event für den Pfeil
            toggle.addEventListener('click', function (e) {
                e.stopPropagation();
                item.classList.toggle('is-open');
            });
            
            // Optional: Klick auf den Ordner-Button/Link soll auch öffnen, 
            // wenn es ein Ordner ist (kein direkter Link zu einer Seite)
            const link = item.querySelector('a, .dropbtn');
            if (link && (link.getAttribute('href') === '#' || !link.getAttribute('href'))) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    item.classList.toggle('is-open');
                });
            }

            // Automatisch öffnen, wenn die Seite oder ein Kind aktiv ist
            if (item.querySelector('.active') || item.classList.contains('active') || item.classList.contains('active-parent')) {
                item.classList.add('is-open');
            }
        }
    });
});