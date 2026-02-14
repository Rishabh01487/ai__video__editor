import { useEffect, useState } from 'react';
import { jobsAPI } from '../services/api';

export const useJobs = (projectId) => {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLatestJob = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const response = await jobsAPI.getLatest(projectId);
      setJob(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch job');
    } finally {
      setLoading(false);
    }
  };

  const fetchJobStatus = async (jobId) => {
    if (!jobId) return;
    try {
      const response = await jobsAPI.getStatus(jobId);
      setJob(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch job status');
    }
  };

  useEffect(() => {
    fetchLatestJob();
    // Poll for updates every 2 seconds
    const interval = setInterval(fetchLatestJob, 2000);
    return () => clearInterval(interval);
  }, [projectId]);

  return { job, loading, error, fetchLatestJob, fetchJobStatus };
};
