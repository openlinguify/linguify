import React from 'react'
import { cn } from '@/lib/utils'

// Grilles responsive standardisées
export const ResponsiveGrid = ({ 
  children, 
  className, 
  variant = 'default',
  ...props 
}: {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'profile' | 'dense' | 'wide'
} & React.HTMLAttributes<HTMLDivElement>) => {
  const variants = {
    default: 'grid grid-cols-1 md:grid-cols-2 gap-6',
    profile: 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8',
    dense: 'grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4',
    wide: 'grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8'
  }
  
  return (
    <div className={cn(variants[variant], className)} {...props}>
      {children}
    </div>
  )
}

// Cartes modernisées
export const ModernCard = ({ 
  children, 
  className, 
  variant = 'default',
  ...props 
}: {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'elevated' | 'glass' | 'subtle'
} & React.HTMLAttributes<HTMLDivElement>) => {
  const variants = {
    default: 'bg-card rounded-lg shadow-sm border',
    elevated: 'shadow-xl border-0 rounded-2xl overflow-hidden backdrop-blur-sm bg-white/95 dark:bg-gray-900/95',
    glass: 'backdrop-blur-sm bg-white/80 dark:bg-gray-900/80 rounded-xl border border-white/20',
    subtle: 'bg-gray-50 dark:bg-gray-800/50 rounded-xl border-0'
  }
  
  return (
    <div className={cn(variants[variant], className)} {...props}>
      {children}
    </div>
  )
}

// Boutons d'icônes standardisés
export const IconButton = ({ 
  icon: Icon, 
  children, 
  className, 
  size = 'default',
  variant = 'default',
  ...props 
}: {
  icon?: React.ComponentType<{ className?: string }>
  children?: React.ReactNode
  className?: string
  size?: 'sm' | 'default' | 'lg'
  variant?: 'default' | 'primary' | 'ghost' | 'destructive'
} & React.ButtonHTMLAttributes<HTMLButtonElement>) => {
  const sizes = {
    sm: 'h-9 px-4',
    default: 'h-11 px-6',
    lg: 'h-12 px-8'
  }
  
  const iconSizes = {
    sm: 'h-4 w-4',
    default: 'h-5 w-5',
    lg: 'h-6 w-6'
  }
  
  const variants = {
    default: 'bg-primary text-primary-foreground shadow-md hover:bg-primary/90',
    primary: 'bg-primary text-primary-foreground shadow-md hover:bg-primary/90',
    ghost: 'hover:bg-gray-100 dark:hover:bg-gray-800',
    destructive: 'bg-red-500 text-white shadow-md hover:bg-red-600'
  }
  
  return (
    <button 
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-medium transition-all',
        sizes[size],
        variants[variant],
        className
      )} 
      {...props}
    >
      {Icon && <Icon className={cn(iconSizes[size], children && 'mr-2')} />}
      {children}
    </button>
  )
}

// Headers de sections uniformisés
export const SectionHeader = ({ 
  icon: Icon, 
  title, 
  description, 
  className,
  ...props 
}: {
  icon?: React.ComponentType<{ className?: string }>
  title: string
  description?: string
  className?: string
} & React.HTMLAttributes<HTMLDivElement>) => {
  return (
    <div className={cn('pb-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 border-b', className)} {...props}>
      <div className="flex items-center gap-3 text-2xl font-bold mb-2">
        {Icon && (
          <div className="p-2 bg-primary/10 rounded-lg">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        )}
        {title}
      </div>
      {description && (
        <p className="text-gray-600 dark:text-gray-400 text-base">
          {description}
        </p>
      )}
    </div>
  )
}

// Champs d'informations uniformisés
export const InfoField = ({ 
  icon: Icon, 
  label, 
  value, 
  className,
  ...props 
}: {
  icon?: React.ComponentType<{ className?: string }>
  label: string
  value: string | React.ReactNode
  className?: string
} & React.HTMLAttributes<HTMLDivElement>) => {
  return (
    <div className={cn('p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl', className)} {...props}>
      <h3 className="text-sm font-semibold mb-2 flex items-center gap-2 text-gray-700 dark:text-gray-300">
        {Icon && <Icon className="h-4 w-4 text-primary" />}
        {label}
      </h3>
      <div className="text-base text-gray-900 dark:text-white font-medium">
        {value || <span className="text-gray-500 italic">Non renseigné</span>}
      </div>
    </div>
  )
}

// Avatar moderne
export const ModernAvatar = ({ 
  src, 
  alt, 
  fallback, 
  size = 'default',
  className,
  onClick,
  isLoading = false,
  ...props 
}: {
  src?: string
  alt?: string
  fallback?: string
  size?: 'sm' | 'default' | 'lg' | 'xl'
  className?: string
  onClick?: () => void
  isLoading?: boolean
} & React.HTMLAttributes<HTMLDivElement>) => {
  const sizes = {
    sm: 'h-16 w-16',
    default: 'h-24 w-24',
    lg: 'h-32 w-32',
    xl: 'h-40 w-40'
  }
  
  const textSizes = {
    sm: 'text-xl',
    default: 'text-3xl',
    lg: 'text-4xl',
    xl: 'text-5xl'
  }
  
  return (
    <div className="relative">
      <div
        className={cn(
          'rounded-full overflow-hidden border-4 border-white dark:border-gray-800 shadow-lg transition-all',
          onClick && 'cursor-pointer hover:scale-105 hover:shadow-xl',
          sizes[size],
          className
        )}
        onClick={onClick}
        {...props}
      >
        {src ? (
          <img
            src={src}
            alt={alt}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-br from-purple-500 via-blue-500 to-indigo-600 flex items-center justify-center">
            <span className={cn('font-bold text-white drop-shadow-sm', textSizes[size])}>
              {fallback?.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
      </div>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded-full backdrop-blur-sm">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white" />
        </div>
      )}
    </div>
  )
}