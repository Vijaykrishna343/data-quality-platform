import React, { useState } from "react";
import { analyzeDataset } from "../services/api";

function FileUploader({ setData }) {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    try {
      const result = await analyzeDataset(file);
      setData(result);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  return (
    <div>
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