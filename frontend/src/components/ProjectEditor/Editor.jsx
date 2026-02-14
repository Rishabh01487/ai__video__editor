import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { projectsAPI, jobsAPI } from '../../services/api';
import { useJobs } from '../../hooks/useJobs';
import UploadZone from '../UploadZone/UploadZone';
import ProcessingStatus from '../ProcessingStatus/ProcessingStatus';
import VideoPlayer from '../VideoPlayer/VideoPlayer';

const Editor = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [startingJob, setStartingJob] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);

  const { job } = useJobs(projectId);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  useEffect(() => {
    if (job?.status === 'completed' && project?.output_video_key) {
      // Generate video URL
      setVideoUrl(`${process.env.REACT_APP_API_URL}/projects/${projectId}/output`);
    }
  }, [job, project, projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      const response = await projectsAPI.get(projectId);
      setProject(response.data);
      setPrompt(response.data.prompt || '');
      // loadAssets(projectId);
    } catch (err) {
      setError('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePrompt = async () => {
    try {
      const response = await projectsAPI.update(projectId, { prompt });
      setProject(response.data);
    } catch (err) {
      setError('Failed to save prompt');
    }
  };

  const handleStartEdit = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    try {
      setStartingJob(true);
      await jobsAPI.startEdit({ project_id: projectId });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start editing');
    } finally {
      setStartingJob(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading project...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-600">Project not found</p>
      </div>
    );
  }

  const isProcessing = job?.status === 'processing';
  const isCompleted = job?.status === 'completed';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">{project.title}</h1>
          <p className="text-gray-600 mt-2">Edit your video using AI</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Video Preview */}
          <div className="lg:col-span-2 space-y-6">
            <VideoPlayer videoUrl={videoUrl} isLoading={isProcessing} />

            {/* Upload Section */}
            {!isProcessing && !isCompleted && (
              <UploadZone projectId={projectId} onAssetCreated={loadProject} />
            )}
          </div>

          {/* Right Column - Controls */}
          <div className="space-y-6">
            {/* Prompt Section */}
            <div className="card">
              <h3 className="text-lg font-bold mb-4">Edit Prompt</h3>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isProcessing}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                rows="6"
                placeholder="Describe how you want your video edited. Example: 'Make a 30 second fast-paced montage with upbeat music, add vintage filter'"
              />
              <button
                onClick={handleSavePrompt}
                disabled={isProcessing}
                className="w-full btn-secondary mt-4 disabled:opacity-50"
              >
                Save Prompt
              </button>
            </div>

            {/* Action Button */}
            {!isCompleted && (
              <button
                onClick={handleStartEdit}
                disabled={isProcessing || startingJob || !prompt.trim()}
                className="w-full btn-primary text-lg py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? 'Processing...' : startingJob ? 'Starting...' : '🎬 Generate Video'}
              </button>
            )}

            {isCompleted && (
              <div className="card bg-green-50">
                <p className="text-green-700 font-medium">✓ Video Ready!</p>
                <p className="text-sm text-green-600 mt-2">Your edited video is ready to download.</p>
              </div>
            )}

            {/* Status Section */}
            <ProcessingStatus job={job} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Editor;
