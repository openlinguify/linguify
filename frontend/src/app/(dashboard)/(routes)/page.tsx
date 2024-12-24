"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { GlobeIcon, PlayCircle } from "lucide-react";

// Importation du Header
import Header from "@/app/(dashboard)/components/Header";

const SelectField = ({
    label,
    placeholder,
    options,
    value,
    onChange,
}: {
    label: string;
    placeholder: string;
    options: { value: string; label: string }[];
    value: string;
    onChange: (value: string) => void;
}) => {
    return (
        <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-700">
                {label}
            </label>
            <Select onValueChange={onChange}>
                <SelectTrigger className="w-full sm:w-[240px]">
                    <SelectValue placeholder={placeholder} />
                </SelectTrigger>
                <SelectContent>
                    <SelectGroup>
                        {options.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                                {option.label}
                            </SelectItem>
                        ))}
                    </SelectGroup>
                </SelectContent>
            </Select>
        </div>
    );
};

export default function Home() {
    const [level, setLevel] = useState("");
    const [language, setLanguage] = useState("en");

    const handleStart = () => {
        if (!level || !language) {
            alert("Please select both a language and a proficiency level.");
            return;
        }
        alert(`Starting ${language.toUpperCase()} at level ${level}`);
    };

    const levels = [
        { value: "A1", label: "A1 - Beginner" },
        { value: "A2", label: "A2 - Elementary" },
        { value: "B1", label: "B1 - Intermediate" },
        { value: "B2", label: "B2 - Upper Intermediate" },
        { value: "C1", label: "C1 - Advanced" },
        { value: "C2", label: "C2 - Mastery" },
    ];

    const languages = [
        { value: "en", label: "English" },
        { value: "fr", label: "French" },
        { value: "es", label: "Spanish" },
        { value: "de", label: "German" },
        { value: "nl", label: "Dutch" },
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Affichage du Header */}
            <Header />

            <div className="p-8">
                <Card className="max-w-2xl mx-auto">
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <GlobeIcon className="h-8 w-8 text-sky-500" />
                            <CardTitle className="text-4xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                                Linguify
                            </CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="bg-sky-50 p-4 rounded-lg border border-sky-100">
                            <p className="text-sky-800 font-medium">
                                Welcome to your personalized language learning journey!
                            </p>
                        </div>

                        <div className="space-y-4">
                            <SelectField
                                label="Select your target language"
                                placeholder="Choose a language"
                                options={languages}
                                value={language}
                                onChange={setLanguage}
                            />

                            <SelectField
                                label="Select your proficiency level"
                                placeholder="Choose your level"
                                options={levels}
                                value={level}
                                onChange={setLevel}
                            />
                        </div>

                        <div className="pt-4">
                            <Button
                                onClick={handleStart}
                                disabled={!level || !language}
                                className="w-full sm:w-auto bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <PlayCircle className="h-5 w-5 mr-2" />
                                Start Learning
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
