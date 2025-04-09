export const gradientStyles = {
  // Styles de conteneurs avec dégradés
  card: "bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 backdrop-blur-sm shadow-xl",
  
  // Styles de texte avec dégradé
  text: "bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent",
  
  // Styles de boutons avec dégradé
  button: "bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90",
  
  // Conteneurs avec effets supplémentaires
  container: "relative overflow-hidden rounded-xl mb-8",
  background: "absolute inset-0 bg-gradient-to-br from-brand-purple/10 to-brand-gold/10",
  
  // Styles pour composants spécifiques
  tabs: {
    list: "grid w-full grid-cols-3 bg-gray-100/50 dark:bg-gray-800/50 p-1 rounded-lg",
    trigger: "data-[state=active]:bg-gradient-to-r data-[state=active]:from-brand-purple data-[state=active]:to-brand-gold data-[state=active]:text-white"
  }
} as const;

// Fonction utilitaire pour générer des classes dynamiques
export function generateGradientClass(
  from: string = 'from-brand-purple', 
  to: string = 'to-brand-gold'
) {
  return `bg-gradient-to-r ${from} ${to}`;
}