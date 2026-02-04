import React, { useState, useEffect } from 'react';
import './App.css';

interface AgeGroup {
  id: string;
  range: string;
  marathiRange: string;
  title: string;
  marathiTitle: string;
  description: string;
  marathiDescription: string;
  icon: string;
  color: string;
  bgGradient: string;
  features: string[];
  marathiFeatures: string[];
  storyLength: string;
  vocabulary: string;
}

interface NotificationState {
  show: boolean;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  marathiTitle?: string;
  marathiMessage?: string;
}

const ageGroups: AgeGroup[] = [
  {
    id: 'toddler',
    range: '2-4 Years',
    marathiRange: '२-४ वर्षे',
    title: 'Little Explorers',
    marathiTitle: 'छोटे अन्वेषक',
    description: 'Simple stories with basic concepts',
    marathiDescription: 'सोप्या संकल्पनांसह साध्या गोष्टी',
    icon: '🧸',
    color: 'emerald',
    bgGradient: 'from-emerald-400 to-teal-500',
    features: ['Simple words', 'Bright colors', 'Animal friends', 'Basic emotions'],
    marathiFeatures: ['सोपे शब्द', 'चमकदार रंग', 'प्राणी मित्र', 'मूलभूत भावना'],
    storyLength: '1-2 minutes',
    vocabulary: '50-100 words'
  },
  {
    id: 'preschool',
    range: '5-7 Years',
    marathiRange: '५-७ वर्षे',
    title: 'Young Learners',
    marathiTitle: 'तरुण शिकणारे',
    description: 'Educational stories with moral lessons',
    marathiDescription: 'नैतिक शिकवणीसह शैक्षणिक गोष्टी',
    icon: '🎨',
    color: 'blue',
    bgGradient: 'from-blue-400 to-indigo-500',
    features: ['Moral lessons', 'Problem solving', 'Friendship', 'School concepts'],
    marathiFeatures: ['नैतिक शिकवण', 'समस्या सोडवणे', 'मैत्री', 'शाळेच्या संकल्पना'],
    storyLength: '3-4 minutes',
    vocabulary: '150-250 words'
  },
  {
    id: 'elementary',
    range: '8-12 Years',
    marathiRange: '८-१२ वर्षे',
    title: 'Story Adventurers',
    marathiTitle: 'कथा साहसी',
    description: 'Complex narratives with life lessons',
    marathiDescription: 'जीवनाच्या धड्यांसह जटिल कथा',
    icon: '📚',
    color: 'purple',
    bgGradient: 'from-purple-400 to-pink-500',
    features: ['Complex plots', 'Character development', 'Cultural values', 'Critical thinking'],
    marathiFeatures: ['जटिल कथानक', 'पात्र विकास', 'सांस्कृतिक मूल्ये', 'गंभीर विचार'],
    storyLength: '5-7 minutes',
    vocabulary: '300-500 words'
  }
];

