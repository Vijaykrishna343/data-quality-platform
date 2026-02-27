import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFile } from "../services/api";

const UploadPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a CSV file");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile); // MUST match backend param

    try {
      setLoading(true);
      const response = await uploadFile(formData);

      const datasetId = response.data.dataset_id;

      navigate(`/dashboard/${datasetId}`);
    } catch (error) {
      console.error(error);
      alert("Upload failed. Make sure it is a valid CSV file.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-black flex items-center justify-center px-6">
      <div className="w-full max-w-xl bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-10 shadow-2xl">

        <h1 className="text-3xl font-bold text-white text-center mb-8">
          Upload Your Dataset
        </h1>

        {/* Drag Area */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300 ${
            dragActive
              ? "border-purple-400 bg-purple-500/10"
              : "border-white/20"
          }`}
        >
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="hidden"
            id="fileUpload"
          />

          <label
            htmlFor="fileUpload"
            className="cursor-pointer text-white"
          >
            {selectedFile ? (
              <span className="text-green-400 font-medium">
                {selectedFile.name}
              </span>
            ) : (
              "Drag & drop CSV file here or click to browse"
            )}
          </label>
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={loading}
          className="w-full mt-8 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold hover:scale-105 transition-all duration-300 disabled:opacity-50"
        >
          {loading ? "Uploading..." : "Upload & Analyze"}
        </button>
      </div>
    </div>
  );
};

export default UploadPage;