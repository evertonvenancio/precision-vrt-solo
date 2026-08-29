function appData() {
            return {
                isDark: false,
                sidebarOpen: true,

                initApp() {
                    this.isDark = window.vrtTheme.isDark;
                    this.sidebarOpen = localStorage.getItem('sidebarOpen') !== 'false';
                },

                toggleTheme() {
                    window.vrtTheme.toggle();
                    this.isDark = window.vrtTheme.isDark;
                }
            }
        }