function App() {
  const [selectedAge, setSelectedAge] = useState<string>('');
  const [language, setLanguage] = useState<'en' | 'mr'>('mr');
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<NotificationState>({
    show: false,
    type: 'info',
    title: '',
    message: ''
  });

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'mr' : 'en');
    showNotification(
      'success',
      'Language Changed',
      `Switched to ${language === 'en' ? 'Marathi' : 'English'}`,
      'भाषा बदलली',
      `${language === 'en' ? 'मराठी' : 'इंग्रजी'} मध्ये बदलले`
    );
  };

  const showNotification = (
    type: 'success' | 'error' | 'info' | 'warning',
    title: string,
    message: string,
    marathiTitle?: string,
    marathiMessage?: string
  ) => {
    setNotification({
      show: true,
      type,
      title,
      message,
      marathiTitle,
      marathiMessage
    });
  };

  const handleCreateStory = () => {
    if (!selectedAge) {
      showNotification(
        'warning',
        'Please Select Age Group',
        'Choose an age group to create a personalized story',
        'कृपया वयोगट निवडा',
        'वैयक्तिकृत गोष्ट तयार करण्यासाठी वयोगट निवडा'
      );
      return;
    }

    setIsLoading(true);
    
    setTimeout(() => {
      setIsLoading(false);
      showNotification(
        'info',
        'Story Creation Started',
        'Your personalized Marathi story is being created...',
        'गोष्ट तयार करणे सुरू',
        'तुमची वैयक्तिकृत मराठी गोष्ट तयार केली जात आहे...'
      );
    }, 2000);
  };

  const handleViewSamples = () => {
    showNotification(
      'info',
      'Sample Stories',
      'Sample stories feature coming soon!',
      'नमुना गोष्टी',
      'नमुना गोष्टी वैशिष्ट्य लवकरच येत आहे!'
    );
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      showNotification(
        'success',
        'Welcome to Goshti Ghar!',
        'Create beautiful Marathi stories for your children',
        'गोष्टी घरात आपले स्वागत आहे!',
        'आपल्या मुलांसाठी सुंदर मराठी गोष्टी तयार करा'
      );
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  // Simple notification component
  const NotificationComponent = () => {
    if (!notification.show) return null;

    const typeStyles = {
      success: 'bg-green-500',
      error: 'bg-red-500', 
      info: 'bg-blue-500',
      warning: 'bg-yellow-500'
    };

    return (
      <div className="fixed top-4 right-4 z-50 bg-white rounded-lg shadow-lg p-4 max-w-sm border">
        <div className="flex items-start space-x-3">
          <div className={`w-6 h-6 ${typeStyles[notification.type]} rounded-full flex items-center justify-center text-white text-sm`}>
            {notification.type === 'success' ? '✓' : notification.type === 'error' ? '✗' : notification.type === 'warning' ? '!' : 'i'}
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-gray-800 text-sm">
              {language === 'mr' && notification.marathiTitle ? notification.marathiTitle : notification.title}
            </h4>
            <p className="text-gray-600 text-xs mt-1">
              {language === 'mr' && notification.marathiMessage ? notification.marathiMessage : notification.message}
            </p>
          </div>
          <button 
            onClick={() => setNotification(prev => ({ ...prev, show: false }))}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <NotificationComponent />

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center">
          <div className="bg-white rounded-3xl p-12 shadow-2xl">
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="w-12 h-12 animate-spin rounded-full border-4 border-gray-200 border-t-orange-500"></div>
              <p className="text-gray-600 font-medium animate-pulse">
                {language === 'mr' ? 'तुमची गोष्ट तयार करत आहे...' : 'Creating your story...'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-white/20 sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-400 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-2xl">📚</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-pink-600 bg-clip-text text-transparent">
                  {language === 'mr' ? 'गोष्टी घर' : 'Goshti Ghar'}
                </h1>
                <p className="text-sm text-gray-600">
                  {language === 'mr' ? 'मराठी कथा मुलांसाठी' : 'Marathi Stories for Kids'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleLanguage}
                className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-medium text-sm shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
              >
                {language === 'mr' ? 'English' : 'मराठी'}
              </button>
              
              <button 
                onClick={handleCreateStory}
                className="px-6 py-2 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-lg hover:from-orange-600 hover:to-pink-600 transition-all duration-200 font-medium shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
              >
                {language === 'mr' ? 'नवीन गोष्ट' : 'New Story'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-orange-100 to-pink-100 px-4 py-2 rounded-full mb-6 shadow-sm">
            <span className="text-orange-600 font-medium text-sm">
              {language === 'mr' ? '✨ AI द्वारे तयार केलेल्या गोष्टी' : '✨ AI-Generated Stories'}
            </span>
          </div>
          
          <h2 className="text-5xl md:text-6xl font-bold text-gray-800 mb-6 leading-tight">
            {language === 'mr' ? (
              <>
                आपल्या मुलासाठी<br />
                <span className="bg-gradient-to-r from-orange-600 to-pink-600 bg-clip-text text-transparent">
                  परफेक्ट गोष्ट
                </span>
              </>
            ) : (
              <>
                Perfect Stories<br />
                <span className="bg-gradient-to-r from-orange-600 to-pink-600 bg-clip-text text-transparent">
                  For Your Child
                </span>
              </>
            )}
          </h2>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            {language === 'mr' 
              ? 'वयानुसार तयार केलेल्या मराठी गोष्टी ज्या नैतिक मूल्ये शिकवतात आणि कल्पनाशक्ती वाढवतात'
              : 'Age-appropriate Marathi stories that teach moral values and spark imagination'
            }
          </p>
        </div>

        {/* Age Group Selection */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-800 mb-4">
            {language === 'mr' ? 'वयोगट निवडा' : 'Choose Age Group'}
          </h3>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            {language === 'mr' 
              ? 'आपल्या मुलाच्या वयानुसार योग्य गोष्ट निवडा'
              : 'Select the perfect story category for your child\'s age'
            }
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {ageGroups.map((group) => (
              <div
                key={group.id}
                className={`relative group cursor-pointer transition-all duration-300 ${
                  selectedAge === group.id 
                    ? 'scale-105 shadow-2xl' 
                    : 'hover:scale-102 hover:shadow-xl'
                }`}
                onClick={() => setSelectedAge(selectedAge === group.id ? '' : group.id)}
              >
                <div className="bg-white rounded-3xl p-8 shadow-lg border border-white/50 backdrop-blur-sm">
                  {/* Icon and Badge */}
                  <div className="flex items-center justify-between mb-6">
                    <div className={`w-16 h-16 bg-gradient-to-r ${group.bgGradient} rounded-2xl flex items-center justify-center text-3xl shadow-lg`}>
                      {group.icon}
                    </div>
                    <div className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                      {language === 'mr' ? group.marathiRange : group.range}
                    </div>
                  </div>
                  
                  {/* Title and Description */}
                  <h4 className="text-2xl font-bold text-gray-800 mb-3">
                    {language === 'mr' ? group.marathiTitle : group.title}
                  </h4>
                  <p className="text-gray-600 mb-6 leading-relaxed">
                    {language === 'mr' ? group.marathiDescription : group.description}
                  </p>
                  
                  {/* Features */}
                  <div className="space-y-3 mb-6">
                    {(language === 'mr' ? group.marathiFeatures : group.features).map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className={`w-2 h-2 bg-gradient-to-r ${group.bgGradient} rounded-full`}></div>
                        <span className="text-sm text-gray-700">{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4 pt-6 border-t border-gray-100">
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-800">{group.storyLength}</div>
                      <div className="text-xs text-gray-500">
                        {language === 'mr' ? 'कथेची लांबी' : 'Story Length'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-800">{group.vocabulary}</div>
                      <div className="text-xs text-gray-500">
                        {language === 'mr' ? 'शब्दसंग्रह' : 'Vocabulary'}
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection Indicator */}
                  {selectedAge === group.id && (
                    <div className={`absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r ${group.bgGradient} rounded-full flex items-center justify-center shadow-lg`}>
                      <span className="text-white text-sm">✓</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Section */}
        {selectedAge && (
          <div className="text-center bg-white/80 backdrop-blur-md rounded-3xl p-12 shadow-xl border border-white/50 max-w-4xl mx-auto">
            <div className="mb-8">
              <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-4xl">🎉</span>
              </div>
              <h3 className="text-3xl font-bold text-gray-800 mb-4">
                {language === 'mr' ? 'उत्तम निवड!' : 'Great Choice!'}
              </h3>
              <p className="text-gray-600 text-lg">
                {language === 'mr' 
                  ? `${ageGroups.find(g => g.id === selectedAge)?.marathiRange} वयोगटासाठी गोष्ट तयार करूया`
                  : `Let's create a story for ${ageGroups.find(g => g.id === selectedAge)?.range} age group`
                }
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={handleCreateStory}
                className="px-8 py-4 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-xl hover:from-orange-600 hover:to-pink-600 transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                {language === 'mr' ? '🎨 गोष्ट तयार करा' : '🎨 Create Story'}
              </button>
              <button 
                onClick={handleViewSamples}
                className="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl hover:from-indigo-600 hover:to-purple-600 transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                {language === 'mr' ? '📖 नमुना गोष्टी पहा' : '📖 View Sample Stories'}
              </button>
            </div>
          </div>
        )}

        {/* Features Section */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-8 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 hover:shadow-lg transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-3xl">🤖</span>
            </div>
            <h4 className="text-xl font-bold text-gray-800 mb-3">
              {language === 'mr' ? 'AI द्वारे तयार' : 'AI-Generated'}
            </h4>
            <p className="text-gray-600">
              {language === 'mr' 
                ? 'प्रत्येक गोष्ट आपल्या मुलासाठी खास तयार केली जाते'
                : 'Each story is uniquely crafted for your child'
              }
            </p>
          </div>
          
          <div className="text-center p-8 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 hover:shadow-lg transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-3xl">🎭</span>
            </div>
            <h4 className="text-xl font-bold text-gray-800 mb-3">
              {language === 'mr' ? 'व्हिडिओ गोष्टी' : 'Video Stories'}
            </h4>
            <p className="text-gray-600">
              {language === 'mr' 
                ? 'मराठी आवाज आणि सुंदर व्हिडिओसह'
                : 'With Marathi narration and beautiful visuals'
              }
            </p>
          </div>
          
          <div className="text-center p-8 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 hover:shadow-lg transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-3xl">💝</span>
            </div>
            <h4 className="text-xl font-bold text-gray-800 mb-3">
              {language === 'mr' ? 'नैतिक मूल्ये' : 'Moral Values'}
            </h4>
            <p className="text-gray-600">
              {language === 'mr' 
                ? 'प्रत्येक गोष्टीत जीवनाचे महत्वाचे धडे'
                : 'Important life lessons in every story'
              }
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;