import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { assetsAPI } from '../../services/api';

const UploadZone = ({ projectId, onAssetCreated }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const onDrop = async (acceptedFiles) => {
    if (!acceptedFiles.length) return;

    const file = acceptedFiles[0];

    try {
      setUploading(true);
      setError(null);
      setProgress(0);

      // Get presigned URL
      const assetType = file.type.startsWith('video') ? 'video' : 'image';
      const presignedResponse = await assetsAPI.getPresignedUrl({
        asset_type: assetType,
        filename: file.name,
      });

      // Upload to S3
      const presignedUrl = presignedResponse.data.presigned_url;
      const s3Key = presignedResponse.data.s3_key;

      const config = {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        },
      };

      // Upload using the presigned URL
      await fetch(presignedUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      });

      setProgress(100);

      // Create asset record in database
      await assetsAPI.create(projectId, {
        s3_key: s3Key,
        filename: file.name,
        asset_type: assetType,
        file_size_bytes: file.size,
      });

      if (onAssetCreated) {
        onAssetCreated();
      }

      setUploading(false);
      setProgress(0);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: uploading,
  });

  return (
    <div className="card">
      <h3 className="text-lg font-bold mb-4">Upload Media</h3>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
          isDragActive
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <p className="text-gray-700 font-medium">
          {isDragActive
            ? 'Drop your files here...'
            : 'Drag and drop videos or images here, or click to select'}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Supported: MP4, WebM, JPG, PNG
        </p>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {uploading && progress > 0 && (
        <div className="mt-4">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">Uploading...</span>
            <span className="text-sm text-gray-600">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadZone;
