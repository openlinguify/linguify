'use client';
import { useAuth0 } from '@auth0/auth0-react';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ThumbsUp, ThumbsDown, Download, Printer, AlertCircle } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import * as XLSX from 'xlsx';


interface VocabularyWord {
  id: number;
  content_lesson: string;
  word_en: string;
  word_fr: string;
  word_es: string;
  word_nl: string;
  definition_en: string;
  definition_fr: string;
  definition_es: string;
  definition_nl: string;
  example_sentence_en: string | null;
  example_sentence_fr: string | null;
  example_sentence_es: string | null;
  example_sentence_nl: string | null;
  word_type_en: string;
  word_type_fr: string;
  word_type_es: string;
  word_type_nl: string;
  synonymous_en: string | null;
  synonymous_fr: string | null;
  synonymous_es: string | null;
  synonymous_nl: string | null;
  antonymous_en: string | null;
  antonymous_fr: string | null;
  antonymous_es: string | null;
  antonymous_nl: string | null;
}

type LanguageCode = 'en' | 'fr' | 'es' | 'nl';

interface VocabularyPageProps {
  vocabularyLists?: VocabularyWord[];
}

const VocabularyPage = ({ vocabularyLists }: VocabularyPageProps) => {
  // 1. D'abord le hook Auth0
  const { getAccessTokenSilently, isAuthenticated, isLoading: isAuthLoading } = useAuth0();

  // 2. Ensuite les autres states
  const [vocabulary, setVocabulary] = useState<VocabularyWord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nativeLanguage, setNativeLanguage] = useState<LanguageCode>(() => 
    (localStorage.getItem('nativeLanguage') as LanguageCode) || 'fr'
  );
  const [targetLanguage, setTargetLanguage] = useState<LanguageCode>(() => 
    (localStorage.getItem('targetLanguage') as LanguageCode) || 'en'
  );
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [knownWords, setKnownWords] = useState<Set<number>>(() => {
    const saved = localStorage.getItem('knownWords');
    return saved ? new Set(JSON.parse(saved)) : new Set();
  });

  // Mot courant avec valeurs par défaut
  const currentWord = vocabulary[currentWordIndex] || {
    id: 0,
    content_lesson: '',
    word_en: '',
    word_fr: '',
    word_es: '',
    word_nl: '',
    definition_en: '',
    definition_fr: '',
    definition_es: '',
    definition_nl: '',
    example_sentence_en: '',
    example_sentence_fr: '',
    example_sentence_es: '',
    example_sentence_nl: '',
    word_type_en: '',
    word_type_fr: '',
    word_type_es: '',
    word_type_nl: '',
    synonymous_en: '',
    synonymous_fr: '',
    synonymous_es: '',
    synonymous_nl: '',
    antonymous_en: '',
    antonymous_fr: '',
    antonymous_es: '',
    antonymous_nl: '',
  };

  useEffect(() => {
    const fetchVocabulary = async () => {
      try {
        if (!isAuthenticated) {
          throw new Error('Not authenticated');
        }

        const token = await getAccessTokenSilently();
        
        const response = await fetch('http://localhost:8000/api/v1/course/vocabulary-list/', {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch vocabulary');
        }

        const data = await response.json();
        setVocabulary(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching vocabulary:', err);
        setError('Failed to load vocabulary');
      } finally {
        setLoading(false);
      }
    };

    if (vocabularyLists?.length) {
      setVocabulary(vocabularyLists);
      setLoading(false);
    } else if (isAuthenticated && !isAuthLoading) {
      fetchVocabulary();
    }
  }, [vocabularyLists, isAuthenticated, isAuthLoading, getAccessTokenSilently]);

  useEffect(() => {
    localStorage.setItem('knownWords', JSON.stringify(Array.from(knownWords)));
  }, [knownWords]);

  useEffect(() => {
    localStorage.setItem('nativeLanguage', nativeLanguage);
  }, [nativeLanguage]);

  useEffect(() => {
    localStorage.setItem('targetLanguage', targetLanguage);
  }, [targetLanguage]);

  // Handlers
  const handleNextWord = () => {
    setCurrentWordIndex((prev) => (prev + 1) % vocabulary.length);
  };
  
  const handlePreviousWord = () => {
    setCurrentWordIndex((prev) => (prev - 1 + vocabulary.length) % vocabulary.length);
  };

  const handleNativeLanguageChange = (value: LanguageCode) => {
    setNativeLanguage(value);
  };

  const handleTargetLanguageChange = (value: LanguageCode) => {
    setTargetLanguage(value);
  };

  const toggleKnownStatus = () => {
    setKnownWords((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(currentWordIndex)) {
        newSet.delete(currentWordIndex);
      } else {
        newSet.add(currentWordIndex);
      }
      return newSet;
    });
  };

  // Getters
  const getWordInLanguage = (language: LanguageCode) => {
    const wordKey = `word_${language}` as keyof VocabularyWord;
    return currentWord[wordKey];
  };

  const getDefinitionInLanguage = (language: LanguageCode) => {
    const definitionKey = `definition_${language}` as keyof VocabularyWord;
    return currentWord[definitionKey];
  };

  const getExampleInLanguage = (language: LanguageCode) => {
    const exampleKey = `example_sentence_${language}` as keyof VocabularyWord;
    return currentWord[exampleKey];
  };

  // Export functions
  const exportToExcel = () => {
    const exportData = vocabulary.map(word => ({
      [`Mot (${targetLanguage})`]: word[`word_${targetLanguage}` as keyof VocabularyWord],
      [`Mot (${nativeLanguage})`]: word[`word_${nativeLanguage}` as keyof VocabularyWord],
      [`Définition (${targetLanguage})`]: word[`definition_${targetLanguage}` as keyof VocabularyWord],
      [`Définition (${nativeLanguage})`]: word[`definition_${nativeLanguage}` as keyof VocabularyWord],
      [`Exemple (${targetLanguage})`]: word[`example_sentence_${targetLanguage}` as keyof VocabularyWord],
      [`Exemple (${nativeLanguage})`]: word[`example_sentence_${nativeLanguage}` as keyof VocabularyWord],
      [`Synonymes (${targetLanguage})`]: word[`synonymous_${targetLanguage}` as keyof VocabularyWord],
      [`Antonymes (${targetLanguage})`]: word[`antonymous_${targetLanguage}` as keyof VocabularyWord],
    }));

    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Vocabulaire");
    XLSX.writeFile(workbook, `vocabulaire_${targetLanguage}_${nativeLanguage}.xlsx`);
  };

  const printVocabularyList = () => {
    const printContent = `
      <html>
        <head>
          <title>Liste de vocabulaire</title>
          <style>
            body { 
              font-family: Arial, sans-serif;
              margin: 20px;
              line-height: 1.6;
            }
            .word-entry {
              margin-bottom: 30px;
              padding: 15px;
              border-bottom: 1px solid #ccc;
              page-break-inside: avoid;
            }
            .word {
              font-size: 20px;
              font-weight: bold;
              margin-bottom: 10px;
              color: #2c5282;
            }
            .translation {
              color: #4a5568;
              margin-bottom: 10px;
            }
            .example {
              font-style: italic;
              color: #718096;
              margin-top: 10px;
            }
            @media print {
              body { font-size: 12px; }
              .word-entry { padding: 10px 0; }
              .word { font-size: 16px; }
            }
          </style>
        </head>
        <body>
          <h1>Liste de vocabulaire (${targetLanguage.toUpperCase()} - ${nativeLanguage.toUpperCase()})</h1>
          ${vocabulary.map(word => `
            <div class="word-entry">
              <div class="word">${word[`word_${targetLanguage}` as keyof VocabularyWord]} - 
                   ${word[`word_${nativeLanguage}` as keyof VocabularyWord]}</div>
              <div class="translation">
                ${word[`definition_${targetLanguage}` as keyof VocabularyWord]}<br>
                ${word[`definition_${nativeLanguage}` as keyof VocabularyWord]}
              </div>
              <div class="example">
                ${word[`example_sentence_${targetLanguage}` as keyof VocabularyWord]}<br>
                ${word[`example_sentence_${nativeLanguage}` as keyof VocabularyWord]}
              </div>
            </div>
          `).join('')}
        </body>
      </html>
    `;

    const printWindow = window.open('', '', 'height=600,width=800');
    if (printWindow) {
      printWindow.document.write(printContent);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
      printWindow.close();
    }
  };

    // 5. Les vérifications d'authentification avant le return principal
    if (isAuthLoading) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Authenticating...</div>
        </div>
      );
    }
  
    if (!isAuthenticated) {
      return (
        <div className="p-6">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>Please log in to view vocabulary.</AlertDescription>
          </Alert>
        </div>
      );
    }
  
    // 6. Les autres vérifications (loading, error, etc.)
    if (loading) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading vocabulary...</div>
        </div>
      );
    }

  // Loading states
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse">Loading vocabulary...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (vocabulary.length === 0) {
    return (
      <div className="p-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>No vocabulary items found.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="bg-white shadow-lg">
        <CardHeader>
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div className="flex flex-col">
              <CardTitle className="text-2xl font-bold">Apprentissage du vocabulaire</CardTitle>
              <span className="text-sm text-gray-500 mt-1">
                {currentWordIndex + 1} / {vocabulary.length} mots
              </span>
            </div>
            <div className="flex gap-4">
              <Select value={nativeLanguage} onValueChange={handleNativeLanguageChange}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Langue maternelle" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fr">Français</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="nl">Nederlands</SelectItem>
                </SelectContent>
              </Select>
              <Select value={targetLanguage} onValueChange={handleTargetLanguageChange}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Langue cible" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fr">Français</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="nl">Nederlands</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={exportToExcel} 
              className="flex items-center gap-2 hover:bg-blue-50"
            >
              <Download className="w-4 h-4" />
              Exporter en Excel
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={printVocabularyList} 
              className="flex items-center gap-2 hover:bg-blue-50"
            >
              <Printer className="w-4 h-4" />
              Imprimer la liste
            </Button>
          </div>
        </CardHeader>
  
        <CardContent>
          <div className="space-y-6">
            {/* Mot à apprendre */}
            <div className="text-center p-8 bg-blue-50 rounded-lg shadow-sm">
              <h2 className="text-4xl font-bold mb-3">{getWordInLanguage(targetLanguage)}</h2>
              <p className="text-xl text-gray-600">{getWordInLanguage(nativeLanguage)}</p>
              <div className="mt-2 text-sm text-gray-500">
                Type: {currentWord[`word_type_${targetLanguage}` as keyof VocabularyWord] || 'N/A'}
              </div>
            </div>
  
            {/* Exemple */}
            {(currentWord[`example_sentence_${targetLanguage}`] || currentWord[`example_sentence_${nativeLanguage}`]) && (
              <div className="bg-gray-50 p-6 rounded-lg space-y-3 shadow-sm">
                <h3 className="font-semibold text-gray-700 mb-2">Exemple :</h3>
                <p className="font-medium text-lg">{getExampleInLanguage(targetLanguage) || '-'}</p>
                <p className="text-gray-600 italic">{getExampleInLanguage(nativeLanguage) || '-'}</p>
              </div>
            )}
  
            {/* Informations supplémentaires */}
            <Tabs defaultValue="definition" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="definition">Définition</TabsTrigger>
                <TabsTrigger value="synonyms">Synonymes</TabsTrigger>
                <TabsTrigger value="antonyms">Antonymes</TabsTrigger>
              </TabsList>
  
              <TabsContent value="definition" className="mt-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="space-y-3">
                      <p className="font-medium text-lg">{getDefinitionInLanguage(targetLanguage)}</p>
                      <p className="text-gray-600">{getDefinitionInLanguage(nativeLanguage)}</p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
  
              <TabsContent value="synonyms" className="mt-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="space-y-3">
                      <p className="font-medium text-lg">
                        {currentWord[`synonymous_${targetLanguage}` as keyof VocabularyWord] || 'Aucun synonyme disponible'}
                      </p>
                      <p className="text-gray-600">
                        {currentWord[`synonymous_${nativeLanguage}` as keyof VocabularyWord] || 'Aucun synonyme disponible'}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
  
              <TabsContent value="antonyms" className="mt-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="space-y-3">
                      <p className="font-medium text-lg">
                        {currentWord[`antonymous_${targetLanguage}` as keyof VocabularyWord] || 'Aucun antonyme disponible'}
                      </p>
                      <p className="text-gray-600">
                        {currentWord[`antonymous_${nativeLanguage}` as keyof VocabularyWord] || 'Aucun antonyme disponible'}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
  
            {/* Navigation et contrôles */}
            <div className="flex justify-between items-center pt-4">
              <Button 
                onClick={handlePreviousWord} 
                variant="outline"
                className="hover:bg-blue-50"
                disabled={vocabulary.length <= 1}
              >
                Précédent
              </Button>
              <div className="text-center">
                <Button
                  onClick={toggleKnownStatus}
                  variant="outline"
                  className={`flex items-center gap-2 ${
                    knownWords.has(currentWordIndex) ? 'bg-green-100 hover:bg-green-200' : 'hover:bg-blue-50'
                  }`}
                >
                  {knownWords.has(currentWordIndex) ? (
                    <ThumbsUp className="w-4 h-4" />
                  ) : (
                    <ThumbsDown className="w-4 h-4" />
                  )}
                  {knownWords.has(currentWordIndex) ? 'Mot maîtrisé' : 'À réviser'}
                </Button>
                <div className="text-sm text-gray-500 mt-2">
                  {currentWordIndex + 1} / {vocabulary.length}
                </div>
              </div>
              <Button 
                onClick={handleNextWord} 
                variant="outline"
                className="hover:bg-blue-50"
                disabled={vocabulary.length <= 1}
              >
                Suivant
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default VocabularyPage;
