// src/styles/gradient_style.ts
export const commonStyles = {
  gradientCard: "bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 backdrop-blur-sm shadow-xl",
  gradientText: "bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent",
  gradientButton: "bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90",
  contentBox: "relative overflow-hidden rounded-xl mb-8",
  gradientBackground: "absolute inset-0 bg-gradient-to-br from-brand-purple/10 to-brand-gold/10",
  container: "max-w-4xl mx-auto p-6",
  cardPadding: "p-8",
  exampleBox: "rounded-lg border border-brand-purple/20 bg-gradient-to-br from-brand-purple/5 to-transparent p-6 mb-8",
  tabsList: "grid w-full grid-cols-3 bg-gray-100/50 dark:bg-gray-800/50 p-1 rounded-lg",
  tabsTrigger: "data-[state=active]:bg-gradient-to-r data-[state=active]:from-brand-purple data-[state=active]:to-brand-gold data-[state=active]:text-white",
  tabsContent: "mt-6 bg-gray-50/50 dark:bg-gray-800/50 rounded-lg p-6"
} as const;