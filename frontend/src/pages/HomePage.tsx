import React, { useState, useEffect } from 'react';
import { StoryCard } from '../components/StoryCard';
import { useStories } from '../hooks/useStories';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';

export const HomePage: React.FC = () => {
  const { stories, loading, error, fetchStories } = useStories();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAgeGroup, setSelectedAgeGroup] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('');

  useEffect(() => {
    fetchStories();
  }, []);

  const filteredStories = stories.filter(story => {
    const matchesSearch = story.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         story.moral.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesAge = !selectedAgeGroup || story.ageGroup === selectedAgeGroup;
    const matchesTheme = !selectedTheme || story.theme === selectedTheme;
    
    return matchesSearch && matchesAge && matchesTheme;
  });

  const ageGroups = ['2-4', '5-7', '8-12'];
  const themes = ['मैत्री', 'प्रामाणिकता', 'धैर्य', 'दया', 'मदत', 'शिक्षण'];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">गोष्टी लोड होत आहेत...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <span className="text-4xl">😔</span>
        </div>
        <h2 className="text-xl font-semibold text-gray-800 mb-2">काहीतरी चूक झाली</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchStories}
          className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg transition-colors"
        >
          पुन्हा प्रयत्न करा
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12 bg-white rounded-2xl shadow-lg">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          गोष्टी घरात आपले स्वागत आहे! 🏠
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          मुलांसाठी सुंदर मराठी गोष्टी. नैतिक शिकवणी आणि मनोरंजनाने भरपूर!
        </p>
        
        {/* Age Group Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {ageGroups.map((age) => (
            <div
              key={age}
              className="bg-gradient-to-br from-orange-100 to-pink-100 p-6 rounded-xl hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedAgeGroup(age === selectedAgeGroup ? '' : age)}
            >
              <div className="text-3xl mb-2">
                {age === '2-4' ? '🧸' : age === '5-7' ? '🎨' : '📚'}
              </div>
              <h3 className="font-semibold text-gray-800">{age} वर्षे</h3>
              <p className="text-sm text-gray-600 mt-1">
                {age === '2-4' ? 'सोप्या गोष्टी' : 
                 age === '5-7' ? 'मध्यम गोष्टी' : 'विस्तृत गोष्टी'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="गोष्ट शोधा..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>

          {/* Age Filter */}
          <select
            value={selectedAgeGroup}
            onChange={(e) => setSelectedAgeGroup(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          >
            <option value="">सर्व वयोगट</option>
            {ageGroups.map((age) => (
              <option key={age} value={age}>{age} वर्षे</option>
            ))}
          </select>

          {/* Theme Filter */}
          <select
            value={selectedTheme}
            onChange={(e) => setSelectedTheme(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          >
            <option value="">सर्व विषय</option>
            {themes.map((theme) => (
              <option key={theme} value={theme}>{theme}</option>
            ))}
          </select>
        </div>

        {/* Active Filters */}
        {(selectedAgeGroup || selectedTheme || searchTerm) && (
          <div className="mt-4 flex flex-wrap gap-2">
            {searchTerm && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                शोध: "{searchTerm}"
                <button
                  onClick={() => setSearchTerm('')}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            )}
            {selectedAgeGroup && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
                {selectedAgeGroup} वर्षे
                <button
                  onClick={() => setSelectedAgeGroup('')}
                  className="ml-2 text-green-600 hover:text-green-800"
                >
                  ×
                </button>
              </span>
            )}
            {selectedTheme && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800">
                {selectedTheme}
                <button
                  onClick={() => setSelectedTheme('')}
                  className="ml-2 text-purple-600 hover:text-purple-800"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Stories Grid */}
      {filteredStories.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredStories.map((story) => (
            <StoryCard
              key={story.id}
              id={story.id}
              title={story.title}
              moral={story.moral}
              ageGroup={story.ageGroup}
              theme={story.theme}
              duration={story.duration}
              characters={story.characters}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <span className="text-6xl">📚</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-600 mb-2">
            {stories.length === 0 ? 'अजून गोष्टी नाहीत' : 'कोणत्या गोष्टी सापडल्या नाहीत'}
          </h3>
          <p className="text-gray-500 mb-6">
            {stories.length === 0 
              ? 'नवीन गोष्ट तयार करा किंवा थोडा वेळ थांबा'
              : 'वेगळे शब्द वापरून शोधा किंवा फिल्टर बदला'
            }
          </p>
          {stories.length === 0 && (
            <button
              onClick={() => window.location.href = '/create'}
              className="bg-gradient-to-r from-orange-400 to-pink-400 hover:from-orange-500 hover:to-pink-500 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              पहिली गोष्ट तयार करा
            </button>
          )}
        </div>
      )}
    </div>
  );
};