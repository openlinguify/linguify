// Performance monitoring utilities
import { useRef, lazy } from 'react';
export const measurePerformance = (componentName: string) => {
  if (typeof window === 'undefined') return;
  
  const startTime = performance.now();
  
  return () => {
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    if (duration > 100) {
      console.warn(`[Performance] ${componentName} took ${duration.toFixed(2)}ms to render`);
    }
  };
};

// Web Vitals tracking
export const trackWebVitals = () => {
  if (typeof window === 'undefined') return;
  
  // First Contentful Paint
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      console.log(`[Web Vitals] ${entry.name}: ${entry.startTime.toFixed(2)}ms`);
    }
  });
  
  observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
};

// Component render counter for debugging
export const useRenderCount = (componentName: string) => {
  const renderCount = useRef(0);
  renderCount.current += 1;
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Render] ${componentName} rendered ${renderCount.current} times`);
  }
};

// Bundle size analyzer helper
export const analyzeBundle = async () => {
  if (process.env.NODE_ENV === 'production') return;
  
  const moduleInfo = {
    totalSize: 0,
    modules: []
  };
  
  // This would be connected to webpack-bundle-analyzer
  console.log('[Bundle] Analysis:', moduleInfo);
};

// Lazy loading with prefetch
export const lazyWithPrefetch = (importFunc: () => Promise<any>) => {
  const Component = lazy(importFunc);
  
  // Prefetch on hover or when idle
  const prefetch = () => {
    importFunc();
  };
  
  return { Component, prefetch };
};