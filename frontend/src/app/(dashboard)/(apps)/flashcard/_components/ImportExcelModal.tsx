// src/app/(dashboard)/(apps)/flashcard/_components/ImportExcelModal.tsx

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, HelpCircle, Upload, FileSpreadsheet } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { revisionApi } from "@/services/revisionAPI";

interface ImportExcelModalProps {
  deckId: number;
  isOpen: boolean;
  onClose: () => void;
  onImportSuccess: () => void;
}

export default function ImportExcelModal({
  deckId,
  isOpen,
  onClose,
  onImportSuccess,
}: ImportExcelModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    
    if (file) {
      // Vérifier le format du fichier
      if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
        toast({
          title: "Invalid format",
          description: "Please select an Excel (.xlsx, .xls) or CSV (.csv) file",
          variant: "destructive",
        });
        return;
      }
      
      setSelectedFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      toast({
        title: "Error",
        description: "Please select a file",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsUploading(true);
      
      // Simuler une progression
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);

      // Importer le fichier
      const result = await revisionApi.flashcards.importFromExcel(deckId, selectedFile);

      // Progression terminée
      clearInterval(progressInterval);
      setProgress(100);

      toast({
        title: "Import successful",
        description: `${result.created} flashcards have been imported successfully.${result.failed > 0 ? ` ${result.failed} imports failed.` : ''}`,
      });

      // Notifier le composant parent pour rafraîchir les données
      onImportSuccess();
      
      // Fermer le modal après un court délai
      setTimeout(() => {
        onClose();
        setSelectedFile(null);
        setProgress(0);
      }, 1500);
      
    } catch (error: any) {
      const errorMessage = error.data?.detail || "An error occurred during import";
      
      toast({
        title: "Import error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-[90%] max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Import flashcards</span>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <HelpCircle className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p>The file must contain at least 2 columns. The first column will be used for the front and the second for the back of the cards.</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardTitle>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center">
              {selectedFile ? (
                <div className="flex flex-col items-center">
                  <FileSpreadsheet className="h-10 w-10 text-green-600 mb-2" />
                  <p className="text-sm text-green-600 font-medium">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="sm" 
                    className="mt-2"
                    onClick={() => setSelectedFile(null)}
                    disabled={isUploading}
                  >
                    Change file
                  </Button>
                </div>
              ) : (
                <>
                  <Upload className="h-10 w-10 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-500 text-center mb-4">
                    Drop your Excel or CSV file here
                  </p>
                  <label htmlFor="excel-upload" className="cursor-pointer">
                    <span className="bg-gradient-to-r from-brand-purple to-brand-gold text-white py-2 px-4 rounded-md">
                      Browse
                    </span>
                    <input
                      id="excel-upload"
                      type="file"
                      accept=".xlsx,.xls,.csv"
                      className="hidden"
                      onChange={handleFileChange}
                      disabled={isUploading}
                    />
                  </label>
                </>
              )}
            </div>

            {isUploading && (
              <div className="space-y-2">
                <Progress value={progress} className="h-2" />
                <p className="text-sm text-gray-500 text-center">
                  {progress === 100 ? 'Import completed!' : 'Importing...'}
                </p>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-end space-x-2">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onClose}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              disabled={isUploading || !selectedFile}
              className="bg-gradient-to-r from-brand-purple to-brand-gold"
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Importing...
                </>
              ) : 'Import'}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}