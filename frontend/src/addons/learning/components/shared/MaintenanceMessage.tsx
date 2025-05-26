'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface MaintenanceMessageProps {
  /** The title of the content that is under maintenance */
  contentTitle?: string;
  /** The type of content (e.g., "leçon", "exercice", "test") */
  contentType?: string;
  /** Custom message to display instead of the default */
  customMessage?: string;
  /** Custom back button text */
  backButtonText?: string;
  /** Custom back button action */
  onBack?: () => void;
  /** Additional CSS classes */
  className?: string;
}

const MaintenanceMessage: React.FC<MaintenanceMessageProps> = ({
  contentTitle,
  contentType = "contenu",
  customMessage,
  backButtonText = "Retour",
  onBack,
  className = ""
}) => {
  const router = useRouter();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      router.back();
    }
  };

  const getDefaultMessage = () => {
    if (customMessage) return customMessage;
    
    const title = contentTitle ? ` "${contentTitle}"` : '';
    return `Ce ${contentType}${title} est temporairement indisponible. Notre équipe travaille pour le rendre disponible prochainement.`;
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center ${className}`}>
      <Card className="p-8 max-w-lg">
        <CardContent className="text-center">
          <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-orange-600" />
          </div>
          
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            {contentType === "session de révision" ? "Session de révision en maintenance" : "Contenu en maintenance"}
          </h2>
          
          <p className="text-gray-600 mb-6">
            {getDefaultMessage()}
          </p>
          
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-orange-800">
              <strong>En attendant :</strong> Vous pouvez continuer avec les autres leçons ou réviser 
              d'autres contenus en retournant à la vue précédente.
            </p>
          </div>
          
          <Button onClick={handleBack}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            {backButtonText}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default MaintenanceMessage;