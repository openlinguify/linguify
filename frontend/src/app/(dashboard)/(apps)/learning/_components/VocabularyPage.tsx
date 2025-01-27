import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ThumbsUp, ThumbsDown, Download, Printer } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import * as XLSX from 'xlsx';

interface VocabularyWord {
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

// Sample data for preview
const SAMPLE_VOCABULARY: VocabularyWord[] = [
  {
    word_en: "Journey",
    word_fr: "Voyage",
    word_es: "Viaje",
    word_nl: "Reis",
    definition_en: "An act of traveling from one place to another, especially over a long distance",
    definition_fr: "Action de se déplacer d'un endroit à un autre, particulièrement sur une longue distance",
    definition_es: "Acto de trasladarse de un lugar a otro, especialmente a larga distancia",
    definition_nl: "Het zich verplaatsen van de ene plaats naar de andere, vooral over lange afstand",
    example_sentence_en: "Their journey to the mountains was full of adventures.",
    example_sentence_fr: "Leur voyage dans les montagnes était plein d'aventures.",
    example_sentence_es: "Su viaje a las montañas estuvo lleno de aventuras.",
    example_sentence_nl: "Hun reis naar de bergen was vol avonturen.",
    word_type_en: "noun",
    word_type_fr: "nom",
    word_type_es: "sustantivo",
    word_type_nl: "zelfstandig naamwoord",
    synonymous_en: "trip, voyage, excursion, expedition",
    synonymous_fr: "périple, traversée, excursion, expédition",
    synonymous_es: "travesía, excursión, expedición, trayecto",
    synonymous_nl: "tocht, expeditie, uitstap, trip",
    antonymous_en: "arrival, destination, stay",
    antonymous_fr: "arrivée, destination, séjour",
    antonymous_es: "llegada, destino, estancia",
    antonymous_nl: "aankomst, bestemming, verblijf"
  },
  {
    word_en: "Discover",
    word_fr: "Découvrir",
    word_es: "Descubrir",
    word_nl: "Ontdekken",
    definition_en: "To find something or someone unexpectedly or during a search",
    definition_fr: "Trouver quelque chose ou quelqu'un de manière inattendue ou après une recherche",
    definition_es: "Encontrar algo o alguien inesperadamente o durante una búsqueda",
    definition_nl: "Iets of iemand onverwacht of tijdens een zoektocht vinden",
    example_sentence_en: "Scientists discovered a new species in the rainforest.",
    example_sentence_fr: "Les scientifiques ont découvert une nouvelle espèce dans la forêt tropicale.",
    example_sentence_es: "Los científicos descubrieron una nueva especie en la selva tropical.",
    example_sentence_nl: "Wetenschappers ontdekten een nieuwe soort in het regenwoud.",
    word_type_en: "verb",
    word_type_fr: "verbe",
    word_type_es: "verbo",
    word_type_nl: "werkwoord",
    synonymous_en: "uncover, find, locate, detect",
    synonymous_fr: "trouver, repérer, détecter, dénicher",
    synonymous_es: "encontrar, hallar, localizar, detectar",
    synonymous_nl: "vinden, aantreffen, opsporen, waarnemen",
    antonymous_en: "hide, conceal, miss, overlook",
    antonymous_fr: "cacher, dissimuler, manquer, négliger",
    antonymous_es: "ocultar, esconder, perder, pasar por alto",
    antonymous_nl: "verbergen, verhullen, missen, over het hoofd zien"
  },
  {
    word_en: "Courage",
    word_fr: "Courage",
    word_es: "Coraje",
    word_nl: "Moed",
    definition_en: "The ability to face danger, pain, or difficulty without fear",
    definition_fr: "Capacité à faire face au danger, à la douleur ou à la difficulté sans peur",
    definition_es: "Capacidad de enfrentar el peligro, dolor o dificultad sin miedo",
    definition_nl: "Het vermogen om gevaar, pijn of moeilijkheden zonder angst tegemoet te treden",
    example_sentence_en: "It takes great courage to stand up for what you believe in.",
    example_sentence_fr: "Il faut beaucoup de courage pour défendre ses convictions.",
    example_sentence_es: "Se necesita gran coraje para defender lo que uno cree.",
    example_sentence_nl: "Het vergt veel moed om op te komen voor waar je in gelooft.",
    word_type_en: "noun",
    word_type_fr: "nom",
    word_type_es: "sustantivo",
    word_type_nl: "zelfstandig naamwoord",
    synonymous_en: "bravery, valor, fearlessness, boldness",
    synonymous_fr: "bravoure, vaillance, intrépidité, audace",
    synonymous_es: "valentía, valor, osadía, intrepidez",
    synonymous_nl: "dapperheid, durf, onverschrokkenheid, lef",
    antonymous_en: "cowardice, fear, timidity, weakness",
    antonymous_fr: "lâcheté, peur, timidité, faiblesse",
    antonymous_es: "cobardía, miedo, timidez, debilidad",
    antonymous_nl: "lafheid, angst, verlegenheid, zwakheid"
  }
];

const VocabularyPage = () => {
  const [nativeLanguage, setNativeLanguage] = useState<LanguageCode>('fr');
  const [targetLanguage, setTargetLanguage] = useState<LanguageCode>('en');
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [knownWords, setKnownWords] = useState<Set<number>>(new Set());

  const currentWord = SAMPLE_VOCABULARY[currentWordIndex];

  const handleNextWord = () => {
    setCurrentWordIndex((prev) => (prev + 1) % SAMPLE_VOCABULARY.length);
  };

  const handlePreviousWord = () => {
    setCurrentWordIndex((prev) => (prev - 1 + SAMPLE_VOCABULARY.length) % SAMPLE_VOCABULARY.length);
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

  const exportToExcel = () => {
    const exportData = SAMPLE_VOCABULARY.map(word => ({
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
          ${SAMPLE_VOCABULARY.map(word => `
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

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="bg-white shadow-lg">
        <CardHeader>
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div className="flex flex-col">
              <CardTitle className="text-2xl font-bold">Apprentissage du vocabulaire</CardTitle>
              <span className="text-sm text-gray-500 mt-1">
                {currentWordIndex + 1} / {SAMPLE_VOCABULARY.length} mots
              </span>
            </div>
            <div className="flex gap-4">
              <Select value={nativeLanguage} onValueChange={(value: LanguageCode) => setNativeLanguage(value)}>
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
              <Select value={targetLanguage} onValueChange={(value: LanguageCode) => setTargetLanguage(value)}>
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
            {/* Word to learn */}
            <div className="text-center p-8 bg-blue-50 rounded-lg shadow-sm">
              <h2 className="text-4xl font-bold mb-3">{getWordInLanguage(targetLanguage)}</h2>
              <p className="text-xl text-gray-600">{getWordInLanguage(nativeLanguage)}</p>
              <div className="mt-2 text-sm text-gray-500">
                Type: {currentWord[`word_type_${targetLanguage}` as keyof VocabularyWord]}
              </div>
            </div>

            {/* Example sentence */}
            <div className="bg-gray-50 p-6 rounded-lg space-y-3 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-2">Example:</h3>
              <p className="font-medium text-lg">{getExampleInLanguage(targetLanguage)}</p>
              <p className="text-gray-600 italic">{getExampleInLanguage(nativeLanguage)}</p>
            </div>

            {/* Additional information tabs */}
            <Tabs defaultValue="definition" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="definition">Definition</TabsTrigger>
                <TabsTrigger value="synonyms">Synonyms</TabsTrigger>
                <TabsTrigger value="antonyms">Antonyms</TabsTrigger>
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
                        {currentWord[`synonymous_${targetLanguage}` as keyof VocabularyWord]}
                      </p>
                      <p className="text-gray-600">
                        {currentWord[`synonymous_${nativeLanguage}` as keyof VocabularyWord]}
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
                        {currentWord[`antonymous_${targetLanguage}` as keyof VocabularyWord]}
                      </p>
                      <p className="text-gray-600">
                        {currentWord[`antonymous_${nativeLanguage}` as keyof VocabularyWord]}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            {/* Navigation and controls */}
            <div className="flex justify-between items-center pt-4">
              <Button 
                onClick={handlePreviousWord} 
                variant="outline"
                className="hover:bg-blue-50"
              >
                Previous
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
                  {knownWords.has(currentWordIndex) ? 'Word Mastered' : 'Need Review'}
                </Button>
                <div className="text-sm text-gray-500 mt-2">
                  {currentWordIndex + 1} / {SAMPLE_VOCABULARY.length}
                </div>
              </div>
              <Button 
                onClick={handleNextWord} 
                variant="outline"
                className="hover:bg-blue-50"
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VocabularyPage;