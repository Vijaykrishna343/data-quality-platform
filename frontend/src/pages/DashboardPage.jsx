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
  Cell,
} from "recharts";

const PAGE_SIZE = 20;

export default function DashboardPage() {
  const { datasetId } = useParams();

  const [analytics, setAnalytics] = useState(null);
  const [cleanResult, setCleanResult] = useState(null);
  const [rows, setRows] = useState([]);
  const [columns, setColumns] = useState([]);
  const [page, setPage] = useState(1);
  const [totalRows, setTotalRows] = useState(0);
  const [cleaningLoading, setCleaningLoading] = useState(false);

  const [handleMissing, setHandleMissing] = useState(true);
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [outlierMethod, setOutlierMethod] = useState("iqr");
  const [dropColumns, setDropColumns] = useState([]);

  useEffect(() => {
    init();
  }, []);

  const init = async () => {
    const res = await getAnalytics(datasetId);
    setAnalytics(res.data);
  };

  const loadPreview = async (p = 1) => {
    const res = await fetchDatasetPage(datasetId, p, PAGE_SIZE);
    setRows(res.data.rows || []);
    setColumns(res.data.columns || []);
    setTotalRows(res.data.total_rows || 0);
    setPage(p);
  };

  const toggleColumn = (col) => {
    if (dropColumns.includes(col)) {
      setDropColumns(dropColumns.filter((c) => c !== col));
    } else {
      setDropColumns([...dropColumns, col]);
    }
  };

  const runCleaning = async () => {
    setCleaningLoading(true);
    try {
      const res = await simulateCleaning(datasetId, {
        handle_missing: handleMissing,
        remove_duplicates: removeDuplicates,
        outlier_method: outlierMethod,
        drop_columns: dropColumns,
      });
      setCleanResult(res.data);
      await loadPreview(1);
    } finally {
      setCleaningLoading(false);
    }
  };

  const handleDownload = async () => {
    const response = await downloadCleanedDataset(datasetId);
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "cleaned_dataset.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  if (!analytics)
    return (
      <div className="flex items-center justify-center h-screen bg-[#0f172a] text-white">
        Loading analytics...
      </div>
    );

  const importanceData = Object.entries(
    analytics.importance || {}
  ).map(([key, value]) => ({ name: key, value }));

  const allColumns = [
    ...(analytics.data_types?.numeric || []),
    ...(analytics.data_types?.categorical || []),
    ...(analytics.data_types?.boolean || []),
    ...(analytics.data_types?.datetime || []),
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e1b4b] to-[#0f172a] text-white p-10 space-y-14">

      {/* OVERVIEW */}
      <Section title="Dataset Overview">
        <StatsGrid profile={analytics.profile} />
        <MLBadge readiness={analytics.ml_readiness} />
      </Section>

      {/* DATA TYPES */}
      <Section title="Column Data Types">
        <DataTypeBlock title="Numeric" items={analytics.data_types?.numeric} />
        <DataTypeBlock title="Categorical" items={analytics.data_types?.categorical} />
        <DataTypeBlock title="Boolean" items={analytics.data_types?.boolean} />
        <DataTypeBlock title="Datetime" items={analytics.data_types?.datetime} />
      </Section>

      {/* IMPORTANCE */}
      <Section title="Column Importance">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={importanceData}>
            <XAxis dataKey="name" angle={-30} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" radius={[10, 10, 0, 0]}>
              {importanceData.map((entry, index) => {
                let color = "#6366f1";
                if (index === 0) color = "#10b981";
                if (index === 1) color = "#22c55e";
                if (index === 2) color = "#84cc16";
                return <Cell key={index} fill={color} />;
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Section>

      {/* CORRELATION */}
      <Section title="Correlation Analysis">
        <CorrelationHeatmap matrix={analytics.correlation?.matrix} />
        <StrongCorrelationPairs pairs={analytics.correlation?.strong_pairs} />
      </Section>

      {/* AI REVIEW BEFORE */}
      <Section title="AI Review (Before Cleaning)">
        <AIReview review={analytics.ai_review} />
      </Section>

      {/* CLEANING CONTROLS */}
      <Section title="Smart Cleaning Controls">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="space-y-4">
            <Toggle label="Handle Missing" value={handleMissing} setValue={setHandleMissing} />
            <Toggle label="Remove Duplicates" value={removeDuplicates} setValue={setRemoveDuplicates} />

            <select
              value={outlierMethod}
              onChange={(e) => setOutlierMethod(e.target.value)}
              className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2"
            >
              <option value="none">No Outlier Removal</option>
              <option value="iqr">IQR</option>
              <option value="isolation">Isolation Forest</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <h3 className="text-gray-400 mb-4">Drop Columns</h3>
            <div className="grid grid-cols-2 gap-3 max-h-72 overflow-y-auto">
              {allColumns.map((col) => (
                <label key={col} className="flex items-center space-x-2 bg-black/30 px-3 py-2 rounded-lg">
                  <input
                    type="checkbox"
                    checked={dropColumns.includes(col)}
                    onChange={() => toggleColumn(col)}
                  />
                  <span>{col}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <button
          disabled={cleaningLoading}
          onClick={runCleaning}
          className="mt-6 px-6 py-3 bg-indigo-600 rounded-xl hover:scale-105 transition"
        >
          {cleaningLoading ? "Cleaning..." : "Run Smart Cleaning"}
        </button>
      </Section>

      {/* CLEANING RESULTS */}
      {cleanResult && (
        <>
          <Section title="Cleaning Results">
            <ComparisonChart
              before={cleanResult.score_before}
              after={cleanResult.score_after}
              rowsRemoved={cleanResult.rows_removed}
            />
            <AIReview review={cleanResult.ai_review_after} />
            <button
              onClick={handleDownload}
              className="mt-6 bg-green-600 px-5 py-2 rounded-lg"
            >
              Download Cleaned CSV
            </button>
          </Section>

          <Section title="Cleaned Dataset Preview">
            <DataTable
              rows={rows}
              columns={columns}
              page={page}
              totalRows={totalRows}
              loadPreview={loadPreview}
            />
          </Section>
        </>
      )}
    </div>
  );
}

/* COMPONENTS */

function Section({ title, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8"
    >
      <h2 className="text-2xl mb-6 font-semibold">{title}</h2>
      {children}
    </motion.div>
  );
}

function MLBadge({ readiness }) {
  if (!readiness) return null;
  const colorMap = {
    red: "text-red-400 bg-red-500/20",
    orange: "text-orange-400 bg-orange-500/20",
    blue: "text-blue-400 bg-blue-500/20",
    green: "text-green-400 bg-green-500/20",
  };
  return (
    <div className={`inline-block mt-6 px-4 py-2 rounded-full ${colorMap[readiness.color]}`}>
      {readiness.label}
    </div>
  );
}

function DataTypeBlock({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="mb-6">
      <h3 className="text-indigo-400 mb-3">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {items.map((col) => (
          <span key={col} className="bg-indigo-500/20 px-3 py-1 rounded-full text-sm">
            {col}
          </span>
        ))}
      </div>
    </div>
  );
}

function AIReview({ review }) {
  if (!review) return null;
  return (
    <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-6 space-y-2">
      {review.map((line, index) => (
        <div key={index}>• {line}</div>
      ))}
    </div>
  );
}

function ComparisonChart({ before, after, rowsRemoved }) {
  const data = [
    { name: "Before", value: before },
    { name: "After", value: after },
  ];
  return (
    <>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Bar dataKey="value" radius={[10,10,0,0]}>
            <Cell fill="#6366f1" />
            <Cell fill="#10b981" />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 text-green-400">
        Rows Removed: {rowsRemoved}
      </div>
    </>
  );
}

function CorrelationHeatmap({ matrix }) {
  if (!matrix) return null;
  const columns = Object.keys(matrix);
  return (
    <div className="overflow-x-auto">
      <table className="text-xs border border-white/10">
        <thead className="bg-indigo-500/20">
          <tr>
            <th></th>
            {columns.map((col) => (
              <th key={col} className="p-3">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {columns.map((row) => (
            <tr key={row}>
              <td className="p-3 font-bold">{row}</td>
              {columns.map((col) => {
                const val = matrix[row][col] || 0;
                const bg =
                  val >= 0
                    ? `rgba(16,185,129,${Math.abs(val)})`
                    : `rgba(239,68,68,${Math.abs(val)})`;
                return (
                  <td key={col} style={{ backgroundColor: bg }} className="p-3 text-center">
                    {val.toFixed(2)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StrongCorrelationPairs({ pairs }) {
  if (!pairs || pairs.length === 0) return null;
  return (
    <div className="mt-4">
      <h3 className="text-red-400 mb-3">Strong Correlations</h3>
      {pairs.map((pair, index) => (
        <div key={index} className="bg-red-500/20 px-4 py-2 rounded mb-2">
          {pair.feature_1} ↔ {pair.feature_2} ({pair.correlation})
        </div>
      ))}
    </div>
  );
}

function Toggle({ label, value, setValue }) {
  return (
    <label className="flex items-center justify-between bg-black/30 px-4 py-3 rounded-lg">
      <span>{label}</span>
      <input type="checkbox" checked={value} onChange={(e) => setValue(e.target.checked)} />
    </label>
  );
}

function DataTable({ rows, columns, page, totalRows, loadPreview }) {
  const totalPages = Math.ceil(totalRows / PAGE_SIZE);
  if (!rows.length) return <div>No data available</div>;
  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border border-white/10">
          <thead className="bg-indigo-500/20">
            <tr>
              {columns.map((col) => (
                <th key={col} className="px-3 py-2 text-left">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="odd:bg-white/5 hover:bg-indigo-500/20">
                {columns.map((col) => (
                  <td key={col} className="px-3 py-2">{row[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between mt-6">
        <button
          disabled={page === 1}
          onClick={() => loadPreview(page - 1)}
          className="px-4 py-2 bg-indigo-600 rounded disabled:bg-gray-600"
        >
          Previous
        </button>

        <span>Page {page} of {totalPages}</span>

        <button
          disabled={page === totalPages}
          onClick={() => loadPreview(page + 1)}
          className="px-4 py-2 bg-indigo-600 rounded disabled:bg-gray-600"
        >
          Next
        </button>
      </div>
    </>
  );
}

function StatsGrid({ profile }) {
  if (!profile) return null;

  const stats = [
    { label: "Rows", value: profile.rows },
    { label: "Columns", value: profile.columns },
    { label: "Missing Count", value: profile.missing_count },
    { label: "Duplicate Count", value: profile.duplicate_count },
    { label: "Quality Score", value: profile.quality_score },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
      {stats.map((item) => (
        <div
          key={item.label}
          className="bg-gradient-to-br from-white/10 to-white/5 border border-white/20 shadow-lg shadow-indigo-500/10 rounded-2xl p-6 text-center hover:scale-105 transition duration-300"
        >
          <div className="text-sm text-gray-400">{item.label}</div>
          <div className="text-2xl font-bold mt-2">{item.value}</div>
        </div>
      ))}
    </div>
  );
}