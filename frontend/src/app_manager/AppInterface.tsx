import React from "react";
import {
  Layers,
  BookOpen,
  MessageSquare,
  Users,
  Check,
  AlertCircle,
} from "lucide-react";
import { motion } from "framer-motion";

// Types
type ModuleId = "learn" | "study" | "chat" | "coach";

interface Module {
  id: ModuleId;
  icon: React.ReactNode;
  label: string;
  isCore: boolean;
  description: string;
}

interface AppInterfaceProps {
  onModulesSelected?: (selectedModules: ModuleId[]) => void;
  defaultPremium?: boolean;
}

const AppInterface: React.FC<AppInterfaceProps> = ({
  onModulesSelected,
  defaultPremium = false,
}) => {
  const [selectedApp, setSelectedApp] = React.useState<ModuleId | null>(null);
  const [isPremium, setIsPremium] = React.useState(defaultPremium);
  const [error, setError] = React.useState<string | null>(null);

  const modules: Module[] = [
    {
      id: "learn",
      icon: <Layers size={28} />,
      label: "Learn",
      isCore: false,
      description: "Cours et leçons interactifs",
    },
    {
      id: "study",
      icon: <BookOpen size={28} />,
      label: "Study",
      isCore: false,
      description: "Révisions et exercices",
    },
    {
      id: "chat",
      icon: <MessageSquare size={28} />,
      label: "Chat",
      isCore: false,
      description: "Discussion avec des natifs",
    },
    {
      id: "coach",
      icon: <Users size={28} />,
      label: "Coach",
      isCore: false,
      description: "Cours particuliers",
    },
  ];

  const handleAppSelection = (moduleId: ModuleId) => {
    if (isPremium) return;
    setSelectedApp(selectedApp === moduleId ? null : moduleId);
    setError(null);
  };

  const togglePremium = () => {
    setIsPremium(!isPremium);
    if (!isPremium) setSelectedApp(null);
    setError(null);
  };

  const handleConfirmSelection = () => {
    if (!isPremium && !selectedApp) {
      setError("Veuillez sélectionner au moins une application");
      return;
    }

    if (onModulesSelected) {
      if (isPremium) {
        onModulesSelected(modules.map(m => m.id));
      } else if (selectedApp) {
        onModulesSelected([selectedApp]);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-50">
      {/* Header avec les plans */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl p-6 mb-8 shadow-sm"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">
            Choisissez vos applications
          </h2>
          <button
            onClick={togglePremium}
            className={`px-6 py-3 rounded-xl font-medium transition-all
              ${isPremium
                ? "bg-gray-100 text-gray-600 hover:bg-gray-200"
                : "bg-gradient-to-r from-purple-600 to-purple-700 text-white hover:from-purple-700 hover:to-purple-800"
              }`}
          >
            {isPremium ? "Plan Gratuit" : "Premium 20€/mois"}
          </button>
        </div>

        <div className="flex gap-4 flex-wrap text-sm">
          {["Toutes les applications", "Fonctionnalités avancées", "Support prioritaire"].map((feature, index) => (
            <div
              key={index}
              className={`px-4 py-2 rounded-lg ${
                isPremium
                  ? "bg-purple-100 text-purple-700"
                  : "bg-gray-100 text-gray-600"
              }`}
              role="status"
            >
              {isPremium ? `✓ ${feature}` : feature}
            </div>
          ))}
        </div>
      </motion.div>

      {error && (
        <div className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200 text-red-600 flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <p>{error}</p>
        </div>
      )}

      {/* Grille des applications */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {modules.map((module) => {
          const isAvailable = isPremium || selectedApp === module.id;
          return (
            <motion.div
              key={module.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => !module.isCore && handleAppSelection(module.id)}
              className={`
                relative group rounded-2xl p-4 transition-all duration-300 cursor-pointer
                ${isAvailable
                  ? "bg-white shadow-sm hover:shadow-md"
                  : "bg-gray-50 hover:bg-gray-100 border-2 border-dashed border-gray-200"
                }
              `}
              role="button"
              tabIndex={0}
              aria-selected={isAvailable}
              aria-label={`Select ${module.label} module`}
            >
              {selectedApp === module.id && !isPremium && (
                <div className="absolute top-2 right-2">
                  <div className="bg-purple-100 text-purple-600 text-xs px-2 py-1 rounded-full">
                    Sélectionné
                  </div>
                </div>
              )}

              <div className="flex flex-col items-center text-center gap-3">
                <motion.div
                  whileHover={{ rotate: 5 }}
                  className={`
                    w-16 h-16 rounded-xl flex items-center justify-center transition-all
                    ${isAvailable
                      ? "bg-gradient-to-br from-purple-500 to-orange-300"
                      : "bg-gray-100"
                    }
                  `}
                >
                  <div className={isAvailable ? "text-white" : "text-gray-400"}>
                    {module.icon}
                  </div>
                </motion.div>

                <div>
                  <h3
                    className={`font-medium mb-1 ${
                      isAvailable ? "text-gray-900" : "text-gray-500"
                    }`}
                  >
                    {module.label}
                  </h3>
                  <p className="text-sm text-gray-500 line-clamp-2">
                    {module.description}
                  </p>
                </div>

                <div
                  className={`
                    mt-2 text-sm px-4 py-2 rounded-lg transition-all
                    ${isAvailable
                      ? "bg-purple-50 text-purple-600"
                      : "bg-gray-50 text-gray-400"
                    }
                  `}
                >
                  {isAvailable ? "Activé" : "Sélectionner"}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Bouton de confirmation */}
      <div className="flex justify-center">
        <button
          onClick={handleConfirmSelection}
          disabled={!isPremium && !selectedApp}
          className={`
            flex items-center px-8 py-3 rounded-xl font-medium transition-all
            ${(!isPremium && !selectedApp)
              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
              : "bg-purple-600 hover:bg-purple-700 text-white"
            }
          `}
        >
          <Check className="w-5 h-5 mr-2" />
          Confirmer la sélection
        </button>
      </div>

      {/* Bottom banner for premium */}
      {!isPremium && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 bg-gradient-to-r from-purple-600 to-purple-700 rounded-2xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium mb-1">Passez Premium</h3>
              <p className="text-purple-100">
                Accédez à toutes les applications pour 20€/mois
              </p>
            </div>
            <button
              onClick={togglePremium}
              className="px-6 py-3 bg-white text-purple-600 rounded-xl font-medium hover:bg-purple-50 transition-colors"
            >
              Activer Premium
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default AppInterface;