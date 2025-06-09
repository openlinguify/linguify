// Variants CSS centralisés pour éviter la répétition

export const layouts = {
  // Grilles responsive
  grid: {
    default: 'grid grid-cols-1 md:grid-cols-2 gap-6',
    profile: 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8',
    dense: 'grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4',
    wide: 'grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8',
    sidebar: 'grid grid-cols-1 xl:grid-cols-5 gap-8 lg:gap-12 max-w-[1600px] mx-auto'
  },
  
  // Conteneurs
  container: {
    page: 'w-full px-6 py-8 lg:px-12',
    card: 'p-6 lg:p-8',
    section: 'space-y-8'
  }
}

export const cards = {
  // Styles de cartes
  default: 'bg-card rounded-lg shadow-sm border',
  modern: 'shadow-xl border-0 rounded-2xl overflow-hidden backdrop-blur-sm bg-white/95 dark:bg-gray-900/95',
  glass: 'backdrop-blur-sm bg-white/80 dark:bg-gray-900/80 rounded-xl border border-white/20',
  subtle: 'bg-gray-50 dark:bg-gray-800/50 rounded-xl',
  sidebar: 'bg-card rounded-xl shadow-lg border-0 overflow-hidden sticky top-8 backdrop-blur-sm bg-white/95 dark:bg-gray-900/95'
}

export const buttons = {
  // Tailles de boutons
  size: {
    sm: 'h-9 px-4',
    default: 'h-11 px-6',
    lg: 'h-12 px-8',
    nav: 'h-10 px-4'
  },
  
  // Variants de boutons
  variant: {
    primary: 'bg-primary text-primary-foreground shadow-md hover:bg-primary/90 transition-all',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-gray-100 dark:hover:bg-gray-800 transition-all',
    destructive: 'bg-red-500 text-white shadow-md hover:bg-red-600',
    nav: 'w-full justify-start text-left transition-all text-sm',
    navActive: 'bg-primary text-primary-foreground shadow-md text-sm'
  }
}

export const icons = {
  // Tailles d'icônes
  size: {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    default: 'h-5 w-5',
    lg: 'h-6 w-6',
    xl: 'h-8 w-8'
  },
  
  // Conteneurs d'icônes
  container: {
    primary: 'p-2 bg-primary/10 rounded-lg',
    secondary: 'p-1.5 bg-secondary/10 rounded-full'
  }
}

export const avatars = {
  // Tailles d'avatars
  size: {
    sm: 'h-16 w-16',
    default: 'h-24 w-24',
    lg: 'h-32 w-32',
    xl: 'h-40 w-40'
  },
  
  // Styles d'avatars
  style: {
    default: 'rounded-full overflow-hidden border-4 border-white dark:border-gray-800 shadow-lg cursor-pointer transition-all hover:scale-105 hover:shadow-xl',
    gradient: 'h-full w-full bg-gradient-to-br from-purple-500 via-blue-500 to-indigo-600 flex items-center justify-center'
  },
  
  // Tailles de texte pour fallback
  textSize: {
    sm: 'text-xl',
    default: 'text-3xl',
    lg: 'text-4xl',
    xl: 'text-5xl'
  }
}

export const headers = {
  // En-têtes de sections
  section: 'pb-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 border-b',
  title: 'flex items-center gap-3 text-2xl font-bold',
  description: 'text-gray-600 dark:text-gray-400 text-base'
}

export const fields = {
  // Champs d'informations
  container: 'p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl',
  label: 'text-sm font-semibold mb-2 flex items-center gap-2 text-gray-700 dark:text-gray-300',
  value: 'text-base text-gray-900 dark:text-white font-medium',
  empty: 'text-gray-500 italic'
}

export const animations = {
  // Animations communes
  spin: 'animate-spin',
  pulse: 'animate-pulse',
  bounce: 'animate-bounce',
  fade: 'transition-opacity duration-300',
  scale: 'transition-transform duration-200 hover:scale-105',
  shadow: 'transition-shadow duration-200 hover:shadow-lg'
}