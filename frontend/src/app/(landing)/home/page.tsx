'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { 
  ArrowRight, 
  CheckCircle, 
  BookOpen, 
  Users, 
  Award, 
  MessageCircle, 
  Brain, 
  Globe, 
  Star 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';

export default function Home() {
  const [activeLanguage, setActiveLanguage] = useState('spanish');
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  // Available languages
  const languages = [
    { id: 'spanish', name: 'Español', flag: '🇪🇸', color: 'bg-red-500' },
    { id: 'english', name: 'English', flag: '🇬🇧', color: 'bg-blue-600' },
    { id: 'french', name: 'Français', flag: '🇫🇷', color: 'bg-indigo-500' },
    { id: 'german', name: 'Deutsch', flag: '🇩🇪', color: 'bg-yellow-500' },
    { id: 'italian', name: 'Italiano', flag: '🇮🇹', color: 'bg-green-500' },
    { id: 'dutch', name: 'Nederlands', flag: '🇳🇱', color: 'bg-orange-500' },
  ];

  // Testimonials
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

  // Features
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

  // Pricing plans
  const pricingPlans = [
    {
      name: "Gratuit",
      price: "0€",
      period: "pour toujours",
      description: "Parfait pour débuter et tester l'application",
      features: [
        "1 langue au choix",
        "Accès aux leçons de base",
        "5 minutes de chat par jour",
        "Révisions limitées"
      ],
      cta: "Commencer gratuitement",
      popular: false
    },
    {
      name: "Premium",
      price: "9,99€",
      period: "par mois",
      description: "Notre formule la plus populaire pour progresser",
      features: [
        "Toutes les langues accessibles",
        "Leçons avancées et spécialisées",
        "Chat illimité avec l'IA",
        "Système complet de révision",
        "Coaching hebdomadaire"
      ],
      cta: "Essai gratuit de 7 jours",
      popular: true
    },
    {
      name: "Entreprise",
      price: "Sur mesure",
      period: "",
      description: "Solution complète pour les équipes",
      features: [
        "Formations personnalisées",
        "Tableau de bord d'entreprise",
        "Suivi des progrès de l'équipe",
        "Intégration LMS",
        "Support dédié"
      ],
      cta: "Contacter les ventes",
      popular: false
    }
  ];

  // Stats
  const stats = [
    { figure: "25+", label: "Langues disponibles" },
    { figure: "10M+", label: "Utilisateurs actifs" },
    { figure: "98%", label: "Taux de satisfaction" },
    { figure: "120+", label: "Pays représentés" },
  ];

  // Smooth fadeIn animation for sections
  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  // Handle video play
  const playVideo = () => {
    setIsVideoPlaying(true);
    // Logic to play video would go here
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section - Enhanced with animated gradient */}
      <section className="relative bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0 opacity-20 bg-[url('/pattern.svg')]"></div>
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: 'radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0) 25%), radial-gradient(circle at 70% 65%, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0) 30%)'
          }}
        ></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white z-10">
          <motion.h1 
            className="text-4xl md:text-6xl font-extrabold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-indigo-100"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            Maîtrisez de nouvelles langues de façon naturelle
          </motion.h1>
          
          <motion.p 
            className="text-xl md:text-2xl max-w-3xl mx-auto mb-8 text-indigo-100"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            Linguify combine l'IA, la science cognitive et l'apprentissage adaptatif pour vous faire progresser rapidement.
          </motion.p>
          
          <motion.div 
            className="flex flex-col sm:flex-row justify-center gap-4 mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Link href="/register">
              <Button size="lg" className="bg-white text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700 font-medium px-8">
                Commencer gratuitement
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/features">
              <Button size="lg" variant="outline" className="text-white border-white hover:bg-white/10 font-medium px-8">
                Découvrir nos méthodes
              </Button>
            </Link>
          </motion.div>
          
          {/* Interactive app demo */}
          <motion.div 
            className="relative mx-auto w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.6 }}
          >
            <div className="bg-white p-1 rounded-2xl">
              <div className="relative w-full aspect-video">
                {isVideoPlaying ? (
                  <div className="w-full h-full bg-black">
                    {/* Video player would go here */}
                    <iframe 
                      className="w-full h-full" 
                      src="about:blank" 
                      frameBorder="0" 
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                      allowFullScreen
                    ></iframe>
                  </div>
                ) : (
                  <>
                    <div className="absolute inset-0 bg-gray-200 flex items-center justify-center text-gray-500 rounded-xl">
                      <div className="text-center">
                        <p>Capture d'écran de l'application</p>
                        <p className="text-sm">(Image non disponible)</p>
                      </div>
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <button 
                        onClick={playVideo}
                        className="bg-black/60 rounded-full p-4 cursor-pointer hover:bg-black/70 transition-colors transform hover:scale-105"
                      >
                        <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M6.3 2.841A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                        </svg>
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Floating language bubbles - decorative element */}
        <div className="absolute bottom-0 left-0 right-0 h-20 overflow-hidden">
          {languages.map((lang, index) => (
            <motion.div
              key={lang.id}
              className={`absolute bottom-0 ${lang.color} rounded-full flex items-center justify-center w-14 h-14 opacity-80`}
              initial={{ y: 100 }}
              animate={{ 
                y: [100, -50, -20, -30, -25], 
                x: [index * 50, index * 60, index * 55, index * 58, index * 56],
                opacity: [0, 0.8, 0.7, 0.85, 0.8]
              }}
              transition={{ 
                duration: 10,
                repeat: Infinity,
                repeatType: 'reverse',
                delay: index * 0.5
              }}
            >
              <span className="text-2xl">{lang.flag}</span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Language Selector */}
      <section className="py-10 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-6">
              Quelle langue souhaitez-vous apprendre ?
            </h2>
            <div className="flex flex-wrap justify-center gap-4">
              {languages.map((lang) => (
                <motion.button
                  key={lang.id}
                  className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                    activeLanguage === lang.id
                      ? `${lang.color} text-white`
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  onClick={() => setActiveLanguage(lang.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>{lang.flag}</span>
                  <span>{lang.name}</span>
                </motion.button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Statistics Section - Improved visual presentation */}
      <section className="py-16 bg-gradient-to-b from-indigo-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={{
              visible: {
                transition: {
                  staggerChildren: 0.15
                }
              }
            }}
          >
            {stats.map((stat, index) => (
              <motion.div 
                key={index}
                className="flex flex-col items-center p-6 rounded-lg bg-white shadow-sm border border-indigo-50"
                variants={fadeIn}
                transition={{ duration: 0.5 }}
              >
                <div className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  {stat.figure}
                </div>
                <div className="text-gray-600">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section - Enhanced with animations */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <motion.h2 
              className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
              transition={{ duration: 0.5 }}
            >
              Pourquoi choisir Linguify ?
            </motion.h2>
            <motion.p 
              className="text-xl text-gray-600 max-w-3xl mx-auto"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              Notre plateforme a été conçue par des experts en linguistique et en pédagogie pour maximiser votre progression.
            </motion.p>
          </div>

          <motion.div 
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-8"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={{
              visible: {
                transition: {
                  staggerChildren: 0.15
                }
              }
            }}
          >
            {features.map((feature, index) => (
              <motion.div 
                key={index}
                className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
                variants={fadeIn}
                transition={{ duration: 0.5 }}
              >
                <div className="bg-indigo-50 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>

          <motion.div 
            className="mt-12 text-center"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Link href="/features">
              <Button variant="outline" size="lg" className="text-indigo-600 border-indigo-600 hover:bg-indigo-50">
                En savoir plus sur nos fonctionnalités
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Testimonials Section - Improved with animated cards */}
      <section className="py-20 bg-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <motion.h2 
              className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
              transition={{ duration: 0.5 }}
            >
              Ce que nos utilisateurs disent
            </motion.h2>
            <motion.p 
              className="text-xl text-gray-600 max-w-3xl mx-auto"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              Rejoignez des milliers d'apprenants satisfaits qui ont transformé leur approche des langues.
            </motion.p>
          </div>

          <motion.div 
            className="grid md:grid-cols-3 gap-8"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={{
              visible: {
                transition: {
                  staggerChildren: 0.15
                }
              }
            }}
          >
            {testimonials.map((testimonial, index) => (
              <motion.div 
                key={index}
                className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow relative"
                variants={fadeIn}
                transition={{ duration: 0.5 }}
                whileHover={{ y: -5 }}
              >
                <div className="absolute -top-6 left-8">
                  <div className="relative w-12 h-12 rounded-full overflow-hidden border-4 border-white shadow-sm bg-gray-200">
                    {/* Placeholder for avatar if image fails to load */}
                    <div className="flex items-center justify-center h-full text-gray-400">
                      {testimonial.name.charAt(0)}
                    </div>
                  </div>
                </div>
                <div className="pt-6">
                  <div className="flex items-center mb-4">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star key={star} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-600 italic mb-6">{testimonial.text}</p>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-gray-500">{testimonial.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <motion.h2 
              className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
              transition={{ duration: 0.5 }}
            >
              Des forfaits adaptés à vos besoins
            </motion.h2>
            <motion.p 
              className="text-xl text-gray-600 max-w-3xl mx-auto"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeIn}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              Choisissez l'offre qui correspond à vos objectifs et à votre rythme d'apprentissage.
            </motion.p>
          </div>

          <motion.div 
            className="grid md:grid-cols-3 gap-8"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={{
              visible: {
                transition: {
                  staggerChildren: 0.15
                }
              }
            }}
          >
            {pricingPlans.map((plan, index) => (
              <motion.div 
                key={index}
                className={`bg-white rounded-xl overflow-hidden ${
                  plan.popular 
                    ? 'border-2 border-indigo-500 shadow-lg relative' 
                    : 'border border-gray-200 shadow-sm'
                }`}
                variants={fadeIn}
                transition={{ duration: 0.5 }}
                whileHover={{ y: -5 }}
              >
                {plan.popular && (
                  <div className="absolute top-0 right-0">
                    <Badge className="bg-indigo-500 text-white m-4">Le plus populaire</Badge>
                  </div>
                )}
                
                <div className="p-8">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="flex items-end">
                    <div className="text-4xl font-bold">{plan.price}</div>
                    {plan.period && (
                      <div className="text-gray-500 ml-1 mb-1">{plan.period}</div>
                    )}
                  </div>
                  <p className="mt-4 text-gray-600">{plan.description}</p>
                  
                  <div className="mt-6 space-y-4">
                    {plan.features.map((feature, i) => (
                      <div key={i} className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-indigo-500 mt-0.5 mr-2 flex-shrink-0" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-8">
                    <Link href={index === 2 ? "/contact" : "/register"}>
                      <Button 
                        className={`w-full ${
                          plan.popular 
                            ? 'bg-indigo-600 hover:bg-indigo-700 text-white' 
                            : 'bg-white border border-indigo-600 text-indigo-600 hover:bg-indigo-50'
                        }`}
                        size="lg"
                      >
                        {plan.cta}
                      </Button>
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Call-to-Action Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.h2 
            className="text-3xl md:text-4xl font-bold mb-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
            transition={{ duration: 0.5 }}
          >
            Prêt à commencer votre voyage linguistique ?
          </motion.h2>
          <motion.p 
            className="text-xl text-indigo-100 mb-8 max-w-3xl mx-auto"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            Rejoignez notre communauté d'apprenants et commencez à maîtriser une nouvelle langue dès aujourd'hui.
          </motion.p>
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Link href="/register">
              <Button size="lg" className="bg-white text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700 font-medium px-8">
                Commencer gratuitement
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}