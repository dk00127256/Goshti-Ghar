import React, { useEffect, useState } from 'react';

interface NotificationProps {
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  marathiTitle?: string;
  marathiMessage?: string;
  language?: 'en' | 'mr';
  duration?: number;
  onClose?: () => void;
}

export const Notification: React.FC<NotificationProps> = ({
  type,
  title,
  message,
  marathiTitle,
  marathiMessage,
  language = 'mr',
  duration = 5000,
  onClose
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose?.(), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const typeStyles = {
    success: {
      bg: 'bg-gradient-to-r from-green-500 to-emerald-500',
      icon: '✅',
      border: 'border-green-200'
    },
    error: {
      bg: 'bg-gradient-to-r from-red-500 to-pink-500',
      icon: '❌',
      border: 'border-red-200'
    },
    info: {
      bg: 'bg-gradient-to-r from-blue-500 to-indigo-500',
      icon: 'ℹ️',
      border: 'border-blue-200'
    },
    warning: {
      bg: 'bg-gradient-to-r from-yellow-500 to-orange-500',
      icon: '⚠️',
      border: 'border-yellow-200'
    }
  };

  const currentStyle = typeStyles[type];

  return (
    <div className={`fixed top-4 right-4 z-50 transition-all duration-300 transform ${
      isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
    }`}>
      <div className={`bg-white rounded-2xl shadow-2xl border ${currentStyle.border} p-6 max-w-sm backdrop-blur-md`}>
        <div className="flex items-start space-x-4">
          <div className={`w-10 h-10 ${currentStyle.bg} rounded-xl flex items-center justify-center text-white shadow-lg`}>
            <span className="text-lg">{currentStyle.icon}</span>
          </div>
          
          <div className="flex-1">
            <h4 className="font-bold text-gray-800 mb-1">
              {language === 'mr' && marathiTitle ? marathiTitle : title}
            </h4>
            <p className="text-gray-600 text-sm leading-relaxed">
              {language === 'mr' && marathiMessage ? marathiMessage : message}
            </p>
          </div>
          
          <button
            onClick={() => {
              setIsVisible(false);
              setTimeout(() => onClose?.(), 300);
            }}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <span className="text-xl">×</span>
          </button>
        </div>
      </div>
    </div>
  );
};