// src/addons/quizz/components/QuizCreator.tsx
'use client';

import React, { useState } from 'react';
import { Plus, Save, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

interface Question {
  id: string;
  type: 'mcq' | 'true_false' | 'short_answer';
  text: string;
  answers: Answer[];
  points: number;
  explanation?: string;
}

interface Answer {
  id: string;
  text: string;
  isCorrect: boolean;
}

interface QuizCreatorProps {
  onSave: (quiz: any) => void;
  onCancel: () => void;
}

export const QuizCreator: React.FC<QuizCreatorProps> = ({ onSave, onCancel }) => {
  const [quiz, setQuiz] = useState({
    title: '',
    description: '',
    category: '',
    difficulty: 'medium' as 'easy' | 'medium' | 'hard',
    timeLimit: '',
    isPublic: true,
  });

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question>({
    id: '',
    type: 'mcq',
    text: '',
    answers: [],
    points: 1,
    explanation: '',
  });

  const addAnswer = () => {
    const newAnswer: Answer = {
      id: Date.now().toString(),
      text: '',
      isCorrect: false,
    };
    setCurrentQuestion(prev => ({
      ...prev,
      answers: [...prev.answers, newAnswer],
    }));
  };

  const updateAnswer = (answerId: string, field: keyof Answer, value: any) => {
    setCurrentQuestion(prev => ({
      ...prev,
      answers: prev.answers.map(answer =>
        answer.id === answerId ? { ...answer, [field]: value } : answer
      ),
    }));
  };

  const removeAnswer = (answerId: string) => {
    setCurrentQuestion(prev => ({
      ...prev,
      answers: prev.answers.filter(answer => answer.id !== answerId),
    }));
  };

  const addQuestion = () => {
    if (currentQuestion.text && currentQuestion.answers.some(a => a.isCorrect)) {
      const newQuestion: Question = {
        ...currentQuestion,
        id: Date.now().toString(),
      };
      setQuestions(prev => [...prev, newQuestion]);
      setCurrentQuestion({
        id: '',
        type: 'mcq',
        text: '',
        answers: [],
        points: 1,
        explanation: '',
      });
    }
  };

  const removeQuestion = (questionId: string) => {
    setQuestions(prev => prev.filter(q => q.id !== questionId));
  };

  const handleSave = () => {
    if (quiz.title && questions.length > 0) {
      onSave({
        ...quiz,
        questions,
        timeLimit: quiz.timeLimit ? parseInt(quiz.timeLimit) : null,
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Quiz Info */}
      <Card>
        <CardHeader>
          <CardTitle>Informations du Quiz</CardTitle>
          <CardDescription>Configurez les détails de base de votre quiz</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="title">Titre *</Label>
              <Input
                id="title"
                value={quiz.title}
                onChange={(e) => setQuiz(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Titre du quiz"
              />
            </div>
            <div>
              <Label htmlFor="category">Catégorie</Label>
              <Input
                id="category"
                value={quiz.category}
                onChange={(e) => setQuiz(prev => ({ ...prev, category: e.target.value }))}
                placeholder="Ex: Grammaire, Vocabulaire..."
              />
            </div>
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={quiz.description}
              onChange={(e) => setQuiz(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Description du quiz"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="difficulty">Difficulté</Label>
              <Select value={quiz.difficulty} onValueChange={(value: any) => setQuiz(prev => ({ ...prev, difficulty: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="easy">Facile</SelectItem>
                  <SelectItem value="medium">Moyen</SelectItem>
                  <SelectItem value="hard">Difficile</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="timeLimit">Temps limite (minutes)</Label>
              <Input
                id="timeLimit"
                type="number"
                value={quiz.timeLimit}
                onChange={(e) => setQuiz(prev => ({ ...prev, timeLimit: e.target.value }))}
                placeholder="0 = illimité"
              />
            </div>
            <div className="flex items-center space-x-2 pt-6">
              <Switch
                id="isPublic"
                checked={quiz.isPublic}
                onCheckedChange={(checked) => setQuiz(prev => ({ ...prev, isPublic: checked }))}
              />
              <Label htmlFor="isPublic">Quiz public</Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Question Creator */}
      <Card>
        <CardHeader>
          <CardTitle>Ajouter une Question</CardTitle>
          <CardDescription>Créez les questions de votre quiz</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="questionText">Question *</Label>
            <Textarea
              id="questionText"
              value={currentQuestion.text}
              onChange={(e) => setCurrentQuestion(prev => ({ ...prev, text: e.target.value }))}
              placeholder="Tapez votre question ici..."
              rows={2}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="questionType">Type de question</Label>
              <Select
                value={currentQuestion.type}
                onValueChange={(value: any) => setCurrentQuestion(prev => ({ ...prev, type: value, answers: [] }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mcq">Choix multiples</SelectItem>
                  <SelectItem value="true_false">Vrai/Faux</SelectItem>
                  <SelectItem value="short_answer">Réponse courte</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="points">Points</Label>
              <Input
                id="points"
                type="number"
                min="1"
                value={currentQuestion.points}
                onChange={(e) => setCurrentQuestion(prev => ({ ...prev, points: parseInt(e.target.value) || 1 }))}
              />
            </div>
          </div>

          {/* Answers */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <Label>Réponses</Label>
              <Button type="button" variant="outline" size="sm" onClick={addAnswer}>
                <Plus className="h-4 w-4 mr-1" />
                Ajouter réponse
              </Button>
            </div>
            
            <div className="space-y-2">
              {currentQuestion.answers.map((answer) => (
                <div key={answer.id} className="flex items-center gap-2">
                  <Input
                    value={answer.text}
                    onChange={(e) => updateAnswer(answer.id, 'text', e.target.value)}
                    placeholder="Texte de la réponse"
                    className="flex-1"
                  />
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={answer.isCorrect}
                      onCheckedChange={(checked) => updateAnswer(answer.id, 'isCorrect', checked)}
                    />
                    <Label className="text-sm">Correcte</Label>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => removeAnswer(answer.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="explanation">Explication (optionnel)</Label>
            <Textarea
              id="explanation"
              value={currentQuestion.explanation}
              onChange={(e) => setCurrentQuestion(prev => ({ ...prev, explanation: e.target.value }))}
              placeholder="Expliquez pourquoi cette réponse est correcte..."
              rows={2}
            />
          </div>

          <Button
            onClick={addQuestion}
            disabled={!currentQuestion.text || !currentQuestion.answers.some(a => a.isCorrect)}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-2" />
            Ajouter la question
          </Button>
        </CardContent>
      </Card>

      {/* Questions List */}
      {questions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Questions ajoutées ({questions.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {questions.map((question, index) => (
                <div key={question.id} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium">Q{index + 1}: {question.text}</h4>
                      <p className="text-sm text-gray-600">
                        {question.type} • {question.points} point(s) • {question.answers.filter(a => a.isCorrect).length} bonne(s) réponse(s)
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeQuestion(question.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Button onClick={handleSave} disabled={!quiz.title || questions.length === 0} className="flex-1">
          <Save className="h-4 w-4 mr-2" />
          Sauvegarder le Quiz
        </Button>
        <Button variant="outline" onClick={onCancel}>
          Annuler
        </Button>
      </div>
    </div>
  );
};

export default QuizCreator;