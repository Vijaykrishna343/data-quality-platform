import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useParams } from "react-router-dom";
import {
  getAnalytics,
  simulateCleaning,
  fetchDatasetPage,
  downloadCleanedDataset,
} from "../services/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const PAGE_SIZE = 20;

const DashboardPage = () => {
  const { datasetId } = useParams();

  const [analytics, setAnalytics] = useState(null);
  const [cleanResult, setCleanResult] = useState(null);

  const [previewRows, setPreviewRows] = useState([]);
  const [previewColumns, setPreviewColumns] = useState([]);
  const [page, setPage] = useState(1);
  const [totalRows, setTotalRows] = useState(0);

  const [handleMissing, setHandleMissing] = useState(true);
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [outlierMethod, setOutlierMethod] = useState("iqr");
  const [dropColumns, setDropColumns] = useState([]);

  const [showPreview, setShowPreview] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    initialize();
  }, []);

  const initialize = async () => {
    setLoading(true);
    const res = await getAnalytics(datasetId);
    setAnalytics(res.data);
    setLoading(false);
  };

  const loadPreview = async (pageNumber) => {
    const res = await fetchDatasetPage(datasetId, pageNumber, PAGE_SIZE);

    setPreviewRows(res.data.rows || []);
    setPreviewColumns(res.data.columns || []);
    setTotalRows(res.data.total_rows || 0);
    setPage(pageNumber);
  };

  const totalPages = Math.ceil(totalRows / PAGE_SIZE);

  const runCleaning = async () => {
    const res = await simulateCleaning(datasetId, {
      handle_missing: handleMissing,
      remove_duplicates: removeDuplicates,
      outlier_method: outlierMethod,
      drop_columns: dropColumns,
    });

    setCleanResult(res.data);

    await loadPreview(1);
    setShowPreview(true);
  };

  const toggleColumn = (col) => {
    if (dropColumns.includes(col)) {
      setDropColumns(dropColumns.filter((c) => c !== col));
    } else {
      setDropColumns([...dropColumns, col]);
    }
  };

  if (!analytics)
    return <div className="p-10 text-white">Loading analytics...</div>;

  const importanceData = Object.entries(
    analytics.importance || {}
  ).map(([key, value]) => ({
    name: key,
    value,
  }));

  return (
    <div className="p-8 text-white space-y-10">

      {/* ================= OVERVIEW ================= */}
      <Section title="Dataset Overview (Before Cleaning)">
        <StatsGrid profile={analytics.profile} />
      </Section>

      {/* ================= IMPORTANCE ================= */}
      <Section title="Column Importance">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={importanceData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#6366f1" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>

        <ImportanceTable data={importanceData} />
      </Section>

      {/* ================= MANUAL DROP ================= */}
      <Section title="Manual Column Removal">
        <div className="grid grid-cols-3 gap-3">
          {importanceData.map((col) => (
            <label key={col.name} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={dropColumns.includes(col.name)}
                onChange={() => toggleColumn(col.name)}
              />
              <span>{col.name}</span>
            </label>
          ))}
        </div>
      </Section>

      {/* ================= CLEANING OPTIONS ================= */}
      <Section title="Cleaning Options">
        <div className="space-y-4">
          <Checkbox
            label="Handle Missing Values"
            value={handleMissing}
            setValue={setHandleMissing}
          />
          <Checkbox
            label="Remove Duplicates"
            value={removeDuplicates}
            setValue={setRemoveDuplicates}
          />

          <select
            value={outlierMethod}
            onChange={(e) => setOutlierMethod(e.target.value)}
            className="bg-black border px-3 py-2 rounded"
          >
            <option value="none">No Outlier Removal</option>
            <option value="iqr">IQR Method</option>
            <option value="isolation">Isolation Forest</option>
          </select>

          <button
            onClick={runCleaning}
            className="bg-indigo-600 px-6 py-2 rounded hover:scale-105 transition"
          >
            Run Smart Cleaning
          </button>
        </div>
      </Section>

      {/* ================= RESULTS ================= */}
      {cleanResult && (
        <Section title="Cleaning Results">
          <div className="flex gap-10 text-lg">
            <ScoreCard label="Before Score" value={cleanResult.score_before} />
            <ScoreCard label="After Score" value={cleanResult.score_after} />
            <ScoreCard
              label="Improvement"
              value={`+${cleanResult.improvement}`}
            />
          </div>

          <div className="mt-4">
            <AutoMLBadge score={cleanResult.score_after} />
          </div>
        </Section>
      )}

      {/* ================= PREVIEW ================= */}
      {showPreview && (
        <Section title="Cleaned Dataset Preview">
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-white/10">
              <thead>
                <tr>
                  {previewColumns.map((col) => (
                    <th key={col} className="border px-2 py-1">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row, i) => (
                  <tr key={i}>
                    {previewColumns.map((col) => (
                      <td key={col} className="border px-2 py-1">
                        {row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex justify-between mt-6 items-center">
            <button
              disabled={page === 1}
              onClick={() => loadPreview(page - 1)}
              className="bg-gray-700 px-4 py-2 rounded disabled:opacity-50"
            >
              Previous
            </button>

            <span>
              Page {page} of {totalPages}
            </span>

            <button
              disabled={page === totalPages}
              onClick={() => loadPreview(page + 1)}
              className="bg-gray-700 px-4 py-2 rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>

          <button
            onClick={() => downloadCleanedDataset(datasetId)}
            className="mt-6 bg-green-600 px-6 py-2 rounded hover:scale-105 transition"
          >
            Download Cleaned CSV
          </button>
        </Section>
      )}
    </div>
  );
};

/* ================= COMPONENTS ================= */

const Section = ({ title, children }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4 }}
    className="bg-white/5 p-6 rounded-xl border border-white/10 backdrop-blur-md"
  >
    <h2 className="text-xl mb-6 font-semibold">{title}</h2>
    {children}
  </motion.div>
);

const StatsGrid = ({ profile }) => (
  <div className="grid grid-cols-5 gap-4">
    <Stat title="Rows" value={profile.rows} />
    <Stat title="Columns" value={profile.columns} />
    <Stat title="Missing %" value={profile.missing_percentage} />
    <Stat title="Duplicates %" value={profile.duplicate_percentage} />
    <Stat title="Score" value={profile.quality_score} />
  </div>
);

const Stat = ({ title, value }) => (
  <div className="bg-black/40 p-4 rounded text-center">
    <div className="text-sm">{title}</div>
    <div className="text-2xl font-bold">{value}</div>
  </div>
);

const Checkbox = ({ label, value, setValue }) => (
  <label className="flex items-center space-x-2">
    <input type="checkbox" checked={value} onChange={(e) => setValue(e.target.checked)} />
    <span>{label}</span>
  </label>
);

const ScoreCard = ({ label, value }) => (
  <div className="bg-black/40 p-4 rounded text-center">
    <div className="text-sm">{label}</div>
    <div className="text-2xl font-bold">{value}</div>
  </div>
);

const ImportanceTable = ({ data }) => (
  <table className="w-full mt-6 text-sm border border-white/10">
    <thead>
      <tr>
        <th className="border px-2 py-1">Column</th>
        <th className="border px-2 py-1">Importance</th>
      </tr>
    </thead>
    <tbody>
      {data.map((row) => (
        <tr key={row.name}>
          <td className="border px-2 py-1">{row.name}</td>
          <td className="border px-2 py-1">{row.value}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

const AutoMLBadge = ({ score }) => {
  if (score < 70)
    return <div className="bg-red-600 px-4 py-2 rounded w-fit">Not Ready</div>;
  if (score < 85)
    return <div className="bg-yellow-500 px-4 py-2 rounded w-fit">Needs Work</div>;
  return <div className="bg-green-600 px-4 py-2 rounded w-fit">ML Ready</div>;
};

export default DashboardPage;