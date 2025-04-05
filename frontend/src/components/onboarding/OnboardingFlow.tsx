// src/components/onboarding/OnboardingFlow.tsx
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle, 
  Globe, 
  BookOpen, 
  User
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/components/ui/use-toast";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  LANGUAGE_OPTIONS,
  LEVEL_OPTIONS,
  OBJECTIVES_OPTIONS
} from "@/constants/usersettings";
import apiClient from "@/core/api/apiClient";
import { useAuthContext } from "@/core/auth/AuthProvider";

interface OnboardingFlowProps {
  onComplete: () => void;
}

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const { toast } = useToast();
  const { user } = useAuthContext();
  const [step, setStep] = useState(1);
  const totalSteps = 5;
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Form data state
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    username: "",
    bio: "",
    native_language: "",
    target_language: "",
    language_level: "A1",
    objectives: "Travel",
  });

  // Load initial data from user if available
  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        first_name: user.first_name || prev.first_name,
        last_name: user.last_name || prev.last_name,
        username: user.username || prev.username,
        bio: user.bio || prev.bio,
        native_language: user.native_language || prev.native_language,
        target_language: user.target_language || prev.target_language,
        language_level: user.language_level || prev.language_level,
        objectives: user.objectives || prev.objectives,
      }));
    }
  }, [user]);

  // Handle form submission
  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Make API call to update the user's profile
      await apiClient.patch('/api/auth/profile/', formData);
      
      // Show success toast
      toast({
        title: "Profile updated successfully!",
        description: "Your language learning journey begins now.",
        variant: "default",
      });
      
      // Set onboarding as completed in localStorage
      localStorage.setItem("onboardingCompleted", "true");
      
      // Call the onComplete callback to finish the onboarding process
      onComplete();
    } catch (error) {
      console.error("Error updating profile:", error);
      toast({
        title: "Error updating profile",
        description: "There was an error saving your information. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle input changes
  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Navigate to next step
  const nextStep = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      handleSubmit();
    }
  };

  // Navigate to previous step
  const prevStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  // Skip the entire onboarding
  const skipOnboarding = () => {
    // Set default values and submit
    localStorage.setItem("onboardingCompleted", "true");
    onComplete();
  };

  // Animation variants
  const pageVariants = {
    initial: {
      opacity: 0,
      x: 100,
    },
    in: {
      opacity: 1,
      x: 0,
    },
    out: {
      opacity: 0,
      x: -100,
    },
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div 
        className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-2xl overflow-hidden"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header with progress */}
        <div className="bg-gradient-to-r from-violet-500 to-purple-600 p-6 text-white">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Welcome to Linguify</h2>
            <Button variant="ghost" onClick={skipOnboarding} className="text-white hover:text-white/80">
              Skip
            </Button>
          </div>
          <Progress value={(step / totalSteps) * 100} className="h-2 bg-white/30" />
          <div className="flex justify-between text-xs mt-2">
            <span>Step {step} of {totalSteps}</span>
            <span>{Math.round((step / totalSteps) * 100)}% Complete</span>
          </div>
        </div>

        {/* Content area */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={{ duration: 0.3 }}
              className="min-h-[350px] flex flex-col"
            >
              {/* Step 1: Welcome */}
              {step === 1 && (
                <div className="flex flex-col items-center text-center space-y-6 flex-grow justify-center">
                  <div className="bg-indigo-100 dark:bg-indigo-900/50 p-4 rounded-full">
                    <Globe className="h-12 w-12 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <h3 className="text-2xl font-bold">Welcome to Linguify!</h3>
                  <p className="text-gray-600 dark:text-gray-400 max-w-md">
                    Let's set up your profile and language preferences to customize your learning experience.
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">
                    This will only take 2 minutes to complete.
                  </p>
                </div>
              )}

              {/* Step 2: Personal Information */}
              {step === 2 && (
                <div className="space-y-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <User className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
                    <h3 className="text-xl font-bold">Tell us about yourself</h3>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">First Name</Label>
                      <Input 
                        id="first_name"
                        placeholder="Your first name"
                        value={formData.first_name}
                        onChange={(e) => handleInputChange("first_name", e.target.value)}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="last_name">Last Name</Label>
                      <Input 
                        id="last_name"
                        placeholder="Your last name"
                        value={formData.last_name}
                        onChange={(e) => handleInputChange("last_name", e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input 
                      id="username"
                      placeholder="Choose a username"
                      value={formData.username}
                      onChange={(e) => handleInputChange("username", e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="bio">Bio (Optional)</Label>
                    <Textarea 
                      id="bio"
                      placeholder="Tell us a bit about yourself..."
                      value={formData.bio}
                      onChange={(e) => handleInputChange("bio", e.target.value)}
                      rows={3}
                    />
                  </div>
                </div>
              )}

              {/* Step 3: Language Selection */}
              {step === 3 && (
                <div className="space-y-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <Globe className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
                    <h3 className="text-xl font-bold">Your languages</h3>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="native_language">Native Language</Label>
                      <Select
                        value={formData.native_language}
                        onValueChange={(value) => handleInputChange("native_language", value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select your native language" />
                        </SelectTrigger>
                        <SelectContent>
                          {LANGUAGE_OPTIONS.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="target_language">Language You Want to Learn</Label>
                      <Select
                        value={formData.target_language}
                        onValueChange={(value) => handleInputChange("target_language", value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select a language to learn" />
                        </SelectTrigger>
                        <SelectContent>
                          {LANGUAGE_OPTIONS.map((option) => (
                            <SelectItem 
                              key={option.value} 
                              value={option.value}
                              disabled={option.value === formData.native_language}
                            >
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {formData.native_language === formData.target_language && (
                        <p className="text-sm text-red-500 mt-1">
                          Your learning language must be different from your native language.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Learning Preferences */}
              {step === 4 && (
                <div className="space-y-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <BookOpen className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
                    <h3 className="text-xl font-bold">Learning preferences</h3>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="language_level">Your Current Level</Label>
                      <Select
                        value={formData.language_level}
                        onValueChange={(value) => handleInputChange("language_level", value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select your current level" />
                        </SelectTrigger>
                        <SelectContent>
                          {LEVEL_OPTIONS.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="objectives">Learning Objectives</Label>
                      <Select
                        value={formData.objectives}
                        onValueChange={(value) => handleInputChange("objectives", value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select your objectives" />
                        </SelectTrigger>
                        <SelectContent>
                          {OBJECTIVES_OPTIONS.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Completion */}
              {step === 5 && (
                <div className="flex flex-col items-center text-center space-y-6 flex-grow justify-center">
                  <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded-full">
                    <CheckCircle className="h-12 w-12 text-green-600 dark:text-green-500" />
                  </div>
                  <h3 className="text-2xl font-bold">You're all set!</h3>
                  <p className="text-gray-600 dark:text-gray-400 max-w-md">
                    Your profile has been configured. Now you can start your language learning journey with Linguify.
                  </p>
                  
                  <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-lg w-full max-w-md">
                    <h4 className="font-medium text-indigo-700 dark:text-indigo-400 mb-2">
                      Your Learning Path
                    </h4>
                    <ul className="space-y-2 text-left text-gray-700 dark:text-gray-300">
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span>Learning {LANGUAGE_OPTIONS.find(l => l.value === formData.target_language)?.label} from {LANGUAGE_OPTIONS.find(l => l.value === formData.native_language)?.label}</span>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span>Starting at {LEVEL_OPTIONS.find(l => l.value === formData.language_level)?.label} level</span>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span>Focus on {OBJECTIVES_OPTIONS.find(o => o.value === formData.objectives)?.label}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation buttons */}
        <div className="border-t border-gray-200 dark:border-gray-800 p-6 flex justify-between">
          <Button
            variant="outline"
            onClick={prevStep}
            disabled={step === 1}
            className={step === 1 ? "invisible" : ""}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          
          <Button 
            onClick={nextStep}
            disabled={
              isSubmitting || 
              (step === 3 && (
                !formData.native_language || 
                !formData.target_language ||
                formData.native_language === formData.target_language
              ))
            }
          >
            {step === totalSteps ? (
              isSubmitting ? (
                <>
                  <span className="animate-spin mr-2">●</span>
                  Setting Up...
                </>
              ) : (
                "Get Started"
              )
            ) : (
              <>
                Next
                <ArrowRight className="h-4 w-4 ml-2" />
              </>
            )}
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default OnboardingFlow;