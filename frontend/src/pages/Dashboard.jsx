import { useState } from "react";
import axios from "axios";
import { Sparkles } from "lucide-react";

import FileUploader from "../components/FileUploader";
import StatsCards from "../components/StatsCards";
import ColumnProfiles from "../components/ColumnProfiles";
import CleaningPanel from "../components/CleaningPanel";

import ScoreComparison from "../components/ScoreComparison";
import MetricsBreakdown from "../components/MetricsBreakdown";
import ImportanceChart from "../components/ImportanceChart";
import RankingTable from "../components/RankingTable";
import CorrelationMatrix from "../components/CorrelationMatrix";
import CleanedTable from "../components/CleanedTable";

export default function Dashboard() {
  const [rawData, setRawData] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRunAnalysis = async (config) => {
    if (!rawData?.file) {
      alert("Please upload a file first.");
      return;
    }

    setLoading(true);
    setAnalysisResult(null);

    try {
      const formData = new FormData();
      formData.append("file", rawData.file);
      formData.append("remove_duplicates", String(config.removeDuplicates));
      formData.append("missing_strategy", config.missingStrategy);
      formData.append("outlier_method", config.outlierMethod);

      const response = await axios.post(
        "http://127.0.0.1:8000/analyze/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setAnalysisResult(response.data);
    } catch (error) {
      console.error("Analysis error:", error);
      alert("Analysis failed. Check backend.");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#050b18] text-white relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 via-purple-500/5 to-transparent blur-3xl"></div>

      {/* Navbar */}
      <div className="flex items-center px-10 py-6 border-b border-white/10 bg-white/5 backdrop-blur-xl relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/20">
            <Sparkles className="text-cyan-400" size={20} />
          </div>
          <div>
            <h1 className="text-lg font-semibold">
              Data Quality Analyzer
            </h1>
            <p className="text-xs text-white/50">
              UPLOAD • ANALYZE • CLEAN • EXPORT
            </p>
          </div>
        </div>
      </div>

      <div className="relative z-10 px-10 py-12 space-y-10">

        {!rawData && (
          <FileUploader setData={setRawData} />
        )}

        {/* After Upload – Before Analysis */}
        {rawData && !analysisResult && (
          <>
            <StatsCards
              rows={rawData?.rows_before}
              columns={rawData?.columns}
              duplicates={rawData?.duplicate_rows}
            />

            <ColumnProfiles
              data={rawData?.original_preview || []}
            />

            <CleaningPanel
              onRunAnalysis={handleRunAnalysis}
              loading={loading}
            />
          </>
        )}

        {/* After Analysis */}
        {analysisResult && (
          <>
            <ScoreComparison data={analysisResult} />

            <MetricsBreakdown
              beforeMetrics={analysisResult?.before_metrics || {}}
              afterMetrics={analysisResult?.after_metrics || {}}
            />

            {analysisResult?.column_importance && (
              <>
                <ImportanceChart data={analysisResult.column_importance} />
                <RankingTable data={analysisResult.column_importance} />
              </>
            )}

            {analysisResult?.cleaned_preview?.length > 0 && (
              <>
                <CorrelationMatrix data={analysisResult.cleaned_preview} />
                <CleanedTable data={analysisResult.cleaned_preview} />
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}