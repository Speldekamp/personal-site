/* Dark | Light switch (layouts/partials/theme_toggle.html).
   Before first paint the inline script in baseof.html applies the visitor's saved choice
   (localStorage "pref-theme"), else the system setting. This file wires up the buttons,
   keeps following the system setting until the visitor clicks one, and sets the
   browser bar colour (meta theme-color) to match the page. */
(function () {
    var KEY = 'pref-theme';
    var groups = document.querySelectorAll('.theme-toggle');
    var meta = document.getElementById('theme-color');

    function saved() {
        try { var t = localStorage.getItem(KEY); return (t === 'light' || t === 'dark') ? t : null; } catch (e) { return null; }
    }
    function save(t) {
        try { localStorage.setItem(KEY, t); } catch (e) { /* storage blocked: choice lasts for this page only */ }
    }
    function current() { return document.body.classList.contains('dark') ? 'dark' : 'light'; }

    function sync() {
        var t = current();
        if (meta) meta.setAttribute('content', t === 'dark' ? '#1b1c20' : '#f4f2ec');
        groups.forEach(function (g) {
            g.querySelectorAll('button').forEach(function (b) {
                b.setAttribute('aria-pressed', b.dataset.theme === t ? 'true' : 'false');
            });
        });
    }
    function apply(t) {
        document.body.classList.toggle('dark', t === 'dark');
        sync();
    }

    groups.forEach(function (g) {
        g.hidden = false;
        g.addEventListener('click', function (e) {
            var b = e.target.closest('button[data-theme]');
            if (!b) return;
            save(b.dataset.theme);
            apply(b.dataset.theme);
        });
    });

    /* Until the visitor picks one, follow changes to the system setting. */
    if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: light)');
        var follow = function (e) { if (!saved()) apply(e.matches ? 'light' : 'dark'); };
        if (mq.addEventListener) mq.addEventListener('change', follow);
        else if (mq.addListener) mq.addListener(follow);
    }
    sync();
})();
