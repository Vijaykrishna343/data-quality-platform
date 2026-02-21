import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const analyze = async () => {
    if (!file) return alert("Upload CSV file first");

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post(
      "http://127.0.0.1:8000/analyze",
      formData
    );

    setAnalysis(res.data);
  };

  return (
    <div style={{ padding: 40 }}>
      <h1>Data Quality Platform</h1>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={analyze} style={{ marginLeft: 10 }}>
        Analyze
      </button>

      {analysis && (
        <div style={{ marginTop: 20 }}>
          <p><b>Rows:</b> {analysis.rows}</p>
          <p><b>Columns:</b> {analysis.columns}</p>
          <p><b>Quality Score:</b> {analysis.quality_score}</p>

          <h3>Reasons:</h3>
          <ul>
            {analysis.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;