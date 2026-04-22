import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  HeartIcon,
  ShareIcon,
  BookOpenIcon,
  UserGroupIcon,
  ClockIcon,
  LanguageIcon,
  SparklesIcon,
  SpeakerWaveIcon,
  PauseIcon,
  StopIcon,
  PlayIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import type { Story } from '../hooks/useStories.ts';
import { apiUrl } from '../lib/api.ts';

export const StoryPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isFavorite, setIsFavorite] = useState(false);
  const [showTranscript, setShowTranscript] = useState(true);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [preparingAudio, setPreparingAudio] = useState(false);
  const [audioError, setAudioError] = useState('');
  const [showBrowserVoice, setShowBrowserVoice] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (!('speechSynthesis' in window)) {
      return undefined;
    }

    const loadVoices = () => setVoices(window.speechSynthesis.getVoices());
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.cancel();
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, []);

  const fetchStory = useCallback(async (storyId: string) => {
    try {
      setLoading(true);
      const response = await fetch(apiUrl(`/api/stories/${storyId}`));

      if (!response.ok) {
        throw new Error('Could not find story');
      }

      const storyData = await response.json();
      setStory(storyData);

      if (!storyData.audio_url) {
        prepareNarration(storyId, true);
      }

      const favorites = JSON.parse(localStorage.getItem('favoriteStories') || '[]');
      setIsFavorite(favorites.includes(storyId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (id) {
      void fetchStory(id);
    }
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.removeAttribute('src');
        audioRef.current.load();
      }
    };
  }, [fetchStory, id]);

  const prepareNarration = async (storyId: string, force = false) => {
    try {
      setPreparingAudio(true);
      setAudioError('');

      const response = await fetch(apiUrl(`/api/stories/${storyId}/audio?force=${force ? 'true' : 'false'}`), {
        method: 'POST',
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail || 'Could not prepare narration');
      }

      const updatedStory = await response.json();
      setStory(updatedStory);
    } catch (err) {
      setAudioError(err instanceof Error ? err.message : 'Could not prepare narration');
    } finally {
      setPreparingAudio(false);
    }
  };

  const toggleFavorite = () => {
    if (!story) return;

    const favorites = JSON.parse(localStorage.getItem('favoriteStories') || '[]');
    const newFavorites = isFavorite
      ? favorites.filter((fav: string) => fav !== story.id)
      : [...favorites, story.id];

    localStorage.setItem('favoriteStories', JSON.stringify(newFavorites));
    setIsFavorite(!isFavorite);
  };

  const shareStory = async () => {
    if (!story) return;

    if (navigator.share) {
      try {
        await navigator.share({
          title: story.title,
          text: story.summary || story.moral,
          url: window.location.href,
        });
      } catch {
        return;
      }
    } else {
      await navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  const narrationVoice = useMemo(() => {
    if (!story) return undefined;

    const priorityLangs =
      story.language === 'mr'
        ? ['mr', 'hi-IN', 'hi', 'en-IN', 'en-US', 'en']
        : story.language === 'hi'
          ? ['hi-IN', 'hi', 'mr', 'en-IN', 'en-US', 'en']
          : ['en-IN', 'en-US', 'en-GB', 'en', 'hi-IN', 'hi'];

    for (const languageTag of priorityLangs) {
      const matchingVoice = voices.find((voice) => voice.lang.toLowerCase().startsWith(languageTag.toLowerCase()));
      if (matchingVoice) {
        return matchingVoice;
      }
    }

    return voices[0];
  }, [story, voices]);

  const speakStory = () => {
    if (!story || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(story.content);
    utterance.voice = narrationVoice || null;
    utterance.lang = narrationVoice?.lang || (story.language === 'en' ? 'en-US' : story.language === 'hi' ? 'hi-IN' : 'mr-IN');
    utterance.rate = story.story_style === 'bedtime' ? 0.85 : story.story_style === 'funny' ? 0.97 : 0.9;
    utterance.pitch = story.story_style === 'funny' ? 1.06 : 0.98;
    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPaused(false);
    };
    utterance.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };
    utterance.onerror = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const pauseNarration = () => {
    if (!('speechSynthesis' in window) || !isSpeaking) return;
    window.speechSynthesis.pause();
    setIsPaused(true);
  };

  const resumeNarration = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.resume();
    setIsPaused(false);
    setIsSpeaking(true);
  };

  const stopNarration = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '15 min';
    return `${Math.max(1, Math.floor(seconds / 60))} min`;
  };

  const getAgeGroupColor = (age: string) => {
    switch (age) {
      case '2-4':
        return 'bg-emerald-100 text-emerald-800';
      case '5-7':
        return 'bg-sky-100 text-sky-800';
      case '8-12':
        return 'bg-violet-100 text-violet-800';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center">
        <div className="h-16 w-16 animate-spin rounded-full border-4 border-orange-100 border-t-orange-500" />
        <p className="mt-4 font-medium text-slate-500">Loading story...</p>
      </div>
    );
  }

  if (error || !story) {
    return (
      <div className="py-20 text-center">
        <h2 className="text-2xl font-bold text-slate-800">Story not found</h2>
        <p className="mt-3 text-slate-500">{error}</p>
        <button onClick={() => navigate('/')} className="btn-primary mt-6">
          Go Home
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-12">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 font-medium text-slate-500 transition-colors hover:text-orange-600"
        >
          <ArrowLeftIcon className="h-5 w-5" />
          Back to stories
        </button>

        <div className="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-3 py-2 shadow-sm">
          <button
            onClick={toggleFavorite}
            className={`rounded-full p-2 transition-colors ${isFavorite ? 'bg-red-50 text-red-500' : 'text-slate-400 hover:bg-slate-50'}`}
          >
            {isFavorite ? <HeartSolidIcon className="h-6 w-6" /> : <HeartIcon className="h-6 w-6" />}
          </button>
          <button onClick={shareStory} className="rounded-full p-2 text-slate-400 transition-colors hover:bg-slate-50">
            <ShareIcon className="h-6 w-6" />
          </button>
        </div>
      </div>

      <div className="overflow-hidden rounded-[2rem] border border-white bg-white shadow-xl">
        <div className="flex aspect-video items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 px-8 text-center text-white">
          <div>
            <SparklesIcon className="mx-auto h-12 w-12 text-amber-300" />
            <p className="mt-4 text-xl font-semibold">Story player ready</p>
            <p className="mt-2 max-w-xl text-sm leading-7 text-slate-200">
              We’re prioritizing smoother narrated playback for this story instead of the browser’s robotic voice.
            </p>
          </div>
        </div>

        <div className="p-8 md:p-10">
          <div className="mb-8 flex flex-wrap gap-2">
            <span className={`rounded-full px-4 py-1.5 text-xs font-bold uppercase tracking-[0.22em] ${getAgeGroupColor(story.age_group)}`}>
              {story.age_group} years
            </span>
            <span className="rounded-full bg-slate-100 px-4 py-1.5 text-xs font-bold uppercase tracking-[0.22em] text-slate-700">
              {story.story_style}
            </span>
            <span className="rounded-full bg-sky-100 px-4 py-1.5 text-xs font-bold uppercase tracking-[0.22em] text-sky-700">
              {story.language_label}
            </span>
          </div>

          <h1 className="text-3xl font-bold leading-tight text-slate-900 md:text-5xl">{story.title}</h1>
          <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-600">{story.summary}</p>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <div className="rounded-3xl bg-slate-50 p-4">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Read Time</div>
              <div className="mt-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                <ClockIcon className="h-4 w-4 text-orange-500" />
                {formatDuration(story.duration)}
              </div>
            </div>
            <div className="rounded-3xl bg-slate-50 p-4">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Theme</div>
              <div className="mt-2 text-sm font-semibold text-slate-700">{story.theme}</div>
            </div>
            <div className="rounded-3xl bg-slate-50 p-4">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Characters</div>
              <div className="mt-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                <UserGroupIcon className="h-4 w-4 text-sky-500" />
                {story.characters?.length || 0}
              </div>
            </div>
            <div className="rounded-3xl bg-slate-50 p-4">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Language</div>
              <div className="mt-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                <LanguageIcon className="h-4 w-4 text-violet-500" />
                {story.language_label}
              </div>
            </div>
            <div className="rounded-3xl bg-slate-50 p-4">
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Words</div>
              <div className="mt-2 text-sm font-semibold text-slate-700">{story.word_count || 'n/a'}</div>
            </div>
          </div>

          <div className="mt-8 rounded-[2rem] border border-orange-100 bg-gradient-to-r from-orange-50 to-amber-50 p-5">
            <div className="mb-4 flex items-center gap-2 text-sm font-bold uppercase tracking-[0.22em] text-orange-700">
              <SpeakerWaveIcon className="h-4 w-4" />
              Studio Narration
            </div>

            {story.audio_url ? (
              <div className="space-y-4">
                <audio key={story.id} ref={audioRef} controls className="w-full" preload="metadata">
                  <source src={story.audio_url.startsWith('http') ? story.audio_url : apiUrl(story.audio_url)} type="audio/wav" />
                </audio>
                <p className="text-sm leading-6 text-slate-600">
                  This story uses refreshed neural narration instead of the browser fallback voice.
                </p>
              </div>
            ) : preparingAudio ? (
              <div className="rounded-2xl bg-white/80 px-4 py-4 text-sm font-medium text-slate-700">
                Preparing a clearer voice track for this story. Long stories can take a little while on first play.
              </div>
            ) : (
              <div className="space-y-4">
                <button
                  onClick={() => prepareNarration(story.id)}
                  className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white"
                >
                  <PlayIcon className="h-4 w-4" />
                  Prepare story audio
                </button>
                <p className="text-sm leading-6 text-slate-600">
                  Goshti Ghar can generate a fresh narration track for this story on demand.
                </p>
              </div>
            )}

            {audioError && (
              <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                {audioError}
              </div>
            )}

            {!story.audio_url && (
              <div className="mt-5 border-t border-orange-100 pt-5">
                <button
                  onClick={() => setShowBrowserVoice((value) => !value)}
                  className="text-sm font-semibold text-slate-700 underline-offset-4 hover:underline"
                >
                  {showBrowserVoice ? 'Hide browser voice fallback' : 'Use browser voice fallback'}
                </button>

                {showBrowserVoice && (
                  <div className="mt-4 space-y-4 rounded-2xl bg-white/80 p-4">
                    <div className="flex flex-wrap gap-3">
                      {!isSpeaking && (
                        <button onClick={speakStory} className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-700 border border-slate-200">
                          <PlayIcon className="h-4 w-4" />
                          Play browser voice
                        </button>
                      )}
                      {isSpeaking && !isPaused && (
                        <button onClick={pauseNarration} className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-700 border border-slate-200">
                          <PauseIcon className="h-4 w-4" />
                          Pause
                        </button>
                      )}
                      {isSpeaking && isPaused && (
                        <button onClick={resumeNarration} className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-700 border border-slate-200">
                          <PlayIcon className="h-4 w-4" />
                          Resume
                        </button>
                      )}
                      {(isSpeaking || isPaused) && (
                        <button onClick={stopNarration} className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-700 border border-slate-200">
                          <StopIcon className="h-4 w-4" />
                          Stop
                        </button>
                      )}
                    </div>

                    <p className="text-sm leading-6 text-slate-600">
                      {narrationVoice
                        ? `Fallback voice: ${narrationVoice.name} (${narrationVoice.lang})`
                        : 'Fallback to your browser default voice.'}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="mt-8 rounded-[2rem] border border-emerald-100 bg-gradient-to-br from-emerald-50 to-teal-50 p-6">
            <div className="text-sm font-bold uppercase tracking-[0.22em] text-emerald-800">Moral</div>
            <p className="mt-3 text-lg font-medium leading-8 text-emerald-950">{story.moral}</p>
          </div>

          <div className="mt-8 grid gap-6 xl:grid-cols-[1fr_0.34fr]">
            <div className="rounded-[2rem] border border-slate-100 p-6">
              <button
                onClick={() => setShowTranscript(!showTranscript)}
                className="mb-6 flex items-center gap-2 font-medium text-slate-600 transition-colors hover:text-slate-900"
              >
                <BookOpenIcon className="h-5 w-5" />
                {showTranscript ? 'Hide full story' : 'Read full story'}
              </button>

              {showTranscript && (
                <div className="space-y-6">
                  {story.content.split('\n\n').map((paragraph, index) => (
                    <p key={index} className="border-l-2 border-orange-200 pl-5 text-lg leading-8 text-slate-800">
                      {paragraph}
                    </p>
                  ))}
                </div>
              )}
            </div>

            <aside className="space-y-6">
              <div className="rounded-[2rem] border border-slate-100 bg-slate-50 p-6">
                <div className="text-sm font-bold uppercase tracking-[0.22em] text-slate-500">Setting</div>
                <p className="mt-3 text-base leading-7 text-slate-800">{story.setting || 'Not provided'}</p>
              </div>

              <div className="rounded-[2rem] border border-slate-100 bg-slate-50 p-6">
                <div className="text-sm font-bold uppercase tracking-[0.22em] text-slate-500">Characters</div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {(story.characters || []).map((character) => (
                    <span key={character} className="rounded-full bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm">
                      {character}
                    </span>
                  ))}
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-100 bg-slate-50 p-6">
                <div className="text-sm font-bold uppercase tracking-[0.22em] text-slate-500">Age Vocabulary</div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {(story.age_appropriate_words || []).map((word) => (
                    <span key={word} className="rounded-full bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm">
                      {word}
                    </span>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
  );
};
