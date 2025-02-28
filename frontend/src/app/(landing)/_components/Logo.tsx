import React from "react";
import Link from "next/link";
import Image from "next/image";

interface LogoProps {
  href?: string;
  className?: string;
  size?: "small" | "medium" | "large";
}

const sizeClasses = {
  small: {
    container: "w-8 h-8",
    image: "w-5 h-5",
    text: "text-lg"
  },
  medium: {
    container: "w-10 h-10",
    image: "w-6 h-6",
    text: "text-xl"
  },
  large: {
    container: "w-12 h-12",
    image: "w-7 h-7",
    text: "text-2xl"
  }
};

export const Logo: React.FC<LogoProps> = ({ 
  href = "/",
  className = "",
  size = "medium"
}) => {
  const sizes = sizeClasses[size];

  return (
    <div className={className}>
      <Link
        href={href}
        className="flex items-center gap-3 group"
      >
        {/* Logo Image Container */}
        <div 
          className={`relative flex items-center justify-center ${sizes.container} rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-600 shadow-sm overflow-hidden transition-all duration-300 group-hover:shadow-md group-hover:from-indigo-600 group-hover:to-indigo-700`}
          aria-hidden="true"
        >
          <div className="absolute inset-0 bg-black/5 dark:bg-white/5" />
          <Image
            src="/img/logo1.svg"
            alt="Linguify Logo"
            width={24}
            height={24}
            className={`${sizes.image} object-contain relative transition-transform duration-300 group-hover:scale-110`}
            priority
          />
        </div>
        
        {/* Brand Name */}
        <span 
          className={`${sizes.text} font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-200 bg-clip-text text-transparent transition-colors duration-300`}
        >
          Linguify
        </span>
      </Link>
    </div>
  );
};

export default Logo;