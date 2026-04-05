import re

f = 'frontend/src/pages/DashboardPage.jsx'
with open(f, 'r', encoding='utf-8') as file:
    content = file.read()

# 1. Add trainModel, getPlotUrl to imports
import_target = """import {
  getAnalytics,
  simulateCleaning,
  fetchDatasetPage,
  downloadCleanedDataset,
} from "../services/api";"""

import_replacement = """import {
  getAnalytics,
  simulateCleaning,
  fetchDatasetPage,
  downloadCleanedDataset,
  trainModel,
  getPlotUrl
} from "../services/api";"""

content = content.replace(import_target, import_replacement)

# 2. Add the ML component invocation
ml_comp = "<MLSection datasetId={datasetId} columns={allColumns} />\n\n          {/* CLEANED DATA PREVIEW */}"
content = content.replace("{/* CLEANED DATA PREVIEW */}", ml_comp)

# 3. Add MLSection component at the end
ml_section_code = """
function MLSection({ datasetId, columns }) {
  const [targetColumn, setTargetColumn] = useState("");
  const [taskType, setTaskType] = useState("classification");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  const handleTrain = async () => {
    if (!targetColumn) {
      setError("Please select a target column.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await trainModel(datasetId, targetColumn, taskType);
      setMetrics(res.data.metrics);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to train model.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section title="Advanced Machine Learning">
      <div className="space-y-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Target Column (Y)</label>
            <select
              value={targetColumn}
              onChange={(e) => setTargetColumn(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white outline-none focus:border-indigo-500"
            >
              <option value="">-- Select Target --</option>
              {columns && columns.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Task Type</label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white outline-none focus:border-indigo-500"
            >
              <option value="classification">Classification</option>
              <option value="regression">Regression</option>
            </select>
          </div>
          <button
            onClick={handleTrain}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 px-8 py-3 rounded-xl font-bold uppercase tracking-widest transition-all disabled:opacity-50"
          >
            {loading ? "Training..." : "Train Model"}
          </button>
        </div>

        {error && <div className="text-red-400 bg-red-900/20 p-4 rounded-lg">{error}</div>}

        {metrics && (
          <div className="mt-8 space-y-6">
            <h3 className="text-xl font-semibold text-indigo-300">Training Results</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {metrics.accuracy !== undefined && (
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
                  <div className="text-xs text-gray-400 uppercase">Accuracy</div>
                  <div className="text-2xl font-bold">{(metrics.accuracy * 100).toFixed(2)}%</div>
                </div>
              )}
              {metrics.precision !== undefined && (
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
                  <div className="text-xs text-gray-400 uppercase">Precision</div>
                  <div className="text-2xl font-bold">{(metrics.precision * 100).toFixed(2)}%</div>
                </div>
              )}
              {metrics.recall !== undefined && (
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
                  <div className="text-xs text-gray-400 uppercase">Recall</div>
                  <div className="text-2xl font-bold">{(metrics.recall * 100).toFixed(2)}%</div>
                </div>
              )}
              {metrics.f1_score !== undefined && (
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
                  <div className="text-xs text-gray-400 uppercase">F1 Score</div>
                  <div className="text-2xl font-bold">{(metrics.f1_score * 100).toFixed(2)}%</div>
                </div>
              )}
              {metrics.rmse !== undefined && (
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
                  <div className="text-xs text-gray-400 uppercase">RMSE</div>
                  <div className="text-2xl font-bold">{metrics.rmse.toFixed(4)}</div>
                </div>
              )}
            </div>
            
            {metrics.explainability && !metrics.explainability.error && (
              <div className="mt-10 overflow-hidden bg-white/5 p-6 rounded-2xl border border-white/10">
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400"/> SHAP Explainability
                </h3>
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h4 className="text-sm text-gray-400 uppercase tracking-widest mb-4">Summary Plot</h4>
                    <img src={getPlotUrl('summary')} alt="SHAP Summary" className="w-full h-auto rounded-lg border border-white/10 bg-white" onError={(e)=>e.target.style.display='none'} />
                  </div>
                  <div>
                    <h4 className="text-sm text-gray-400 uppercase tracking-widest mb-4">Feature Importance</h4>
                    <img src={getPlotUrl('bar')} alt="SHAP Bar" className="w-full h-auto rounded-lg border border-white/10 bg-white" onError={(e)=>e.target.style.display='none'} />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Section>
  );
}
"""

content += '\n' + ml_section_code

with open(f, 'w', encoding='utf-8') as file: file.write(content)
print('SUCCESS')
