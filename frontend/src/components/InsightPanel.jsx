export default function InsightPanel({ analysis }) {
  if (!analysis) return null;

  const strongestFeature =
    analysis.column_importance &&
    Object.entries(analysis.column_importance)
      .sort((a, b) => b[1] - a[1])[1]?.[0];

  const mlReady =
    analysis.missing_percentage < 5 &&
    analysis.duplicate_count < 5 &&
    Object.keys(analysis.correlation || {}).length >= 3;

  return (
    <div className="bg-gradient-to-r from-indigo-800 to-indigo-600 p-6 rounded-xl shadow-lg space-y-4">

      <h2 className="text-xl font-bold">AI Insights</h2>

      <div className="space-y-2">
        <p>📊 Dataset Size: {analysis.rows} rows</p>
        <p>⚠ Missing: {analysis.missing_percentage}%</p>
        <p>🧹 Duplicates: {analysis.duplicate_count}</p>
        <p>📈 Strongest Feature Influencing Price: {strongestFeature}</p>
      </div>

      <div className="mt-4">
        {mlReady ? (
          <span className="px-4 py-2 bg-green-600 rounded-full">
            🟢 Ready for ML Modeling
          </span>
        ) : (
          <span className="px-4 py-2 bg-yellow-500 rounded-full">
            🟡 Needs Further Preprocessing
          </span>
        )}
      </div>
    </div>
  );
}