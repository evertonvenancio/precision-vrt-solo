(function() {
    var html = document.documentElement;
    var STORAGE_KEY = 'vrt-theme';

    function getTheme() {
        return localStorage.getItem(STORAGE_KEY) || 'light';
    }

    function setTheme(theme) {
        localStorage.setItem(STORAGE_KEY, theme);
        if (theme === 'dark') {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }
        window.dispatchEvent(new CustomEvent('vrt-theme-changed', { detail: { theme: theme } }));
    }

    function toggle() {
        setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    }

    window.vrtTheme = {
        getTheme: getTheme,
        setTheme: setTheme,
        toggle: toggle,
        get isDark() { return getTheme() === 'dark'; }
    };

    setTheme(getTheme());
})();