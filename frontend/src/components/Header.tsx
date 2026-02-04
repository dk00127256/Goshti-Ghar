import React from 'react';
import { Link } from 'react-router-dom';
import { HomeIcon, PlusIcon } from '@heroicons/react/24/outline';

export const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-orange-400 to-pink-400 shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl">📚</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">गोष्टी घर</h1>
              <p className="text-orange-100 text-sm">मराठी कथा मुलांसाठी</p>
            </div>
          </Link>
          
          <nav className="flex items-center space-x-4">
            <Link
              to="/"
              className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors text-white"
            >
              <HomeIcon className="w-5 h-5" />
              <span>मुख्य पान</span>
            </Link>
            
            <Link
              to="/create"
              className="flex items-center space-x-2 px-4 py-2 bg-white hover:bg-orange-50 rounded-lg transition-colors text-orange-600 font-medium"
            >
              <PlusIcon className="w-5 h-5" />
              <span>नवीन गोष्ट</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};