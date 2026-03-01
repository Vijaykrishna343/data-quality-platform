import React, { useEffect, useState } from "react";
import { motion, animate } from "framer-motion";
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
  const [animatedAfterScore, setAnimatedAfterScore] = useState(0);
  const [animatedImprovement, setAnimatedImprovement] = useState(0);

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

      animate(0, res.data.score_after, {
        duration: 1.2,
        onUpdate: (latest) => setAnimatedAfterScore(latest.toFixed(2)),
      });

      animate(0, res.data.improvement, {
        duration: 1.2,
        onUpdate: (latest) => setAnimatedImprovement(latest.toFixed(2)),
      });

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
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#0f172a] via-[#1e1b4b] to-[#0f172a] text-white p-10 space-y-14">

  {/* Animated Background Glow */}
  <div className="absolute inset-0 -z-10">
    <motion.div
      animate={{ 
        x: [0, 100, -100, 0], 
        y: [0, -80, 80, 0] 
      }}
      transition={{ 
        duration: 20, 
        repeat: Infinity, 
        ease: "linear" 
      }}
      className="absolute w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-3xl"
    />
  </div>

      {/* OVERVIEW */}
      <Section title="Dataset Overview">
        <StatsGrid
  profile={analytics.profile}
  updatedScore={cleanResult ? cleanResult.score_after : null}
  outlierPercentage={analytics.outliers?.overall_percentage}
  noisyPercentage={analytics.outliers?.noisy_percentage}
/>
        <MLBadge
  readiness={
    cleanResult
      ? cleanResult.ml_readiness_after
      : analytics.ml_readiness
  }
