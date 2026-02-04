import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { VideoPlayer } from '../components/VideoPlayer';
import { 
  ArrowLeftIcon, 
  HeartIcon, 
  ShareIcon,
  BookOpenIcon,
  UserGroupIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

interface Story {
  id: string;
  title: string;
  content: string;
  moral: string;
  ageGroup: string;
  theme: string;
  videoUrl?: string;
  duration?: number;
  characters?: string[];
  setting?: string;
  ageAppropriateWords?: string[];
  createdAt?: string;
}

export const StoryPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isFavorite, setIsFavorite] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);

  useEffect(() => {
    if (id) {
      fetchStory(id);
    }
  }, [id]);

  const fetchStory = async (storyId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/stories/${storyId}`);
      
      if (!response.ok) {
        throw new Error('गोष्ट सापडली नाही');
      }
      
      const storyData = await response.json();
      setStory(storyData);
      
      // Check if story is in favorites (from localStorage)
      const favorites = JSON.parse(localStorage.getItem('favoriteStories') || '[]');
      setIsFavorite(favorites.includes(storyId));
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'काहीतरी चूक झाली');
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = () => {
    if (!story) return;
    
    const favorites = JSON.parse(localStorage.getItem('favoriteStories') || '[]');
    let newFavorites;
    
    if (isFavorite) {
      newFavorites = favorites.filter((fav: string) => fav !== story.id);
    } else {
      newFavorites = [...favorites, story.id];
    }
    
    localStorage.setItem('favoriteStories', JSON.stringify(newFavorites));
    setIsFavorite(!isFavorite);
  };

  const shareStory = async () => {
    if (!story) return;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: story.title,
          text: story.moral,
          url: window.location.href,
        });
      } catch (err) {
        console.log('Sharing cancelled');
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      alert('लिंक कॉपी झाली!');
    }
  };

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">गोष्ट लोड होत आहे...</p>
        </div>
      </div>
    );
  }

  if (error || !story) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <span className="text-4xl">😔</span>
        </div>
        <h2 className="text-xl font-semibold text-gray-800 mb-2">गोष्ट सापडली नाही</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={() => navigate('/')}
          className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg transition-colors"
        >
          मुख्य पानावर जा
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          <ArrowLeftIcon className="w-5 h-5" />
          <span>परत जा</span>
        </button>

        <div className="flex items-center space-x-2">
          <button
            onClick={toggleFavorite}
            className={`p-2 rounded-full transition-colors ${
              isFavorite 
                ? 'text-red-500 hover:text-red-600' 
                : 'text-gray-400 hover:text-red-500'
            }`}
          >
            {isFavorite ? (
              <HeartSolidIcon className="w-6 h-6" />
            ) : (
              <HeartIcon className="w-6 h-6" />
            )}
          </button>
          
          <button
            onClick={shareStory}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-full transition-colors"
          >
            <ShareIcon className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Story Info */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between mb-6">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-800 mb-3">{story.title}</h1>
            
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getAgeGroupColor(story.ageGroup)}`}>
                {story.ageGroup} वर्षे
              </span>
              
              <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm">
                {story.theme}
              </span>
              
              <div className="flex items-center space-x-1 text-gray-500 text-sm">
                <ClockIcon className="w-4 h-4" />
                <span>{formatDuration(story.duration)}</span>
              </div>
              
              {story.characters && story.characters.length > 0 && (
                <div className="flex items-center space-x-1 text-gray-500 text-sm">
                  <UserGroupIcon className="w-4 h-4" />
                  <span>{story.characters.length} पात्र</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Video Player */}
        {story.videoUrl && (
          <div className="mb-6">
            <VideoPlayer
              url={story.videoUrl}
              title={story.title}
              autoplay={true}
            />
          </div>
        )}

        {/* Story Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Moral */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border border-green-200">
            <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center">
              <span className="mr-2">💡</span>
              या गोष्टीतून काय शिकायला मिळते
            </h3>
            <p className="text-green-700 leading-relaxed">{story.moral}</p>
          </div>

          {/* Characters & Setting */}
          <div className="space-y-4">
            {story.characters && story.characters.length > 0 && (
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-200">
                <h4 className="font-semibold text-blue-800 mb-2">पात्र</h4>
                <div className="flex flex-wrap gap-2">
                  {story.characters.map((character, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm"
                    >
                      {character}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {story.setting && (
              <div className="bg-purple-50 p-4 rounded-xl border border-purple-200">
                <h4 className="font-semibold text-purple-800 mb-2">ठिकाण</h4>
                <p className="text-purple-700">{story.setting}</p>
              </div>
            )}

            {story.ageAppropriateWords && story.ageAppropriateWords.length > 0 && (
              <div className="bg-yellow-50 p-4 rounded-xl border border-yellow-200">
                <h4 className="font-semibold text-yellow-800 mb-2">नवीन शब्द</h4>
                <div className="flex flex-wrap gap-2">
                  {story.ageAppropriateWords.map((word, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-sm"
                    >
                      {word}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Story Transcript */}
        <div className="mt-6">
          <button
            onClick={() => setShowTranscript(!showTranscript)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors mb-4"
          >
            <BookOpenIcon className="w-5 h-5" />
            <span>{showTranscript ? 'गोष्ट लपवा' : 'संपूर्ण गोष्ट वाचा'}</span>
          </button>

          {showTranscript && (
            <div className="bg-gray-50 p-6 rounded-xl border">
              <div className="prose prose-lg max-w-none">
                {story.content.split('\n\n').map((paragraph, index) => (
                  <p key={index} className="mb-4 text-gray-700 leading-relaxed">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related Actions */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">आणखी काही करा</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/create')}
            className="flex items-center justify-center space-x-2 bg-gradient-to-r from-orange-400 to-pink-400 hover:from-orange-500 hover:to-pink-500 text-white font-medium py-3 px-6 rounded-lg transition-colors"
          >
            <span>आणखी एक गोष्ट तयार करा</span>
          </button>
          
          <button
            onClick={() => navigate('/')}
            className="flex items-center justify-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-lg transition-colors"
          >
            <span>इतर गोष्टी पहा</span>
          </button>
        </div>
      </div>
    </div>
  );
};