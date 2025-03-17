// src/app/(dashboard)/(apps)/flashcard/_components/ImportExcelModal.tsx

import React, { useState, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, HelpCircle, Upload, FileSpreadsheet, Check, X, DownloadIcon, ArrowLeftIcon, ArrowRight, ArrowRightIcon } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
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

interface PreviewData {
  front_text: string;
  back_text: string;
  [key: string]: any;
}

interface ColumnMapping {
  frontColumn: string;
  backColumn: string;
}

export default function ImportExcelModal({
  deckId,
  isOpen,
  onClose,
  onImportSuccess,
}: ImportExcelModalProps) {
  // États
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [hasHeader, setHasHeader] = useState(true);
  const [step, setStep] = useState<'upload' | 'map' | 'preview' | 'import'>('upload');
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [totalRows, setTotalRows] = useState(0);
  const [columns, setColumns] = useState<string[]>([]);
  const [columnMapping, setColumnMapping] = useState<ColumnMapping>({ frontColumn: '', backColumn: '' });
  const [fileType, setFileType] = useState<'xlsx' | 'csv' | 'unknown'>('unknown');
  const [invalidRows, setInvalidRows] = useState<number[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // Gestionnaires
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    
    if (file) {
      // Déterminer le type de fichier
      let type: 'xlsx' | 'csv' | 'unknown' = 'unknown';
      if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        type = 'xlsx';
      } else if (file.name.endsWith('.csv')) {
        type = 'csv';
      } else {
        toast({
          title: "Format invalide",
          description: "Veuillez sélectionner un fichier Excel (.xlsx, .xls) ou CSV (.csv)",
          variant: "destructive",
        });
        return;
      }
      
      setSelectedFile(file);
      setFileType(type);
      setStep('upload');
      resetState();
    }
  };

  const analyzeFile = async () => {
    if (!selectedFile) return;
    
    try {
      setIsUploading(true);
      setProgress(30);
      
      // Créer un FormData pour l'upload avec l'option preview_only
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('has_header', hasHeader.toString());
      formData.append('preview_only', 'true');
      
      const result = await revisionApi.flashcards.importFromExcel(deckId, selectedFile, {
        hasHeader,
        previewOnly: true
      });
      
      setProgress(100);
      
      // Extract columns from the preview data if available
      const extractedColumns = result.preview && result.preview.length > 0 ? 
        Object.keys(result.preview[0]) : [];
      
      if (extractedColumns.length > 0) {
        setColumns(extractedColumns);
        
        // Définir les mappages par défaut pour les deux premières colonnes
        setColumnMapping({
          frontColumn: extractedColumns[0] || '',
          backColumn: extractedColumns.length > 1 ? extractedColumns[1] : '',
        });
        
        setPreviewData(result.preview || []);
        setTotalRows(result.preview?.length || 0);
        
        // Passer à l'étape de mappage si nécessaire
        setStep('map');
      } else {
        toast({
          title: "Fichier invalide",
          description: "Aucune colonne n'a été détectée dans le fichier",
          variant: "destructive",
        });
      }
      
    } catch (error: any) {
      toast({
        title: "Erreur d'analyse",
        description: error.message || "Une erreur est survenue lors de l'analyse du fichier",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      setProgress(0);
    }
  };

  const generatePreview = () => {
    if (previewData.length === 0) return;
    
    // Valider les données avec le mappage sélectionné
    const invalid: number[] = [];
    
    // Créer des données transformées avec le mappage
    const transformedData = previewData.map((row, index) => {
      const frontText = row[columnMapping.frontColumn]?.toString().trim() || '';
      const backText = row[columnMapping.backColumn]?.toString().trim() || '';
      
      if (!frontText || !backText) {
        invalid.push(index);
      }
      
      return {
        front_text: frontText,
        back_text: backText,
      };
    });
    
    setPreviewData(transformedData);
    setInvalidRows(invalid);
    setStep('preview');
  };

  const handleImport = async () => {
    if (!selectedFile) return;
    
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

      // Préparer les données pour l'importation
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('has_header', hasHeader.toString());
      formData.append('front_column', columnMapping.frontColumn);
      formData.append('back_column', columnMapping.backColumn);
      
      // Make sure the API accepts these parameters
      const result = await revisionApi.flashcards.importFromExcel(deckId, selectedFile, {
        hasHeader,
        previewOnly: false,
        frontColumn: columnMapping.frontColumn,
        backColumn: columnMapping.backColumn
      } as any); // Use type assertion as a temporary solution
      
      clearInterval(progressInterval);
      setProgress(100);
      
      toast({
        title: "Importation réussie",
        description: `${result.created} cartes ont été importées avec succès.${result.failed > 0 ? ` ${result.failed} imports ont échoué.` : ''}`,
      });

      // Notifier le composant parent pour rafraîchir les données
      onImportSuccess();
      
      // Mettre à jour l'étape
      setStep('import');
      
      // Fermer le modal après un court délai
      setTimeout(() => {
        onClose();
        resetState();
      }, 2000);
      
    } catch (error: any) {
      toast({
        title: "Erreur d'importation",
        description: error.message || "Une erreur est survenue lors de l'importation",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const resetState = () => {
    setPreviewData([]);
    setColumns([]);
    setColumnMapping({ frontColumn: '', backColumn: '' });
    setTotalRows(0);
    setInvalidRows([]);
  };

  const resetForm = () => {
    setSelectedFile(null);
    setStep('upload');
    resetState();
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center space-x-2">
        <Badge variant={step === 'upload' ? "default" : "outline"} className="px-3 py-1">
          1. Fichier
        </Badge>
        <ArrowRightIcon size={12} className="text-gray-400" />
        <Badge variant={step === 'map' ? "default" : "outline"} className="px-3 py-1">
          2. Mappage
        </Badge>
        <ArrowRightIcon size={12} className="text-gray-400" />
        <Badge variant={step === 'preview' ? "default" : "outline"} className="px-3 py-1">
          3. Aperçu
        </Badge>
        <ArrowRightIcon size={12} className="text-gray-400" />
        <Badge variant={step === 'import' ? "default" : "outline"} className="px-3 py-1">
          4. Importation
        </Badge>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto py-8">
      <Card className="w-[95%] max-w-4xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{getStepTitle()}</CardTitle>
              <CardDescription>
                {step === 'upload' && "Sélectionnez un fichier Excel ou CSV contenant vos flashcards"}
                {step === 'map' && "Définissez quelles colonnes utiliser pour le recto et le verso des cartes"}
                {step === 'preview' && "Vérifiez les données avant l'importation finale"}
                {step === 'import' && "Importation terminée!"}
              </CardDescription>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <HelpCircle className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p>Le fichier doit contenir au moins 2 colonnes. Vous pourrez indiquer quelle colonne utiliser pour le recto et le verso des cartes.</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          {renderStepIndicator()}
        </CardHeader>
        <CardContent>
          {step === 'upload' && (
            <div className="space-y-6">
              <div className="border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center">
                {selectedFile ? (
                  <div className="flex flex-col items-center">
                    <FileSpreadsheet className="h-16 w-16 text-green-600 mb-3" />
                    <p className="text-lg text-green-600 font-medium">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                    <div className="flex mt-4 space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setSelectedFile(null)}
                        disabled={isUploading}
                      >
                        Changer de fichier
                      </Button>
                      <Button 
                        variant="default"
                        size="sm"
                        disabled={isUploading}
                        onClick={analyzeFile}
                      >
                        {isUploading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Analyse...
                          </>
                        ) : (
                          <>
                            Analyser le fichier
                            <ArrowRight className="ml-2 h-4 w-4" />
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center">
                    <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">Déposez votre fichier ici ou</h3>
                    <Button 
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-gradient-to-r from-brand-purple to-brand-gold"
                    >
                      Sélectionner un fichier
                    </Button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".xlsx,.xls,.csv"
                      className="hidden"
                      onChange={handleFileChange}
                      disabled={isUploading}
                    />
                    <p className="text-sm text-gray-500 mt-4">
                      Formats supportés: Excel (.xlsx, .xls) ou CSV (.csv)
                    </p>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-2 p-4 bg-gray-50 rounded-lg">
                <Checkbox 
                  id="has-header"
                  checked={hasHeader}
                  onCheckedChange={(checked) => setHasHeader(checked as boolean)}
                />
                <div>
                  <Label htmlFor="has-header" className="font-medium">
                    La première ligne contient les en-têtes de colonnes
                  </Label>
                  <p className="text-sm text-gray-500">
                    Cochez cette case si votre fichier contient une ligne d'en-têtes (qui ne sera pas importée)
                  </p>
                </div>
              </div>
            </div>
          )}

          {step === 'map' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="front-column" className="text-base font-medium mb-2 block">
                    Colonne pour le recto (front)
                  </Label>
                  <Select 
                    value={columnMapping.frontColumn} 
                    onValueChange={(value) => setColumnMapping({...columnMapping, frontColumn: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner une colonne" />
                    </SelectTrigger>
                    <SelectContent>
                      {columns.map((col) => (
                        <SelectItem key={col} value={col}>{col}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-gray-500 mt-1">
                    Cette colonne sera utilisée pour le recto des cartes (question)
                  </p>
                </div>
                <div>
                  <Label htmlFor="back-column" className="text-base font-medium mb-2 block">
                    Colonne pour le verso (back)
                  </Label>
                  <Select 
                    value={columnMapping.backColumn} 
                    onValueChange={(value) => setColumnMapping({...columnMapping, backColumn: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner une colonne" />
                    </SelectTrigger>
                    <SelectContent>
                      {columns.map((col) => (
                        <SelectItem key={col} value={col}>{col}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-gray-500 mt-1">
                    Cette colonne sera utilisée pour le verso des cartes (réponse)
                  </p>
                </div>
              </div>

              <div className="border rounded-md overflow-auto max-h-64">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      {columns.map((col) => (
                        <TableHead key={col}>
                          {col}
                          {col === columnMapping.frontColumn && (
                            <Badge variant="outline" className="ml-2 bg-blue-50">Recto</Badge>
                          )}
                          {col === columnMapping.backColumn && (
                            <Badge variant="outline" className="ml-2 bg-green-50">Verso</Badge>
                          )}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {previewData.slice(0, 5).map((row, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{index + 1}</TableCell>
                        {columns.map((col) => (
                          <TableCell key={col} className={`${
                            col === columnMapping.frontColumn ? 'bg-blue-50' : 
                            col === columnMapping.backColumn ? 'bg-green-50' : ''
                          }`}>
                            {String(row[col] || '')}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium flex items-center">
                  <HelpCircle className="h-4 w-4 mr-2" />
                  Comment fonctionne le mappage?
                </h4>
                <p className="text-sm mt-1">
                  Sélectionnez quelles colonnes de votre fichier contiennent le recto et le verso des cartes. 
                  Assurez-vous de bien vérifier les données avec l'aperçu ci-dessus.
                </p>
              </div>
            </div>
          )}

          {step === 'preview' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Aperçu des données à importer</h3>
                <div className="text-sm text-gray-500">
                  {totalRows} lignes détectées{hasHeader ? " (sans compter l'en-tête)" : ""}
                </div>
              </div>
              
              <div className="border rounded-md overflow-auto max-h-80">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Recto (Front)</TableHead>
                      <TableHead>Verso (Back)</TableHead>
                      <TableHead className="w-16">Statut</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {previewData.map((row, index) => (
                      <TableRow key={index} className={invalidRows.includes(index) ? "bg-red-50" : ""}>
                        <TableCell>{index + 1}</TableCell>
                        <TableCell className="font-medium">{row.front_text}</TableCell>
                        <TableCell>{row.back_text}</TableCell>
                        <TableCell>
                          {invalidRows.includes(index) ? (
                            <Badge variant="destructive" className="flex items-center">
                              <X className="h-3 w-3 mr-1" />
                              Invalide
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="bg-green-50 flex items-center">
                              <Check className="h-3 w-3 mr-1" />
                              Valide
                            </Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              {invalidRows.length > 0 && (
                <div className="bg-red-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-red-600 flex items-center">
                    <X className="h-4 w-4 mr-2" />
                    {invalidRows.length} lignes invalides détectées
                  </h4>
                  <p className="text-sm mt-1">
                    Ces lignes ne seront pas importées car elles ne contiennent pas de données valides pour le recto ou le verso.
                  </p>
                </div>
              )}
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-green-600 flex items-center">
                  <Check className="h-4 w-4 mr-2" />
                  {previewData.length - invalidRows.length} cartes prêtes à être importées
                </h4>
                <p className="text-sm mt-1">
                  Ces cartes seront ajoutées à votre deck. Cliquez sur "Importer" pour confirmer.
                </p>
              </div>
            </div>
          )}

          {step === 'import' && (
            <div className="text-center space-y-6 py-8">
              <div className="mx-auto bg-green-100 rounded-full p-6 w-24 h-24 flex items-center justify-center">
                <Check className="h-12 w-12 text-green-600" />
              </div>
              <h3 className="text-xl font-medium">Importation terminée avec succès!</h3>
              <p className="text-gray-600">
                Vos cartes ont été ajoutées à votre deck et sont prêtes à être utilisées.
              </p>
            </div>
          )}

          {isUploading && (
            <div className="space-y-2 mt-4">
              <Progress value={progress} className="h-2" />
              <p className="text-sm text-gray-500 text-center">
                {progress === 100 ? 'Terminé !' : getProgressLabel()}
              </p>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between">
          <div>
            {step !== 'upload' && step !== 'import' && (
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setStep(step === 'preview' ? 'map' : 'upload')}
                disabled={isUploading}
              >
                <ArrowLeftIcon className="h-4 w-4 mr-2" />
                Retour
              </Button>
            )}
          </div>
          <div className="flex space-x-2">
            <Button 
              type="button" 
              variant="outline" 
              onClick={step === 'import' ? onClose : resetForm}
              disabled={isUploading}
            >
              {step === 'import' ? 'Fermer' : 'Annuler'}
            </Button>
            
            {step === 'upload' && selectedFile && (
              <Button 
                onClick={analyzeFile}
                disabled={isUploading || !selectedFile}
                className="bg-gradient-to-r from-brand-purple to-brand-gold"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyse...
                  </>
                ) : (
                  <>
                    Continuer
                    <ArrowRightIcon className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            )}
            
            {step === 'map' && (
              <Button 
                onClick={generatePreview}
                disabled={isUploading || !columnMapping.frontColumn || !columnMapping.backColumn}
                className="bg-gradient-to-r from-brand-purple to-brand-gold"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Génération...
                  </>
                ) : (
                  <>
                    Voir l'aperçu
                    <ArrowRightIcon className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            )}
            
            {step === 'preview' && (
              <Button 
                onClick={handleImport}
                disabled={isUploading || previewData.length === 0 || previewData.length === invalidRows.length}
                className="bg-gradient-to-r from-brand-purple to-brand-gold"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Importation...
                  </>
                ) : (
                  <>
                    Importer {previewData.length - invalidRows.length} cartes
                    <ArrowRightIcon className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            )}
          </div>
        </CardFooter>
      </Card>
    </div>
  );

  // Fonctions utilitaires
  function getStepTitle() {
    switch(step) {
      case 'upload': return "Importer des flashcards";
      case 'map': return "Mapper les colonnes";
      case 'preview': return "Aperçu des données";
      case 'import': return "Importation réussie";
      default: return "Importer des flashcards";
    }
  }

  function getProgressLabel() {
    switch(step) {
      case 'upload': return "Analyse du fichier...";
      case 'map': return "Traitement des données...";
      case 'preview': return "Préparation de l'aperçu...";
      case 'import': return "Importation en cours...";
      default: return "Traitement en cours...";
    }
  }
}