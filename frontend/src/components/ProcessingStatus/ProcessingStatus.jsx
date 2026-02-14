import React from 'react';

const ProcessingStatus = ({ job }) => {
  if (!job) {
    return (
      <div className="card">
        <p className="text-gray-600">No processing job yet. Click "Generate Video" to start.</p>
      </div>
    );
  }

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <div className="card">
      <h3 className="text-lg font-bold mb-4">Processing Status</h3>

      <div className="space-y-4">
        {/* Status Badge */}
        <div>
          <p className="text-sm text-gray-600 mb-2">Status</p>
          <span
            className={`px-4 py-2 rounded-full font-medium text-sm ${
              statusColors[job.status] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
          </span>
        </div>

        {/* Progress Bar */}
        <div>
          <div className="flex justify-between mb-2">
            <p className="text-sm text-gray-600 font-medium">Progress</p>
            <span className="text-sm font-medium">{job.progress_percent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all"
              style={{ width: `${job.progress_percent}%` }}
            />
          </div>
        </div>

        {/* Timestamps */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Started</p>
            <p className="font-medium">
              {job.started_at
                ? new Date(job.started_at).toLocaleTimeString()
                : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-gray-600">Completed</p>
            <p className="font-medium">
              {job.completed_at
                ? new Date(job.completed_at).toLocaleTimeString()
                : 'N/A'}
            </p>
          </div>
        </div>

        {/* Error Message */}
        {job.error_message && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm font-medium text-red-800">Error</p>
            <p className="text-sm text-red-700 mt-1">{job.error_message}</p>
          </div>
        )}

        {/* Job ID */}
        <div className="pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-600">Job ID</p>
          <p className="text-xs font-mono text-gray-800 break-all">{job.id}</p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingStatus;
