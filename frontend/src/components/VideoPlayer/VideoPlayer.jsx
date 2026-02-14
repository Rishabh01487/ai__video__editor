import React from 'react';

const VideoPlayer = ({ videoUrl, isLoading }) => {
  if (isLoading) {
    return (
      <div className="card aspect-video bg-gray-900 flex items-center justify-center">
        <p className="text-white">Loading video...</p>
      </div>
    );
  }

  if (!videoUrl) {
    return (
      <div className="card aspect-video bg-gray-900 flex items-center justify-center">
        <p className="text-gray-400">No video generated yet</p>
      </div>
    );
  }

  return (
    <div className="card p-0 overflow-hidden">
      <video
        controls
        className="w-full aspect-video bg-black"
        src={videoUrl}
      >
        Your browser doesn't support HTML5 video.
      </video>
      <div className="p-4 border-t border-gray-200 flex gap-2">
        <a
          href={videoUrl}
          download="edited-video.mp4"
          className="btn-primary"
        >
          Download Video
        </a>
      </div>
    </div>
  );
};

export default VideoPlayer;
