import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getProfile,
  getClassification,
  getRecommendation,
  simulateCleaning,
  fetchDatasetPage,
  downloadCleanedDataset,
} from "../services/api";

const DashboardPage = () => {
  const { datasetId } = useParams();

  const [profile, setProfile] = useState(null);
  const [classification, setClassification] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [preview, setPreview] = useState(null);

  const [loading, setLoading] = useState(true);
  const [cleaningResult, setCleaningResult] = useState(null);

  const [page, setPage] = useState(1);
  const pageSize = 20;

  const [cleaningOptions, setCleaningOptions] = useState({
    handle_missing: true,
    remove_duplicates: true,
    outlier_method: "none",
  });

  /* ================= LOAD INITIAL DATA ================= */

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);

        const profileRes = await getProfile(datasetId);
        const classRes = await getClassification(datasetId);
        const recRes = await getRecommendation(datasetId);
        const previewRes = await fetchDatasetPage(datasetId, page, pageSize);

        setProfile(profileRes.data);
        setClassification(classRes.data);
        setRecommendation(recRes.data);
        setPreview(previewRes.data);
      } catch (error) {
        console.error("Dashboard load error:", error);
      } finally {
        setLoading(false);
      }
    };

    if (datasetId) loadData();
  }, [datasetId, page]);

  /* ================= CLEANING ================= */

  const runCleaning = async () => {
    try {
      const res = await simulateCleaning(datasetId, cleaningOptions);
      setCleaningResult(res.data);

      const updatedPreview = await fetchDatasetPage(datasetId, 1, pageSize);
      setPreview(updatedPreview.data);
      setPage(1);
    } catch (err) {
      console.error("Cleaning failed:", err);
    }
  };

  /* ================= DOWNLOAD ================= */

  const handleDownload = async () => {
    try {
      const response = await downloadCleanedDataset(datasetId);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "cleaned_dataset.csv");
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error("Download failed:", err);
    }
  };

  if (loading) return <div className="p-10 text-white">Loading...</div>;

  if (!profile) return <div className="p-10 text-red-500">Failed to load</div>;

  return (
    <div className="p-8 text-white space-y-8">

      {/* ================= STATS ================= */}

      <div className="grid grid-cols-4 gap-6">
        <StatCard title="Rows" value={profile.rows} />
        <StatCard title="Columns" value={profile.columns} />
        <StatCard title="Missing %" value={profile.missing_percentage} />
        <StatCard title="Duplicates %" value={profile.duplicate_percentage} />
      </div>

      {/* ================= QUALITY SCORE ================= */}

      <Section title="Quality Score (Before Cleaning)">
        <h2 className="text-3xl font-bold text-yellow-400">
          {cleaningResult?.before_score || profile.quality_score || "N/A"}
        </h2>
      </Section>

      {/* ================= FEATURE IMPORTANCE ================= */}

      {profile.importance && (
        <Section title="Feature Importance (Before Cleaning)">
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(profile.importance).map(([key, value]) => (
              <div key={key} className="flex justify-between border-b py-1">
                <span>{key}</span>
                <span>{value}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ================= RECOMMENDATIONS ================= */}

      {recommendation?.before?.length > 0 && (
        <Section title="Smart Cleaning Recommendations">
          {recommendation.before.map((rec, index) => (
            <div key={index} className="mb-2">
              • {rec.column} — {rec.issue}
            </div>
          ))}
        </Section>
      )}

      {/* ================= CLASSIFICATION ================= */}

      {classification && (
        <Section title="Column Classification">
          {Object.entries(classification).map(([type, cols]) => (
            <div key={type} className="mb-4">
              <h4 className="font-semibold capitalize">{type}</h4>
              <div>{cols.length ? cols.join(", ") : "None"}</div>
            </div>
          ))}
        </Section>
      )}

      {/* ================= CLEANING OPTIONS ================= */}

      <Section title="Cleaning Options">
        <div className="space-y-4">
          <label>
            <input
              type="checkbox"
              checked={cleaningOptions.handle_missing}
              onChange={(e) =>
                setCleaningOptions({
                  ...cleaningOptions,
                  handle_missing: e.target.checked,
                })
              }
            />{" "}
            Handle Missing Values
          </label>

          <label>
            <input
              type="checkbox"
              checked={cleaningOptions.remove_duplicates}
              onChange={(e) =>
                setCleaningOptions({
                  ...cleaningOptions,
                  remove_duplicates: e.target.checked,
                })
              }
            />{" "}
            Remove Duplicates
          </label>

          <div>
            Outlier Method:
            <select
              className="ml-2 text-black"
              value={cleaningOptions.outlier_method}
              onChange={(e) =>
                setCleaningOptions({
                  ...cleaningOptions,
                  outlier_method: e.target.value,
                })
              }
            >
              <option value="none">None</option>
              <option value="iqr">IQR</option>
              <option value="zscore">Z-Score</option>
            </select>
          </div>

          <button
            onClick={runCleaning}
            className="bg-purple-600 px-4 py-2 rounded"
          >
            Run Smart Cleaning
          </button>
        </div>
      </Section>

      {/* ================= CLEANING IMPACT ================= */}

      {cleaningResult && (
        <Section title="Cleaning Impact">
          <div>Before: {cleaningResult.before_score}</div>
          <div>After: {cleaningResult.after_score}</div>
        </Section>
      )}

      {/* ================= AUTOML READINESS ================= */}

      {cleaningResult && (
        <Section title="AutoML Readiness">
          <div className="bg-green-600 text-center py-3 rounded">
            ML Ready
          </div>
        </Section>
      )}

      {/* ================= DATA PREVIEW ================= */}

      {preview && (
        <Section title="Cleaned Dataset Preview">
          <table className="w-full text-sm">
            <thead>
              <tr>
                {preview.columns.map((col) => (
                  <th key={col} className="border px-2 py-1">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.rows.map((row, i) => (
                <tr key={i}>
                  {preview.columns.map((col) => (
                    <td key={col} className="border px-2 py-1">
                      {row[col]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="flex justify-between mt-4">
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="bg-gray-600 px-4 py-2 rounded"
            >
              Previous
            </button>

            <div>
              Page {page} of {preview.total_pages}
            </div>

            <button
              disabled={page === preview.total_pages}
              onClick={() => setPage(page + 1)}
              className="bg-gray-600 px-4 py-2 rounded"
            >
              Next
            </button>
          </div>

          <button
            onClick={handleDownload}
            className="mt-4 bg-green-600 px-4 py-2 rounded"
          >
            Download Cleaned Dataset
          </button>
        </Section>
      )}
    </div>
  );
};

/* ================= COMPONENTS ================= */

const StatCard = ({ title, value }) => (
  <div className="bg-gray-800 p-4 rounded">
    <div className="text-sm">{title}</div>
    <div className="text-xl font-bold">{value}</div>
  </div>
);

const Section = ({ title, children }) => (
  <div className="bg-gray-900 p-6 rounded">
    <h3 className="text-lg font-semibold mb-4">{title}</h3>
    {children}
  </div>
);

export default DashboardPage;