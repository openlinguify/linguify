/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Django templates - Global coverage for all apps
    "./backend/templates/**/*.html",
    "./backend/saas_web/templates/**/*.html",
    "./backend/core/templates/**/*.html",
    
    // All Django apps templates and static files
    "./backend/apps/*/templates/**/*.html",
    "./backend/apps/*/static/**/*.js",
    "./backend/apps/*/static/**/*.html",
    
    // Global static files
    "./backend/static/**/*.js",
    "./backend/static/**/*.html",
    "./backend/staticfiles/**/*.js",
    "./backend/staticfiles/**/*.html",
  ],
  theme: {
    extend: {
      // Match existing CSS variables from base.html
      colors: {
        'linguify': {
          'primary': '#2D5BBA',
          'primary-dark': '#1E3A8A', 
          'secondary': '#8B5CF6',
          'accent': '#00D4AA',
          'success': '#10b981',
          'warning': '#f59e0b',
          'danger': '#ef4444',
          'gray': {
            50: '#f8fafc',
            100: '#f1f5f9',
            200: '#e2e8f0',
            300: '#cbd5e1',
            400: '#94a3b8',
            500: '#64748b',
            600: '#475569',
            700: '#334155',
            800: '#1e293b',
            900: '#0f172a',
          }
        }
      },
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 4px 16px rgba(0,0,0,0.1)',
        'card-hover': '0 20px 40px rgba(0,0,0,0.1)',
      },
      borderRadius: {
        'card': '16px',
        'form': '12px',
      },
      animation: {
        'flip': 'flip 0.6s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-in',
        'bounce-subtle': 'bounceSubtle 0.5s ease-in-out',
      },
      keyframes: {
        flip: {
          '0%': { transform: 'rotateY(0deg)' },
          '50%': { transform: 'rotateY(90deg)' },
          '100%': { transform: 'rotateY(0deg)' },
        },
        slideIn: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        }
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
  // Ensure compatibility with existing Bootstrap classes
  corePlugins: {
    preflight: false, // Disable Tailwind's CSS reset to avoid conflicts with Bootstrap
  }
}