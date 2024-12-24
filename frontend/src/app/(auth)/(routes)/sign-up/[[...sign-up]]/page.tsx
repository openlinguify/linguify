"use client";

import { SignUp } from "@clerk/nextjs";
import { UserResource } from "@clerk/types";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { GlobeIcon, BookOpen, Languages } from "lucide-react";

export default function SignUpPage() {
  const router = useRouter();
  const [languageLevel, setLanguageLevel] = useState<string>("A1");
  const [targetLanguage, setTargetLanguage] = useState<string>("EN");

  const handleSignUpComplete = async (user: UserResource) => {
    try {
      // Utilisation de setMetadata au lieu de update
      await user.setMetadata({
        language_level: languageLevel,
        target_language: targetLanguage,
      });
      router.push("/dashboard");
    } catch (error) {
      console.error("Error updating metadata:", error);
    }
  };

  const languageLevels = [
    { value: "A1", label: "Beginner", description: "Basic phrases and expressions" },
    { value: "A2", label: "Elementary", description: "Simple daily communication" },
    { value: "B1", label: "Intermediate", description: "Clear standard input on familiar matters" },
    { value: "B2", label: "Upper Intermediate", description: "Complex technical discussions" },
    { value: "C1", label: "Advanced", description: "Express fluently and spontaneously" },
    { value: "C2", label: "Proficiency", description: "Near native-level mastery" }
  ];

  const targetLanguages = [
    { code: "EN", name: "English", flag: "🇬🇧" },
    { code: "FR", name: "French", flag: "🇫🇷" },
    { code: "ES", name: "Spanish", flag: "🇪🇸" },
    { code: "DE", name: "German", flag: "🇩🇪" },
    { code: "IT", name: "Italian", flag: "🇮🇹" },
    { code: "NL", name: "Dutch", flag: "🇳🇱" },
    { code: "PT", name: "Portuguese", flag: "🇵🇹" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <GlobeIcon className="h-8 w-8 text-sky-500" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                Welcome to Linguify
              </h1>
            </div>
            <p className="text-gray-600 max-w-md mx-auto">
              Join our community of language learners and start your journey to fluency today
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Left Column - Clerk SignUp */}
            <div className="bg-white p-6 rounded-xl shadow-md">
              <SignUp
                appearance={{
                  elements: {
                    formButtonPrimary: 
                      "bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-white font-medium rounded-lg px-4 py-2 transition-all duration-200 shadow-md hover:shadow-lg",
                    formFieldInput:
                      "w-full rounded-lg border-gray-300 focus:ring-sky-500 focus:border-sky-500 transition-colors duration-200",
                    formFieldLabel: "text-gray-700 font-medium",
                    formFieldError: "text-red-500 text-sm mt-1",
                    card: "border-0 shadow-none",
                  },
                }}
                afterSignUpUrl="/dashboard"
                signInUrl="/sign-in"
              />
            </div>

            {/* Right Column - Language Preferences */}
            <div className="space-y-6">
              {/* Language Level Selection */}
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="flex items-center gap-2 mb-4">
                  <BookOpen className="h-5 w-5 text-sky-500" />
                  <h2 className="text-lg font-semibold text-gray-900">Your Language Level</h2>
                </div>
                <div className="space-y-4">
                  {languageLevels.map((level) => (
                    <label
                      key={level.value}
                      className={`flex items-start p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                        languageLevel === level.value
                          ? "bg-sky-50 border-2 border-sky-500"
                          : "border-2 border-gray-100 hover:border-sky-200"
                      }`}
                    >
                      <input
                        type="radio"
                        name="languageLevel"
                        value={level.value}
                        checked={languageLevel === level.value}
                        onChange={(e) => setLanguageLevel(e.target.value)}
                        className="mt-1"
                      />
                      <div className="ml-3">
                        <div className="font-medium text-gray-900">{level.label}</div>
                        <div className="text-sm text-gray-500">{level.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Target Language Selection */}
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="flex items-center gap-2 mb-4">
                  <Languages className="h-5 w-5 text-sky-500" />
                  <h2 className="text-lg font-semibold text-gray-900">Target Language</h2>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {targetLanguages.map((language) => (
                    <label
                      key={language.code}
                      className={`flex items-center p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                        targetLanguage === language.code
                          ? "bg-sky-50 border-2 border-sky-500"
                          : "border-2 border-gray-100 hover:border-sky-200"
                      }`}
                    >
                      <input
                        type="radio"
                        name="targetLanguage"
                        value={language.code}
                        checked={targetLanguage === language.code}
                        onChange={(e) => setTargetLanguage(e.target.value)}
                        className="hidden"
                      />
                      <span className="text-2xl mr-2">{language.flag}</span>
                      <span className="font-medium text-gray-900">{language.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}