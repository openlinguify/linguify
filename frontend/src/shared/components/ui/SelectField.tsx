// src/app/
"use client";

import React from "react";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/shared/components/ui/select";

interface SelectFieldProps {
    label: string;
    placeholder: string;
    options: { value: string; label: string }[];
    value: string;
    onChange: (value: string) => void;
}

const SelectField: React.FC<SelectFieldProps> = ({
    label,
    placeholder,
    options,
    value,
    onChange,
}) => {
    return (
        <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-700">
                {label}
            </label>
            <Select onValueChange={onChange} value={value}>
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

export default SelectField;
