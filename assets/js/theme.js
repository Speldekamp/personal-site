/* Dark | Light switch (layouts/partials/theme_toggle.html).
   The site is dark by default; a click is remembered in localStorage "pref-theme".
   The saved choice is applied before first paint by the inline script in baseof.html. */
(function () {
    var groups = document.querySelectorAll('.theme-toggle');
    if (!groups.length) return;

    function save(mode) {
        try { localStorage.setItem('pref-theme', mode); } catch (e) { /* storage blocked: choice lasts for this page only */ }
    }

    function sync() {
        var mode = document.body.classList.contains('dark') ? 'dark' : 'light';
        groups.forEach(function (g) {
            g.querySelectorAll('button').forEach(function (b) {
                b.setAttribute('aria-pressed', b.dataset.theme === mode ? 'true' : 'false');
            });
        });
    }

    groups.forEach(function (g) {
        g.hidden = false;
        g.addEventListener('click', function (e) {
            var b = e.target.closest('button[data-theme]');
            if (!b) return;
            document.body.classList.toggle('dark', b.dataset.theme === 'dark');
            save(b.dataset.theme);
            sync();
        });
    });
    sync();
})();
