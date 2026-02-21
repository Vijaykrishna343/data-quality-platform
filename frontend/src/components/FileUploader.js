import React, { useState } from "react";
import { analyzeDataset } from "../services/api";

function FileUploader({ setAnalysisData }) {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await analyzeDataset(formData);
      setAnalysisData(response.data);
    } catch (error) {
      console.error("Error analyzing dataset:", error);
    }
  };

  return (
    <div>
      <h3>Upload Dataset</h3>
      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload}>Analyze</button>
    </div>
  );
}

export default FileUploader;