/>
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
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6 }}
  >
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={importanceData}>
        <XAxis dataKey="name" angle={-30} textAnchor="end" height={80} />
        <YAxis />
        <Tooltip />
        <Bar
          dataKey="value"
          radius={[10, 10, 0, 0]}
          animationDuration={1200}
        >
          {importanceData.map((entry, index) => (
            <Cell key={index} fill="#6366f1" />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  </motion.div>
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
            <Toggle
              label="Handle Missing"
              value={handleMissing}
              setValue={setHandleMissing}
            />
            <Toggle
              label="Remove Duplicates"
              value={removeDuplicates}
              setValue={setRemoveDuplicates}
            />

            <div className="bg-white/5 border border-white/10 rounded-xl p-2 flex gap-2">
  {[
    { label: "None", value: "none" },
    { label: "IQR", value: "iqr" },
    { label: "Isolation", value: "isolation" },
  ].map((option) => {
    const active = outlierMethod === option.value;

    return (
      <motion.div
        key={option.value}
        whileTap={{ scale: 0.95 }}
        onClick={() => setOutlierMethod(option.value)}
        className={`flex-1 text-center py-2 rounded-lg cursor-pointer text-sm font-medium transition-all duration-300
          ${
            active
              ? "bg-indigo-500/30 text-white shadow-lg shadow-indigo-500/30"
              : "text-gray-400 hover:bg-indigo-500/20"
          }`}
      >
        {option.label}
      </motion.div>
    );
  })}
</div>
          </div>

          <div className="md:col-span-2">
            <h3 className="text-gray-400 mb-4">Drop Columns</h3>

            <div className="flex flex-wrap gap-3 max-h-72 overflow-y-auto">
              {allColumns.map((col) => {
                const selected = dropColumns.includes(col);

                return (
                  <motion.div
                    key={col}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => toggleColumn(col)}
                    className={`cursor-pointer px-4 py-2 rounded-full border text-sm font-medium transition-all duration-300
                      ${
                        selected
                          ? "bg-red-500/20 border-red-400 text-red-300 shadow-lg shadow-red-500/20"
                          : "bg-white/5 border-white/20 hover:bg-indigo-500/20 hover:border-indigo-400"
                      }`}
                  >
                    {col}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

       <motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  disabled={cleaningLoading}
  onClick={runCleaning}
  className="mt-6 px-6 py-3 rounded-xl font-semibold bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 shadow-lg shadow-indigo-500/30 transition-all duration-300"
>
  {cleaningLoading ? "Cleaning..." : "Run Cleaning"}
</motion.button>
      </Section>

      {/* CLEANING RESULTS */}
      {cleanResult && (
        <>
          <Section title="Cleaning Results">
            <ComparisonChart
              before={cleanResult.score_before}
              after={cleanResult.score_after}
              rowsRemoved={
                cleanResult.rows_before - cleanResult.rows_after
              }
            />
            <motion.div
             initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 space-y-2"
>
          <div className="text-xl font-bold text-green-400">
            Final Score: {animatedAfterScore}
   </div>

    <div className="text-green-400 text-lg font-semibold">
    🚀 +{animatedImprovement}% Improvement
    </div>
</motion.div>

            <button
              onClick={handleDownload}
              className="mt-6 bg-green-600 px-5 py-2 rounded-lg hover:scale-105 transition"
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
/* ===================== COMPONENTS ===================== */

function Section({ title, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 25 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
       className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition duration-300"    >
      <h2 className="text-2xl mb-6 font-semibold">{title}</h2>
      {children}
    </motion.div>
  );
}

function MLBadge({ readiness }) {
  if (!readiness) return null;

  const colors = {
    red: "bg-red-500/20 text-red-400",
    orange: "bg-orange-500/20 text-orange-400",
    blue: "bg-blue-500/20 text-blue-400",
    green: "bg-green-500/20 text-green-400 shadow-lg shadow-green-500/30",
  };

  return (
    <motion.div
      initial={{ scale: 0.7, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className={`inline-block mt-6 px-5 py-2 rounded-full font-semibold ${colors[readiness.color]}`}
    >
      {readiness.label === "ML Ready" ? "🚀 ML Ready" : readiness.label}
    </motion.div>
  );
}

function StatsGrid({ profile, updatedScore, outlierPercentage, noisyPercentage }) {
  if (!profile) return null;

  const stats = [
    { label: "Rows", value: profile.rows },
    { label: "Columns", value: profile.columns },
    { label: "Missing Row Count", value: profile.missing_count },
    { label: "Duplicate Row Count", value: profile.duplicate_count },
    {
      label: "Outlier % (Cell-wise)",
      value:
        typeof outlierPercentage === "number"
          ? `${outlierPercentage.toFixed(2)}%`
          : "0%",
    },
    {
      label: "Noisy Data %",
      value:
        typeof noisyPercentage === "number"
          ? `${noisyPercentage.toFixed(2)}%`
          : "0%",
    },
    {
  label: "Quality Score",
  value: updatedScore !== null ? updatedScore : profile.quality_score,
},
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-7 gap-6">
      {stats.map((item) => {
        const isQuality = item.label === "Quality Score";

        return (
          <motion.div
  whileHover={{ scale: 1.07 }}
  transition={{ type: "spring", stiffness: 200 }}
  key={item.label}
  className={`
              rounded-2xl p-6 text-center transition duration-300
              ${
                isQuality
                  ? "bg-gradient-to-br from-green-500/20 to-indigo-500/20 border border-green-400/40 shadow-lg shadow-green-500/20"
                  : "bg-gradient-to-br from-white/10 to-white/5 border border-white/20"
              }
            `}
          >
            <div className="text-sm text-gray-400">{item.label}</div>
            <div
              className={`text-2xl font-bold mt-2 ${
                isQuality ? "text-green-400" : ""
              }`}
            >
              {item.value}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

function ComparisonChart({ before, after, rowsRemoved }) {
  return (
    <div className="space-y-8">

      <div>
        <h3 className="text-gray-400 mb-3">Quality Score Improvement</h3>

        <div className="bg-gray-800 rounded-full h-6 overflow-hidden">
          <motion.div
            initial={{ width: `${before}%` }}
            animate={{ width: `${after}%` }}
            transition={{ duration: 1.2 }}
            className="h-6 bg-gradient-to-r from-indigo-500 via-purple-500 to-green-500"
          />
        </div>

        <div className="flex justify-between mt-2 text-sm text-gray-400">
          <span>Before: {before}</span>
          <span>After: {after}</span>
        </div>
      </div>

      <div className="text-gray-400">
        Rows Removed: <span className="text-red-400">{rowsRemoved}</span>
      </div>
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
          <span
            key={col}
            className="bg-indigo-500/20 px-3 py-1 rounded-full text-sm"
          >
            {col}
          </span>
        ))}
      </div>
    </div>
  );
}

function AIReview({ review }) {
  const [open, setOpen] = useState(true);

  if (!review) return null;

  return (
    <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl overflow-hidden">
      <div
        onClick={() => setOpen(!open)}
        className="cursor-pointer px-6 py-4 flex justify-between items-center hover:bg-indigo-500/20 transition"
      >
        <span className="font-semibold">AI Insights</span>
        <span>{open ? "−" : "+"}</span>
      </div>

      <motion.div
        initial={false}
        animate={{ height: open ? "auto" : 0, opacity: open ? 1 : 0 }}
        className="px-6 overflow-hidden"
      >
        <div className="py-4 space-y-2">
          {review.map((line, index) => (
            <div key={index}>• {line}</div>
          ))}
        </div>
      </motion.div>
    </div>
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
                  <td
                    key={col}
                    style={{ backgroundColor: bg }}
                    className="p-3 text-center"
                  >
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
    <div className="flex items-center justify-between bg-white/5 border border-white/10 px-5 py-4 rounded-xl hover:bg-white/10 transition">
      <span className="text-sm font-medium">{label}</span>

      <div
        onClick={() => setValue(!value)}
        className={`w-14 h-7 flex items-center rounded-full p-1 cursor-pointer transition duration-300
          ${value ? "bg-green-500/40" : "bg-gray-600/40"}`}
      >
        <motion.div
          layout
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className="w-5 h-5 bg-white rounded-full shadow-md"
          style={{
            marginLeft: value ? "auto" : "0",
          }}
        />
      </div>
    </div>
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
                <th key={col} className="px-3 py-2 text-left">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="odd:bg-white/5 hover:bg-indigo-500/20">
                {columns.map((col) => (
                  <td key={col} className="px-3 py-2">
                    {row[col]}
                  </td>
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