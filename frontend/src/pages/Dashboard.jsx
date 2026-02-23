import { useState, useEffect } from "react";
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

  useEffect(() => {
    if (analysisResult) {
      console.log("Analysis completed successfully");
    }
  }, [analysisResult]);

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

      <div className="relative z-10 px-10 py-12 space-y-10 min-h-[400px]">

        {!rawData && (
          <FileUploader setData={setRawData} />
        )}

        {rawData && !analysisResult && (
          <>
            <StatsCards
              rows={rawData?.rows_before}
              columns={rawData?.columns}
              duplicates={rawData?.duplicate_rows}
              emptyRows={rawData?.empty_rows}
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
          <div className="animate-fadeIn space-y-10">

            <ScoreComparison data={analysisResult} />

            {/* ✅ DATASET DIAGNOSTICS SECTION */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-8 space-y-6">
              <h2 className="text-xl font-semibold">
                Dataset Diagnostics
              </h2>

              <div className="grid md:grid-cols-2 gap-6 text-sm text-white/70">

                {/* Empty & Duplicate */}
                <div className="space-y-2">
                  <p>
                    <span className="text-white">Empty Rows:</span>{" "}
                    {analysisResult.empty_rows ?? 0}
                  </p>

                  <p>
                    <span className="text-white">Duplicate Rows:</span>{" "}
                    {analysisResult.duplicate_rows ?? 0}
                  </p>
                </div>

                {/* Order Detection */}
                <div className="space-y-2">
                  <p>
                    <span className="text-white">Ordered By:</span>{" "}
                    {analysisResult.order_report?.ordered_by || "Not Detected"}
                  </p>

                  <p
                    className={
                      analysisResult.order_report?.was_auto_sorted
                        ? "text-yellow-400"
                        : "text-green-400"
                    }
                  >
                    {analysisResult.order_report?.message ||
                      "No order analysis available."}
                  </p>
                </div>

                {/* Sequence Detection */}
                <div className="md:col-span-2 space-y-2">
                  <p className="text-white">Sequence Report:</p>

                  <p
                    className={
                      analysisResult.sequence_report?.has_gaps
                        ? "text-red-400"
                        : "text-green-400"
                    }
                  >
                    {analysisResult.sequence_report?.message ||
                      "No sequence analysis available."}
                  </p>

                  {analysisResult.sequence_report?.has_gaps &&
                    analysisResult.sequence_report?.missing_values?.length > 0 && (
                      <p className="text-red-400 text-xs mt-1">
                        Missing Values:{" "}
                        {analysisResult.sequence_report.missing_values.join(", ")}
                      </p>
                    )}
                </div>

              </div>
            </div>

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

            {analysisResult?.cleaned_preview && (
              <>
                {analysisResult.cleaned_preview.length > 0 ? (
                  <>
                    <CorrelationMatrix data={analysisResult.cleaned_preview} />
                    <CleanedTable data={analysisResult.cleaned_preview} />
                  </>
                ) : (
                  <div className="bg-white/5 border border-white/10 rounded-xl p-8 text-center text-white/60">
                    ⚠️ No rows remaining after cleaning.
                  </div>
                )}
              </>
            )}

          </div>
        )}
      </div>
    </div>
  );
}