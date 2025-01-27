import React, { useState } from 'react';
import { FaUpload, FaSpinner, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
import { chatApi } from '../services/api';

const UploadPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [clearExisting, setClearExisting] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadStatus('error');
      setErrorMessage('Only PDF files are allowed');
      return;
    }

    setIsLoading(true);
    setUploadStatus(null);
    setErrorMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('clear_existing', clearExisting);

      await chatApi.uploadPDF(formData);
      
      setUploadStatus('success');
      event.target.value = null; // Reset file input
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(error.response?.data?.detail || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Upload PDF Document</h1>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
        <label className="cursor-pointer">
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileUpload}
            className="hidden"
            disabled={isLoading}
          />
          <div className="flex flex-col items-center">
            <FaUpload className="w-12 h-12 text-gray-400 mb-4" />
            <p className="text-gray-600 mb-2">
              {isLoading ? 'Uploading...' : 'Click to select a PDF file'}
            </p>
            <p className="text-sm text-gray-500">Maximum file size: 10MB</p>
          </div>
        </label>

        <div className="mt-4 flex items-center justify-center gap-2">
          <input
            type="checkbox"
            id="clearExisting"
            checked={clearExisting}
            onChange={(e) => setClearExisting(e.target.checked)}
            className="h-4 w-4"
          />
          <label htmlFor="clearExisting" className="text-sm text-gray-600">
            Clear existing documents before upload
          </label>
        </div>
      </div>

      {isLoading && (
        <div className="mt-6 flex items-center justify-center gap-2 text-blue-600">
          <FaSpinner className="animate-spin" />
          <span>Processing PDF...</span>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="mt-6 flex items-center justify-center gap-2 text-green-600">
          <FaCheckCircle />
          <span>PDF uploaded and indexed successfully!</span>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="mt-6 flex items-center justify-center gap-2 text-red-600">
          <FaTimesCircle />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};

export default UploadPage;