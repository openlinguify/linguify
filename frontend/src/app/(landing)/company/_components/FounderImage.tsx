'use client';

import React from 'react';

interface FounderImageProps {
  src: string;
  alt: string;
}

export default function FounderImage({ src, alt }: FounderImageProps) {
  return (
    <img 
      src={src} 
      alt={alt} 
      className="h-full w-full object-cover"
      onError={(e) => {
        e.currentTarget.src = "https://via.placeholder.com/300x400?text=Photo";
      }}
    />
  );
}