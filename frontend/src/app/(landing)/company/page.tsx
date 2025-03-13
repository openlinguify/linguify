import React from "react";
import {
  Globe,
  GraduationCap,
  Users,
  Heart
} from "lucide-react";
import FounderImage from "./_components/FounderImage";
import LanguageSwitcher from '../_components/LanguageSwitcher';

export default function Company() {
  const values = [
    {
      title: "Global Impact",
      description: "Breaking down language barriers to foster international understanding and cooperation.",
      icon: <Globe className="w-6 h-6" />,
    },
    {
      title: "Educational Excellence",
      description: "Developing innovative tools that transform how people learn and teach languages.",
      icon: <GraduationCap className="w-6 h-6" />,
    },
    {
      title: "Community First",
      description: "Building a supportive global community of learners and educators.",
      icon: <Users className="w-6 h-6" />,
    },
    {
      title: "Social Responsibility",
      description: "Promoting education accessibility and professional growth worldwide.",
      icon: <Heart className="w-6 h-6" />,
    }
  ];

  const founders = [
    {
      name: "Louis-Philippe Lalou",
      role: "Founder & CEO",
      image: "/landing/img/louis-philippe.jpg",
      bio: "Visionary entrepreneur passionate about leveraging technology to transform education globally."
    },
  ];

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-20">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white lg:text-5xl mb-6">
            Empowering Global Learning
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Next-Corporation proudly presents Linguify - our commitment to breaking down language barriers and fostering international understanding through innovative education technology.
          </p>
        </div>

        {/* Mission Section */}
        <div className="bg-indigo-50 dark:bg-gray-800 rounded-2xl p-12 mb-20">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Our Mission</h2>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              To revolutionize language education by developing accessible, effective tools that enhance learning and teaching experiences worldwide. We believe in the power of education to transform lives and create positive global change.
            </p>
          </div>
        </div>

        {/* Values Section */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">Our Values</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
                <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center mb-4">
                  <div className="text-indigo-600 dark:text-indigo-400">
                    {value.icon}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {value.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Our Story Section */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-6">Our Story</h2>
          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-sm">
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Founded in 2023 by Louis-Philippe Lalou and Lionel Hubaut, Linguify emerged from a shared vision to transform global education. As part of Next-Corporation, we identified the growing need for innovative language learning solutions that could bridge cultural gaps and create opportunities for people worldwide.
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              Our focus extends beyond just language learning - we're building tools that promote international cohesion, enhance employment opportunities, and contribute to a more connected global society. Through our platform, we're making quality language education accessible to everyone, everywhere.
            </p>
          </div>
        </div>

        {/* Founders Section */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">Our Founder</h2>
          <div className="grid grid-cols-1 gap-10 max-w-3xl mx-auto">
            {founders.map((founder, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden flex flex-col md:flex-row">
                <div className="md:w-1/3">
                  <FounderImage src={founder.image} alt={founder.name} />
                </div>
                <div className="p-6 md:w-2/3">
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{founder.name}</h3>
                  <p className="text-indigo-600 dark:text-indigo-400 font-semibold mb-4">{founder.role}</p>
                  <p className="text-gray-600 dark:text-gray-400">{founder.bio}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* Language Switcher (desktop only) */}
      <div className="fixed bottom-6 right-6 hidden md:block z-10">
        <LanguageSwitcher
          variant="dropdown"
          size="sm"
          className="shadow-md"
        />
      </div>
    </div>
  );
}