'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useTranslations } from '@/hooks/useTranslations'; // Chemin correct
import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle, BookOpen, Users, Award, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

export default function Home() {
  const t = useTranslations('home'); // Utiliser 'home' comme namespace
  const [activeLanguage, setActiveLanguage] = useState('spanish');

  // Langue disponibles
  const languages = [
    { id: 'spanish', name: 'Español', flag: '🇪🇸', color: 'bg-red-500' },
    { id: 'english', name: 'English', flag: '🇬🇧', color: 'bg-blue-600' },
    { id: 'french', name: 'Français', flag: '🇫🇷', color: 'bg-indigo-500' },
    { id: 'german', name: 'Deutsch', flag: '🇩🇪', color: 'bg-yellow-500' },
    { id: 'italian', name: 'Italiano', flag: '🇮🇹', color: 'bg-green-500' },
    { id: 'dutch', name: 'Nederlands', flag: '🇳🇱', color: 'bg-orange-500' },
  ];

  // Témoignages
  const testimonials = [
    {
      name: 'Sophie M.',
      role: 'Marketing Manager',
      text: "Linguify a transformé mon apprentissage du français. En 3 mois, j'ai atteint un niveau que je n'aurais jamais cru possible !",
      avatar: '/img/avatar1.png',
    },
    {
      name: 'David L.',
      role: 'Software Engineer',
      text: "Les flashcards et les exercices interactifs m'ont aidé à mémoriser facilement du vocabulaire technique en allemand.",
      avatar: '/img/avatar2.png',
    },
    {
      name: 'Elena R.',
      role: 'Travel Blogger',
      text: "Grâce à Linguify, j'ai pu communiquer avec les locaux lors de mon voyage à travers l'Espagne. Une expérience incroyable !",
      avatar: '/img/avatar3.png',
    },
  ];

  // Caractéristiques
  const features = [
    { 
      icon: <BookOpen className="h-6 w-6 text-indigo-600" />, 
      title: "Apprentissage adaptatif", 
      description: "Linguify adapte votre parcours d'apprentissage en fonction de vos forces et faiblesses." 
    },
    { 
      icon: <Users className="h-6 w-6 text-indigo-600" />, 
      title: "Communauté active", 
      description: "Pratiquez avec des natifs et d'autres apprenants dans notre communauté mondiale." 
    },
    { 
      icon: <Award className="h-6 w-6 text-indigo-600" />, 
      title: "Certification reconnue", 
      description: "Obtenez des certificats reconnus qui valorisent votre niveau linguistique." 
    },
    { 
      icon: <MessageCircle className="h-6 w-6 text-indigo-600" />, 
      title: "Coaching personnalisé", 
      description: "Nos tuteurs professionnels vous aident à atteindre vos objectifs linguistiques." 
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Section Hero */}
      <section className="relative bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 py-20 md:py-32">
        <div className="absolute inset-0 bg-[url('/img/pattern.svg')] opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <motion.h1 
            className="text-4xl md:text-6xl font-extrabold tracking-tight mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {t('hero.title') || "Maîtrisez de nouvelles langues de façon naturelle"}
          </motion.h1>
          <motion.p 
            className="text-xl md:text-2xl max-w-3xl mx-auto mb-8 text-indigo-100"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {t('hero.subtitle') || "Linguify combine l'IA, la science cognitive et l'apprentissage adaptatif pour vous faire progresser rapidement."}
          </motion.p>
          <motion.div 
            className="flex flex-col sm:flex-row justify-center gap-4 mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Button size="lg" className="bg-white text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700">
              {t('hero.start_button') || "Commencer gratuitement"}
            </Button>
            <Button size="lg" variant="outline" className="text-white border-white hover:bg-white/10">
              {t('hero.discover_button') || "Découvrir nos méthodes"}
            </Button>
          </motion.div>
          
          <motion.div 
            className="relative mx-auto w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.6 }}
          >
            <div className="bg-white p-1 rounded-2xl">
              <div className="relative w-full aspect-video">
                <Image
                  src="/img/app-screenshot.jpg"
                  alt={t('hero.screenshot_alt') || "Linguify app interface"}
                  fill
                  className="object-cover rounded-xl"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="bg-black/60 rounded-full p-4 cursor-pointer hover:bg-black/70 transition-colors">
                    <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M6.3 2.841A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Reste du code inchangé pour la brièveté */}
      {/* Vous pouvez continuer à ajouter des appels à t() pour les autres sections */}
      
      {/* Section Statistiques */}
      <section className="py-16 bg-gradient-to-b from-indigo-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="flex flex-col items-center">
              <div className="text-4xl font-bold text-indigo-600 mb-2">25+</div>
              <div className="text-gray-600">{t('stats.languages') || "Langues disponibles"}</div>
            </div>
            {/* Autres statistiques... */}
          </div>
        </div>
      </section>
      
      {/* Autres sections... */}
    </div>
  );
}