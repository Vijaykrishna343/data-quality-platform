import React, { useState } from "react";
import FileUploader from "./components/FileUploader";
import DatasetOverview from "./components/DatasetOverview";
import QualitySection from "./components/QualitySection";
import ImportanceChart from "./components/ImportanceChart";

function App() {
  const [analysisData, setAnalysisData] = useState(null);

  return (
    <div>
      <h1>Intelligent Data Quality Platform</h1>

      <FileUploader setAnalysisData={setAnalysisData} />

      {analysisData && (
        <>
          <DatasetOverview data={analysisData} />
          <QualitySection data={analysisData} />
          <ImportanceChart data={analysisData} />
        </>
      )}
    </div>
  );
}

export default App;