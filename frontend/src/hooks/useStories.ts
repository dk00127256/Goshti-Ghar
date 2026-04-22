import { useState, useCallback } from 'react';
import { apiUrl } from '../lib/api.ts';

export interface Story {
  id: string;
  title: string;
  content: string;
  moral: string;
  age_group: string;
  theme: string;
  moral_type: string;
  language: string;
  language_label: string;
  story_style: string;
  audio_url?: string;
  audio_quality?: string;
  duration?: number;
  duration_minutes?: number;
  word_count?: number;
  summary?: string;
  characters?: string[];
  setting?: string;
  age_appropriate_words?: string[];
  created_at?: string;
}

export const useStories = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchStories = useCallback(async (filters?: {
    ageGroup?: string;
    theme?: string;
    language?: string;
    storyStyle?: string;
  }) => {
    try {
      setLoading(true);
      setError('');

      const params = new URLSearchParams();
      if (filters?.ageGroup) params.append('age_group', filters.ageGroup);
      if (filters?.theme) params.append('theme', filters.theme);
      if (filters?.language) params.append('language', filters.language);
      if (filters?.storyStyle) params.append('story_style', filters.storyStyle);

      const response = await fetch(apiUrl(`/api/stories?${params.toString()}`));

      if (!response.ok) {
        throw new Error('Failed to load stories');
      }

      const data = await response.json();
      setStories(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setStories([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const createStory = useCallback(async (storyData: {
    age_group: string;
    theme: string;
    moral_type: string;
    language: string;
    story_style: string;
    duration_minutes: number;
  }) => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(apiUrl('/api/stories/generate'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(storyData),
      });

      if (!response.ok) {
        throw new Error('Failed to create story');
      }

      const newStory = await response.json();
      setStories((prev) => [newStory, ...prev]);
      return newStory;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    stories,
    loading,
    error,
    fetchStories,
    createStory,
  };
};
