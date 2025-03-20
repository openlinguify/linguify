// src/app/(dashboard)/(apps)/flashcard/_components/DeleteProgressDialog.tsx
import React from "react";
import { Button } from "@/components/ui/button";
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Trash2, AlertTriangle, Loader2, Check, Timer } from "lucide-react";

interface DeleteProgressDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm?: () => void;
  totalCards: number;
  progress: number;
}

/**
 * Enhanced DeleteProgressDialog Component with improved UI
 */
const DeleteProgressDialog: React.FC<DeleteProgressDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  totalCards,
  progress
}) => {
  // Determine if we're in deletion progress mode or confirmation mode
  const isDeleting = progress > 0;
  const isComplete = progress >= 100;

  // Calculate the estimated time remaining
  const getEstimatedTimeRemaining = () => {
    if (progress < 5 || progress >= 100) return null;
    
    // Simple estimate - assumes deletion rate is constant
    const percentageRemaining = 100 - progress;
    const secondsRemaining = Math.ceil(percentageRemaining / 10);
    
    if (secondsRemaining <= 0) return null;
    
    if (secondsRemaining < 60) {
      return `About ${secondsRemaining} second${secondsRemaining === 1 ? '' : 's'} remaining`;
    } else {
      const minutes = Math.floor(secondsRemaining / 60);
      const seconds = secondsRemaining % 60;
      return `About ${minutes} minute${minutes === 1 ? '' : 's'}${seconds > 0 ? ` ${seconds} seconds` : ''} remaining`;
    }
  };
  
  // Get the appropriate status message based on progress
  const getStatusMessage = () => {
    if (progress <= 0) return "Preparing to delete...";
    if (progress < 25) return "Starting deletion process...";
    if (progress < 50) return "Deleting cards...";
    if (progress < 75) return "Continuing to process cards...";
    if (progress < 100) return "Finalizing deletion...";
    return "Deletion complete!";
  };
  
  // Get progress color based on the current progress
  const getProgressColor = () => {
    if (isComplete) return "bg-green-500";
    return "bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-500";
  };

  const processedCards = Math.round((progress / 100) * totalCards);
  const estimatedTime = getEstimatedTimeRemaining();
  
  return (
    <AlertDialog open={isOpen} onOpenChange={isComplete ? onClose : undefined}>
      <AlertDialogContent className="max-w-md">
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            {isComplete ? (
              <Check className="h-5 w-5 text-green-600" />
            ) : isDeleting ? (
              <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-red-600" />
            )}
            {isComplete 
              ? "Deletion Complete" 
              : isDeleting
                ? "Deleting Flashcards"
                : "Confirm Deletion"}
          </AlertDialogTitle>
          <AlertDialogDescription className="space-y-4">
            {isDeleting ? (
              <div className="space-y-6">
                {/* Status and percentage */}
                <div className="flex justify-between items-center">
                  <p className="text-gray-700 font-medium">{getStatusMessage()}</p>
                  <div className={`px-3 py-1 rounded-full ${isComplete ? "bg-green-100" : "bg-blue-100"} transition-colors duration-500`}>
                    <span className={`font-bold ${isComplete ? "text-green-600" : "text-blue-600"}`}>
                      {progress}%
                    </span>
                  </div>
                </div>
                
                {/* Custom progress bar with gradient background */}
                <div className="relative h-4 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className={`absolute top-0 left-0 h-full transition-all duration-300 ${getProgressColor()}`}
                    style={{ width: `${progress}%` }}
                  />
                </div>
                
                {/* Card counter with visual indicator */}
                <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600 font-medium">Progress</span>
                    <span className="text-gray-800 font-bold">{processedCards}/{totalCards}</span>
                  </div>
                  <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="absolute top-0 left-0 h-full bg-blue-400"
                      style={{ width: `${(processedCards / totalCards) * 100}%` }}
                    />
                  </div>
                </div>
                
                {/* Estimated time remaining */}
                {estimatedTime && !isComplete && (
                  <div className="flex items-center justify-center text-sm text-gray-500 bg-gray-50 p-2 rounded-lg">
                    <Timer className="h-4 w-4 mr-2" />
                    <span>{estimatedTime}</span>
                  </div>
                )}
                
                {/* Success message */}
                {isComplete && (
                  <div className="bg-green-50 border border-green-100 rounded-lg p-4 flex flex-col items-center justify-center text-green-600 transition-all duration-500 animate-fadeIn">
                    <div className="bg-green-100 p-3 rounded-full mb-3">
                      <Check className="h-6 w-6" />
                    </div>
                    <p className="font-medium text-center">
                      Successfully deleted {totalCards} cards!
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                  <p className="mb-2 text-gray-700">
                    Are you sure you want to delete <strong>{totalCards}</strong> flashcards?
                  </p>
                  <p className="text-red-600 font-medium flex items-center">
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    This action cannot be undone.
                  </p>
                </div>
                
                <div className="bg-amber-50 p-3 rounded-lg border border-amber-100">
                  <p className="text-amber-700 text-sm">
                    All progress data associated with these flashcards will be permanently removed.
                  </p>
                </div>
              </div>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        {!isDeleting && onConfirm && (
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.preventDefault();
                onConfirm();
              }}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete {totalCards} flashcards
            </AlertDialogAction>
          </AlertDialogFooter>
        )}
        
        {isComplete && (
          <AlertDialogFooter>
            <Button onClick={onClose} className="w-full bg-green-600 hover:bg-green-700 text-white">
              <Check className="h-4 w-4 mr-2" />
              Done
            </Button>
          </AlertDialogFooter>
        )}
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default DeleteProgressDialog;