import React from 'react';
import { Link } from 'react-router-dom';
import { PlayIcon, ClockIcon, UserGroupIcon } from '@heroicons/react/24/outline';

interface StoryCardProps {
  id: string;
  title: string;
  moral: string;
  ageGroup: string;
  theme: string;
  duration?: number;
  thumbnail?: string;
  characters?: string[];
}

export const StoryCard: React.FC<StoryCardProps> = ({
  id,
  title,
  moral,
  ageGroup,
  theme,
  duration,
  thumbnail,
  characters = []
}) => {
  const formatDuration = (seconds?: number) => {
    if (!seconds) return '3 मिनिटे';
    const minutes = Math.floor(seconds / 60);
    return `${minutes} मिनिटे`;
  };

  const getAgeGroupColor = (age: string) => {
    switch (age) {
      case '2-4': return 'bg-green-100 text-green-800';
      case '5-7': return 'bg-blue-100 text-blue-800';
      case '8-12': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
      {/* Thumbnail */}
      <div className="relative h-48 bg-gradient-to-br from-orange-200 to-pink-200">
        {thumbnail ? (
          <img src={thumbnail} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-6xl">📖</span>
          </div>
        )}
        
        {/* Play button overlay */}
        <Link
          to={`/story/${id}`}
          className="absolute inset-0 flex items-center justify-center bg-black/20 hover:bg-black/30 transition-colors group"
        >
          <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
            <PlayIcon className="w-8 h-8 text-orange-500 ml-1" />
          </div>
        </Link>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-xl font-bold text-gray-800 line-clamp-2">{title}</h3>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getAgeGroupColor(ageGroup)}`}>
            {ageGroup} वर्षे
          </span>
        </div>

        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{moral}</p>

        {/* Metadata */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <ClockIcon className="w-4 h-4" />
              <span>{formatDuration(duration)}</span>
            </div>
            
            {characters.length > 0 && (
              <div className="flex items-center space-x-1">
                <UserGroupIcon className="w-4 h-4" />
                <span>{characters.length} पात्र</span>
              </div>
            )}
          </div>

          <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
            {theme}
          </span>
        </div>

        {/* Action button */}
        <Link
          to={`/story/${id}`}
          className="mt-4 w-full bg-gradient-to-r from-orange-400 to-pink-400 hover:from-orange-500 hover:to-pink-500 text-white font-medium py-2 px-4 rounded-lg transition-colors text-center block"
        >
          गोष्ट पहा
        </Link>
      </div>
    </div>
  );
};