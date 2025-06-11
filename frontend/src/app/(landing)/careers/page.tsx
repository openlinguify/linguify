'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Container } from '../_components/Container';
// TODO: Re-enable jobs when jobsApi is available
// import { jobsApi, JobPosition, Department, formatEmploymentType, formatExperienceLevel, formatDate } from '@/core/api/jobsApi';

// Temporary types and functions for build
interface Department {
  id: number;
  name: string;
  description: string;
  position_count: number;
}

interface JobPosition {
  id: number;
  title: string;
  department_name?: string;
  department?: Department;
  location: string;
  employment_type: string;
  experience_level: string;
  description?: string;
  requirements?: string;
  is_open?: boolean;
  closing_date?: string;
  is_featured?: boolean;
  salary_range?: string;
  posted_date?: string;
}

const formatEmploymentType = (type: string) => type;
const formatExperienceLevel = (level: string) => level;
const formatDate = (date: string) => new Date(date).toLocaleDateString();
import { ApplicationModal } from './components/ApplicationModal';

// Import translations (we'll create these)
import enTranslations from '@/core/i18n/translations/en/careers.json';
import esTranslations from '@/core/i18n/translations/es/careers.json';
import frTranslations from '@/core/i18n/translations/fr/careers.json';
import nlTranslations from '@/core/i18n/translations/nl/careers.json';

// Types
type AvailableLocales = 'en' | 'fr' | 'es' | 'nl';

interface TranslationType {
  hero: {
    title: string;
    subtitle: string;
    cta: string;
  };
  about: {
    title: string;
    description: string;
  };
  dna: {
    title: string;
    values: Array<{
      title: string;
      description: string;
    }>;
  };
  positions: {
    title: string;
    departments: string;
    noPositions: string;
    apply: string;
  };
  benefits: {
    title: string;
    items: Array<{
      title: string;
      description: string;
    }>;
  };
  contact: {
    title: string;
    description: string;
    cta: string;
  };
}

const CareersPage: React.FC = () => {
  const [currentLocale, setCurrentLocale] = useState<AvailableLocales>('fr');
  const [jobPositions, setJobPositions] = useState<JobPosition[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<JobPosition | null>(null);
  const [isApplicationModalOpen, setIsApplicationModalOpen] = useState(false);

  // Load language from localStorage on startup
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
      setCurrentLocale(savedLanguage as AvailableLocales);
    }
  }, []);

  // Listen for language changes
  useEffect(() => {
    const handleLanguageChange = () => {
      const savedLanguage = localStorage.getItem('language');
      if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
        setCurrentLocale(savedLanguage as AvailableLocales);
      }
    };

    window.addEventListener('languageChanged', handleLanguageChange);
    
    return () => {
      window.removeEventListener('languageChanged', handleLanguageChange);
    };
  }, []);

  // Load job data
  useEffect(() => {
    const loadJobData = async () => {
      try {
        setLoading(true);
        // TODO: Re-enable when jobsApi is available
        // const [positionsData, departmentsData] = await Promise.all([
        //   jobsApi.getJobPositions(),
        //   jobsApi.getDepartments()
        // ]);
        
        // Mock data for build
        const positionsData: JobPosition[] = [];
        const departmentsData: Department[] = [];
        setJobPositions(positionsData);
        setDepartments(departmentsData);
      } catch (err) {
        console.error('Error loading job data:', err);
        setError('Failed to load job positions');
      } finally {
        setLoading(false);
      }
    };

    loadJobData();
  }, []);

  // Filter positions by department
  const filteredPositions = selectedDepartment
    ? jobPositions.filter(job => job.department_name === selectedDepartment)
    : jobPositions;

  // Handle application modal
  const handleApplyClick = (position: JobPosition) => {
    setSelectedPosition(position);
    setIsApplicationModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsApplicationModalOpen(false);
    setSelectedPosition(null);
  };

  // Translation helper function
  const getTranslation = (locale: AvailableLocales): TranslationType => {
    const translations: Record<AvailableLocales, TranslationType> = {
      fr: frTranslations.fr as TranslationType,
      en: enTranslations.en as TranslationType,
      es: esTranslations.es as TranslationType,
      nl: nlTranslations.nl as TranslationType
    };
    
    return translations[locale] || translations.en;
  };

  const t = getTranslation(currentLocale);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950">
      {/* Hero Section */}
      <section className="pt-24 pb-16">
        <Container>
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-6">
              {t.hero.title}
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 leading-relaxed">
              {t.hero.subtitle}
            </p>
            <a
              href="#positions"
              className="inline-flex items-center px-8 py-4 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              {t.hero.cta}
            </a>
          </div>
        </Container>
      </section>

      {/* About Section */}
      <section className="py-20">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
              {t.about.title}
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
              {t.about.description}
            </p>
          </div>
        </Container>
      </section>

      {/* DNA/Values Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-800">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t.dna.title}
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-6xl mx-auto">
            {t.dna.values.map((value, index) => (
              <div key={index} className="bg-white dark:bg-gray-900 rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  {value.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Open Positions Section */}
      <section id="positions" className="py-20">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t.positions.title}
            </h2>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <select 
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="w-full md:w-auto px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">{t.positions.departments}</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.name}>
                    {dept.name} ({dept.position_count})
                  </option>
                ))}
              </select>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">Loading positions...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-red-600 dark:text-red-400">{error}</p>
              </div>
            ) : filteredPositions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-600 dark:text-gray-400">{t.positions.noPositions}</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredPositions.map((job) => (
                  <div key={job.id} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-200 dark:border-gray-700">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                      <div className="mb-4 md:mb-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                            {job.title}
                          </h3>
                          {job.is_featured && (
                            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                              Featured
                            </span>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                            </svg>
                            {job.location}
                          </span>
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                            </svg>
                            {job.department_name}
                          </span>
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                            </svg>
                            {formatEmploymentType(job.employment_type)}
                          </span>
                          {job.salary_range && (
                            <span className="flex items-center">
                              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                              </svg>
                              {job.salary_range}
                            </span>
                          )}
                        </div>
                        <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                          Posted {job.posted_date ? formatDate(job.posted_date) : 'Recently'}
                        </div>
                      </div>
                      {job.is_open ? (
                        <button
                          onClick={() => handleApplyClick(job)}
                          className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium"
                        >
                          {t.positions.apply}
                        </button>
                      ) : (
                        <div className="text-center">
                          <span className="inline-flex items-center px-6 py-3 bg-red-100 text-red-700 rounded-lg font-medium cursor-not-allowed">
                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            Applications Closed
                          </span>
                          {job.closing_date && (
                            <p className="text-xs text-red-600 mt-1">
                              Closed: {new Date(job.closing_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Container>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-gray-800 dark:to-gray-900">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t.benefits.title}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {t.benefits.items.map((benefit, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center mb-6">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                  {benefit.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {benefit.description}
                </p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Contact Section */}
      <section className="py-20">
        <Container>
          <div className="text-center max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
              {t.contact.title}
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 leading-relaxed">
              {t.contact.description}
            </p>
            <Link
              href="/contact"
              className="inline-flex items-center px-8 py-4 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              {t.contact.cta}
            </Link>
          </div>
        </Container>
      </section>
      
      {/* Application Modal */}
      {selectedPosition && (
        <ApplicationModal
          isOpen={isApplicationModalOpen}
          onClose={handleCloseModal}
          position={selectedPosition}
        />
      )}
    </div>
  );
};

export default CareersPage;