<!-- Sistema de temas global -->
<script>
// Global theme system
window.vrtTheme = {
    isDark: false,
    
    init() {
        // Load theme from localStorage
        const savedTheme = localStorage.getItem('theme');
        this.isDark = savedTheme === 'dark';
        this.apply();
    },
    
    toggle() {
        this.isDark = !this.isDark;
        localStorage.setItem('theme', this.isDark ? 'dark' : 'light');
        this.apply();
    },
    
    apply() {
        if (this.isDark) {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        } else {
            document.documentElement.classList.add('light');
            document.documentElement.classList.remove('dark');
        }
    }
};

// Initialize theme on load
document.addEventListener('DOMContentLoaded', () => {
    vrtTheme.init();
});
</script>