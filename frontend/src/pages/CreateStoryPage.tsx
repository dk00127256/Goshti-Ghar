import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SparklesIcon, ClockIcon } from '@heroicons/react/24/outline';

interface StoryForm {
  ageGroup: string;
  theme: string;
  moralType: string;
}

export const CreateStoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState<StoryForm>({
    ageGroup: '',
    theme: '',
    moralType: 'kindness'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const ageGroups = [
    { value: '2-4', label: '2-4 वर्षे', description: 'सोप्या शब्दांत, छोटी गोष्ट' },
    { value: '5-7', label: '5-7 वर्षे', description: 'मध्यम शब्दांत, रंगीत गोष्ट' },
    { value: '8-12', label: '8-12 वर्षे', description: 'विस्तृत शब्दांत, शिकवणीची गोष्ट' }
  ];

  const themes = [
    'मैत्री', 'प्रामाणिकता', 'धैर्य', 'दया', 'मदत', 'शिक्षण',
    'कुटुंब', 'निसर्ग', 'साहस', 'कृतज्ञता', 'सहकार्य', 'न्याय'
  ];

  const moralTypes = [
    { value: 'kindness', label: 'दयाळूपणा' },
    { value: 'honesty', label: 'प्रामाणिकता' },
    { value: 'courage', label: 'धैर्य' },
    { value: 'friendship', label: 'मैत्री' },
    { value: 'helping', label: 'मदत करणे' },
    { value: 'respect', label: 'आदर' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!form.ageGroup || !form.theme) {
      setError('कृपया सर्व आवश्यक माहिती भरा');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/stories/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age_group: form.ageGroup,
          theme: form.theme,
          moral_type: form.moralType
        }),
      });

      if (!response.ok) {
        throw new Error('गोष्ट तयार करताना समस्या आली');
      }

      const story = await response.json();
      navigate(`/story/${story.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'काहीतरी चूक झाली');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof StoryForm, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-orange-400 to-pink-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <SparklesIcon className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">नवीन गोष्ट तयार करा</h1>
          <p className="text-gray-600">
            आपल्या मुलासाठी खास मराठी गोष्ट तयार करा
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Age Group Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              वयोगट निवडा *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {ageGroups.map((age) => (
                <label
                  key={age.value}
                  className={`relative flex flex-col p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    form.ageGroup === age.value
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-gray-200 hover:border-orange-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="ageGroup"
                    value={age.value}
                    checked={form.ageGroup === age.value}
                    onChange={(e) => handleInputChange('ageGroup', e.target.value)}
                    className="sr-only"
                  />
                  <span className="font-medium text-gray-800">{age.label}</span>
                  <span className="text-sm text-gray-600 mt-1">{age.description}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Theme Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              गोष्टीचा विषय निवडा *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {themes.map((theme) => (
                <button
                  key={theme}
                  type="button"
                  onClick={() => handleInputChange('theme', theme)}
                  className={`p-3 text-sm font-medium rounded-lg border-2 transition-all ${
                    form.theme === theme
                      ? 'border-orange-500 bg-orange-50 text-orange-700'
                      : 'border-gray-200 text-gray-700 hover:border-orange-300 hover:bg-orange-50'
                  }`}
                >
                  {theme}
                </button>
              ))}
            </div>
            
            {/* Custom Theme Input */}
            <div className="mt-3">
              <input
                type="text"
                placeholder="किंवा आपला विषय लिहा..."
                value={form.theme}
                onChange={(e) => handleInputChange('theme', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Moral Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              नैतिक शिकवण
            </label>
            <select
              value={form.moralType}
              onChange={(e) => handleInputChange('moralType', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              {moralTypes.map((moral) => (
                <option key={moral.value} value={moral.value}>
                  {moral.label}
                </option>
              ))}
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !form.ageGroup || !form.theme}
            className={`w-full py-4 px-6 rounded-lg font-medium text-white transition-all ${
              loading || !form.ageGroup || !form.theme
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-orange-400 to-pink-400 hover:from-orange-500 hover:to-pink-500 shadow-lg hover:shadow-xl'
            }`}
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>गोष्ट तयार होत आहे...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-2">
                <SparklesIcon className="w-5 h-5" />
                <span>गोष्ट तयार करा</span>
              </div>
            )}
          </button>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <ClockIcon className="w-5 h-5 text-blue-500 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">गोष्ट तयार होण्यास 2-3 मिनिटे लागतील</p>
                <p>यामध्ये मराठी आवाज आणि व्हिडिओ तयार करणे समाविष्ट आहे</p>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};