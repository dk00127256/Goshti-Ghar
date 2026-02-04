import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  marathiText?: string;
  language?: 'en' | 'mr';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  text = 'Loading...',
  marathiText = 'लोड होत आहे...',
  language = 'mr'
}) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative">
        <div className={`${sizeClasses[size]} animate-spin rounded-full border-4 border-gray-200`}>
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-orange-500 border-r-pink-500"></div>
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-gradient-to-r from-orange-400 to-pink-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      {(text || marathiText) && (
        <p className="text-gray-600 font-medium animate-pulse">
          {language === 'mr' ? marathiText : text}
        </p>
      )}
    </div>
  );
};