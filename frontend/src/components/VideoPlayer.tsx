import React, { useState, useRef } from 'react';
import ReactPlayer from 'react-player';
import { 
  PlayIcon, 
  PauseIcon, 
  SpeakerWaveIcon, 
  SpeakerXMarkIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon
} from '@heroicons/react/24/outline';

interface VideoPlayerProps {
  url: string;
  title: string;
  onEnded?: () => void;
  autoplay?: boolean;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  url,
  title,
  onEnded,
  autoplay = false
}) => {
  const [playing, setPlaying] = useState(autoplay);
  const [muted, setMuted] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [played, setPlayed] = useState(0);
  const [duration, setDuration] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);
  const playerRef = useRef<ReactPlayer>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handlePlayPause = () => {
    setPlaying(!playing);
  };

  const handleMute = () => {
    setMuted(!muted);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setVolume(parseFloat(e.target.value));
  };

  const handleProgress = (state: { played: number }) => {
    setPlayed(state.played);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const seekTo = parseFloat(e.target.value);
    setPlayed(seekTo);
    playerRef.current?.seekTo(seekTo);
  };

  const handleDuration = (duration: number) => {
    setDuration(duration);
  };

  const toggleFullscreen = () => {
    if (!fullscreen) {
      if (containerRef.current?.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setFullscreen(!fullscreen);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div 
      ref={containerRef}
      className={`relative bg-black rounded-lg overflow-hidden ${
        fullscreen ? 'fixed inset-0 z-50' : 'aspect-video'
      }`}
    >
      {/* Video Player */}
      <ReactPlayer
        ref={playerRef}
        url={url}
        width="100%"
        height="100%"
        playing={playing}
        muted={muted}
        volume={volume}
        onProgress={handleProgress}
        onDuration={handleDuration}
        onEnded={onEnded}
        config={{
          file: {
            attributes: {
              controlsList: 'nodownload',
              disablePictureInPicture: true,
            }
          }
        }}
      />

      {/* Custom Controls Overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        {/* Progress Bar */}
        <div className="mb-4">
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={played}
            onChange={handleSeek}
            className="w-full h-2 bg-white/30 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-white text-sm mt-1">
            <span>{formatTime(played * duration)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Play/Pause */}
            <button
              onClick={handlePlayPause}
              className="w-12 h-12 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-colors"
            >
              {playing ? (
                <PauseIcon className="w-6 h-6 text-white" />
              ) : (
                <PlayIcon className="w-6 h-6 text-white ml-1" />
              )}
            </button>

            {/* Volume Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={handleMute}
                className="w-8 h-8 flex items-center justify-center text-white hover:text-orange-300 transition-colors"
              >
                {muted ? (
                  <SpeakerXMarkIcon className="w-5 h-5" />
                ) : (
                  <SpeakerWaveIcon className="w-5 h-5" />
                )}
              </button>
              
              <input
                type="range"
                min={0}
                max={1}
                step={0.1}
                value={muted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20 h-1 bg-white/30 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>

          {/* Right Controls */}
          <div className="flex items-center space-x-2">
            <span className="text-white text-sm font-medium">{title}</span>
            
            <button
              onClick={toggleFullscreen}
              className="w-8 h-8 flex items-center justify-center text-white hover:text-orange-300 transition-colors"
            >
              {fullscreen ? (
                <ArrowsPointingInIcon className="w-5 h-5" />
              ) : (
                <ArrowsPointingOutIcon className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Loading Overlay */}
      {!playing && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <button
            onClick={handlePlayPause}
            className="w-20 h-20 bg-white/90 hover:bg-white rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110"
          >
            <PlayIcon className="w-10 h-10 text-orange-500 ml-1" />
          </button>
        </div>
      )}
    </div>
  );
};