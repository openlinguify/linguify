'use client';
import React, { useState } from 'react';
import { Container } from "../_components/Container";
import { Check, X } from "lucide-react";

export default function Pricing() {
    const [isAnnual, setIsAnnual] = useState(false);

    const plans = [
        {
            name: "Free",
            description: "Perfect for getting started with language learning",
            price: {
                monthly: 0,
                annually: 0
            },
            features: [
                {
                    included: true,
                    text: "Access to basic learning modules",
                    tooltip: "Learn fundamentals in your chosen language"
                },
                {
                    included: true,
                    text: "Core vocabulary exercises",
                    tooltip: "Practice essential words and phrases"
                },
                {
                    included: true,
                    text: "Basic progress tracking",
                    tooltip: "Monitor your learning journey"
                },
                {
                    included: true,
                    text: "Limited practice exercises",
                    tooltip: "Access to beginner-level exercises"
                },
                {
                    included: true,
                    text: "Community forum access",
                    tooltip: "Connect with fellow learners"
                },
                {
                    included: false,
                    text: "Live tutoring sessions",
                    tooltip: "One-on-one sessions with native speakers"
                },
                {
                    included: false,
                    text: "Advanced analytics",
                    tooltip: "Detailed insights into your learning"
                },
                {
                    included: false,
                    text: "Offline access",
                    tooltip: "Learn without internet connection"
                }
            ]
        },
        {
            name: "Premium",
            description: "Full access to all Linguify features",
            price: {
                monthly: 15,
                annually: 150
            },
            features: [
                {
                    included: true,
                    text: "All Free features",
                    tooltip: "Everything in the Free plan"
                },
                {
                    included: true,
                    text: "Unlimited language courses",
                    tooltip: "Learn multiple languages simultaneously"
                },
                {
                    included: true,
                    text: "Live tutoring sessions",
                    tooltip: "Weekly sessions with native speakers"
                },
                {
                    included: true,
                    text: "Advanced progress analytics",
                    tooltip: "Detailed insights and recommendations"
                },
                {
                    included: true,
                    text: "Personalized learning path",
                    tooltip: "AI-powered custom curriculum"
                },
                {
                    included: true,
                    text: "Offline mode",
                    tooltip: "Learn anywhere, anytime"
                },
                {
                    included: true,
                    text: "Priority support",
                    tooltip: "24/7 dedicated assistance"
                },
                {
                    included: true,
                    text: "Certificate of completion",
                    tooltip: "Official certification for completed courses"
                }
            ],
            popular: true
        }
    ];

    return (
        <Container>
            <div className="flex flex-col items-center justify-center w-full max-w-6xl mx-auto py-12">
                {/* Header Section */}
                <div className="text-center mb-16">
                    <p className="text-base font-semibold text-indigo-600 dark:text-indigo-400 mb-2">
                        Pricing Plans
                    </p>
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white lg:text-5xl mb-4">
                        Choose Your Learning Journey
                    </h1>
                    <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                        Start for free and upgrade when you're ready to unlock all features
                    </p>
                </div>

                {/* Billing Toggle */}
                <div className="flex items-center gap-3 mb-12 bg-gray-50 dark:bg-gray-800 p-2 rounded-full">
                    <button
                        className={`px-4 py-2 rounded-full transition-all ${!isAnnual
                                ? 'bg-white dark:bg-gray-700 shadow-sm text-indigo-600 dark:text-white'
                                : 'text-gray-600 dark:text-gray-400'
                            }`}
                        onClick={() => setIsAnnual(false)}
                    >
                        Monthly
                    </button>
                    <button
                        className={`px-4 py-2 rounded-full transition-all ${isAnnual
                                ? 'bg-white dark:bg-gray-700 shadow-sm text-indigo-600 dark:text-white'
                                : 'text-gray-600 dark:text-gray-400'
                            }`}
                        onClick={() => setIsAnnual(true)}
                    >
                        Annually
                        <span className="ml-2 inline-block bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-xs px-2 py-0.5 rounded-full">
                            Save 17%
                        </span>
                    </button>
                </div>

                {/* Pricing Cards */}
                <div className="grid md:grid-cols-2 gap-8 w-full max-w-5xl">
                    {plans.map((plan) => (
                        <div
                            key={plan.name}
                            className={`relative flex flex-col p-8 bg-white dark:bg-gray-800 rounded-xl ${plan.popular
                                    ? 'border-2 border-indigo-600 shadow-xl'
                                    : 'border border-gray-200 dark:border-gray-700'
                                }`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-5 left-0 w-full flex justify-center">
                                    <span className="inline-block bg-indigo-600 text-white text-sm font-semibold px-4 py-1 rounded-full shadow-lg">
                                        Most Popular
                                    </span>
                                </div>
                            )}

                            <div className="mb-6">
                                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {plan.name}
                                </h3>
                                <p className="text-gray-600 dark:text-gray-400 mt-2">
                                    {plan.description}
                                </p>
                            </div>

                            <div className="mb-8">
                                <div className="flex items-end">
                                    <span className="text-5xl font-bold text-gray-900 dark:text-white">
                                        €{isAnnual ? plan.price.annually : plan.price.monthly}
                                    </span>
                                    {plan.price.monthly > 0 && (
                                        <span className="text-gray-600 dark:text-gray-400 ml-2 mb-2">
                                            /{isAnnual ? 'year' : 'month'}
                                        </span>
                                    )}
                                </div>
                                {plan.popular && isAnnual && (
                                    <p className="text-sm text-green-600 dark:text-green-400 mt-2">
                                        €12.50/month billed annually
                                    </p>
                                )}
                            </div>

                            <div className="space-y-4 mb-8 flex-grow">
                                {plan.features.map((feature, index) => (
                                    <div
                                        key={index}
                                        className="flex items-start gap-3 group relative"
                                        title={feature.tooltip}
                                    >
                                        {feature.included ? (
                                            <Check className="w-5 h-5 text-green-500" />


                                        ) : (
                                            <X className="w-5 h-5 text-red-500" />)}
                                        <span className={`${feature.included
                                                ? 'text-gray-600 dark:text-gray-300'
                                                : 'text-gray-400 dark:text-gray-500'
                                            }`}>
                                            {feature.text}
                                        </span>

                                        {/* Tooltip */}
                                        <div className="absolute left-0 -top-2 w-48 invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-all bg-gray-900 text-white text-sm rounded p-2 -translate-y-full ml-8">
                                            {feature.tooltip}
                                            <div className="absolute left-0 top-full w-2 h-2 bg-gray-900 transform rotate-45 translate-x-6 -translate-y-1"></div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <button
                                className={`w-full py-4 px-6 rounded-lg font-semibold transition-all transform hover:scale-[1.02] ${plan.popular
                                        ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/30'
                                        : 'bg-gray-100 hover:bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600'
                                    }`}
                            >
                                {plan.price.monthly === 0 ? 'Get Started Free' : 'Get Premium Access'}
                            </button>
                        </div>
                    ))}
                </div>

                {/* FAQ Section */}
                <div className="mt-20 text-center">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                        Common Questions
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 space-x-1">
                        <span>Need more info?</span>
                        <a href="/faq" className="text-indigo-600 hover:text-indigo-500 underline">
                            Visit our FAQ
                        </a>
                        <span>or</span>
                        <a href="/contact" className="text-indigo-600 hover:text-indigo-500 underline">
                            contact our team
                        </a>
                    </p>
                </div>
            </div>
        </Container>
    );
}