import React, { useCallback, useEffect, useState } from "react";
import { motion, animate } from "framer-motion";
import { useParams } from "react-router-dom";
import {
  getAnalytics,
  simulateCleaning,
  fetchDatasetPage,
  downloadCleanedDataset,
  trainModel,
  getPlotUrl
} from "../services/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";
import {
  AlertOctagon,
  AlertTriangle,
  Info,
  CheckCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck
} from "lucide-react";

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
  const [loadError, setLoadError] = useState(null);
  const [fromCache, setFromCache] = useState(false);

  // Analytics loading progress
  const [analyticsProgress, setAnalyticsProgress] = useState(0);

  // Advanced Cleaning States
  const [missingMethod, setMissingMethod] = useState("smart");
  const [outlierMethod, setOutlierMethod] = useState("iqr");
  const [noisyMethod, setNoisyMethod] = useState("zscore");
  const [dropColumns, setDropColumns] = useState([]);
  const [outlierAction, setOutlierAction] = useState("fix");
  const [noisyAction, setNoisyAction] = useState("fix");
  const [hasExecuted, setHasExecuted] = useState(false);

  const [animatedAfterScore, setAnimatedAfterScore] = useState(0);
  const [animatedImprovement, setAnimatedImprovement] = useState(0);

  const loadPreview = useCallback(async (p = 1) => {
    const res = await fetchDatasetPage(datasetId, p, PAGE_SIZE);
    setRows(res.data.rows || []);
    setColumns(res.data.columns || []);
    setTotalRows(res.data.total_rows || 0);
    setPage(p);
  }, [datasetId]);

  const toggleColumn = (col) => {
    if (dropColumns.includes(col)) {
      setDropColumns(dropColumns.filter((c) => c !== col));
    } else {
      setDropColumns([...dropColumns, col]);
    }
  };

  const [loadingMessage, setLoadingMessage] = useState("Initializing intelligence engine...");

  // Simulate analytics loading progress steps when fetching
  const LOAD_STEPS = [
    { pct: 10, msg: "Connecting to dataset..." },
    { pct: 30, msg: "Reading dataset structure..." },
    { pct: 55, msg: "Calculating quality score..." },
    { pct: 75, msg: "Generating analytics report..." },
    { pct: 90, msg: "Building AI recommendations..." },
    { pct: 98, msg: "Finalising dashboard..." },
  ];

  const startLoadProgress = () => {
    let idx = 0;
    setAnalyticsProgress(5);
    setLoadingMessage(LOAD_STEPS[0].msg);
    const timer = setInterval(() => {
      idx = Math.min(idx + 1, LOAD_STEPS.length - 1);
      setAnalyticsProgress(LOAD_STEPS[idx].pct);
      setLoadingMessage(LOAD_STEPS[idx].msg);
      if (idx === LOAD_STEPS.length - 1) clearInterval(timer);
    }, 800);
    return timer;
  };

  const runCleaning = useCallback(async () => {
    setCleaningLoading(true);
    setHasExecuted(true);
    setLoadingMessage("Refining dataset quality...");
    try {
      // Simulate status changes for better UX
      setTimeout(() => setLoadingMessage("Applying imputation algorithms..."), 1000);
      setTimeout(() => setLoadingMessage("Verifying outlier thresholds..."), 2500);
      
      const res = await simulateCleaning(datasetId, {
        missing_method: missingMethod,
        outlier_method: outlierMethod,
        outlier_action: outlierAction,
        noisy_method: noisyMethod,
        noisy_action: noisyAction,
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
    } catch (error) {
      console.error("Cleaning failed", error);
    } finally {
      setCleaningLoading(false);
      setLoadingMessage("");
    }
  }, [
    datasetId,
    dropColumns,
    loadPreview,
    missingMethod,
    noisyAction,
    noisyMethod,
    outlierAction,
    outlierMethod,
  ]);

  const loadAnalytics = async (invalidate = false) => {
    setAnalytics(null);
    setLoadError(null);
    const progressTimer = startLoadProgress();

    try {
      const [anaRes] = await Promise.all([
        getAnalytics(datasetId, invalidate),
        loadPreview(1),
      ]);
      setAnalytics(anaRes.data);
      // If server returned a cached copy it resolves instantly
      setFromCache(!invalidate);
      setAnalyticsProgress(100);
      setLoadingMessage("Dashboard ready ✓");
    } catch (err) {
      console.error("Failed to load analytics:", err);
      setLoadError(err?.response?.data?.detail || "Failed to load dataset analytics.");
    } finally {
      clearInterval(progressTimer);
    }
  };

  useEffect(() => {
    if (!datasetId) return;
    loadAnalytics(false);
  }, [datasetId]); // eslint-disable-line react-hooks/exhaustive-deps

  // 🚀 Dynamic Cleaning Simulation (Debounced)
  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (analytics && hasExecuted) {
        runCleaning();
      }
    }, 1000);

    return () => clearTimeout(delayDebounceFn);
  }, [
    analytics,
    hasExecuted,
    missingMethod,
    outlierMethod,
    noisyMethod,
    dropColumns,
    outlierAction,
    noisyAction,
    runCleaning,
  ]);

  const handleDownload = async () => {
    await downloadCleanedDataset(datasetId);
  };
  
  if (loadError)
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-[#0f172a] text-white space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-500" />
        <h2 className="text-2xl font-bold">Error Loading Analytics</h2>
        <p className="text-gray-400 max-w-md text-center">{loadError}</p>
        <button 
          onClick={() => window.location.href = '/'}
          className="px-6 py-2 mt-4 bg-indigo-600 hover:bg-indigo-700 font-semibold rounded-lg transition"
        >
          Go Back Home
        </button>
      </div>
    );

  if (!analytics)
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-[#0f172a] text-white gap-6 px-8">
        <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
        <div className="text-lg font-bold tracking-widest uppercase text-indigo-300 animate-pulse">
          {loadingMessage}
        </div>
        {/* Progress bar */}
        <div className="w-full max-w-md">
          <div className="flex justify-between text-xs text-gray-500 mb-1 font-medium">
            <span>Processing…</span>
            <span>{analyticsProgress}%</span>
          </div>
          <div className="relative w-full h-2 bg-white/5 rounded-full overflow-hidden border border-white/10">
            <div
              className="absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out"
              style={{
                width: `${analyticsProgress}%`,
                background: "linear-gradient(90deg, #6366f1 0%, #a855f7 60%, #ec4899 100%)",
                boxShadow: "0 0 10px rgba(139,92,246,0.5)",
              }}
            />
          </div>
        </div>
        <p className="text-gray-600 text-xs">This may take a moment for large datasets…</p>
      </div>
    );

  const importanceData = Object.entries(
    analytics.importance || {}
  ).map(([key, value]) => ({ name: key, value }));

  const allColumns = [
    ...(analytics.data_types?.numeric || []),
    ...(analytics.data_types?.categorical || []),
    ...(analytics.data_types?.alphanumeric || []),
    ...(analytics.data_types?.boolean || []),
    ...(analytics.data_types?.datetime || []),
  ];
  const pointsFixed = cleanResult?.points_fixed ?? 0;
  const correctedWithoutDrops = pointsFixed > 0 && cleanResult?.rows_removed === 0;

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
        {/* Cache indicator + Refresh */}
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <div className="flex items-center gap-2">
            {fromCache ? (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
                Loaded from cache — instant ⚡
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-[11px] font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block" />
                Freshly computed
              </span>
            )}
          </div>
          <button
            onClick={() => loadAnalytics(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-gray-400 hover:text-white text-[11px] font-semibold transition-all duration-200"
            title="Force recompute analytics (bypass cache)"
          >
            🔄 Refresh Analytics
          </button>
        </div>
        <StatsGrid
          profile={analytics.profile}
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
        <DataTypeBlock title="Alphanumeric" items={analytics.data_types?.alphanumeric} />
        <DataTypeBlock title="Boolean" items={analytics.data_types?.boolean} />
        <DataTypeBlock title="Datetime" items={analytics.data_types?.datetime} />
      </Section>

      {/* PRE-PROCESSING REPORT */}
      {analytics.auto_clean_report && (
        <Section title="Pre-Processing Report">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-indigo-500/10 border border-indigo-400/30 rounded-xl p-6 shadow-lg shadow-indigo-500/10">
              <h3 className="text-gray-400 text-sm mb-2">Auto-Sorting Status</h3>
              <div className="text-lg font-medium text-indigo-300">
                {analytics.auto_clean_report.sort_message}
              </div>
            </div>
            <div className="bg-orange-500/10 border border-orange-400/30 rounded-xl p-6 shadow-lg shadow-orange-500/10">
              <h3 className="text-gray-400 text-sm mb-2">Found Duplicates</h3>
              <div className="text-lg font-medium text-orange-300">
                {analytics.auto_clean_report.duplicates_removed > 0 ? (
                  <>
                    <span className="font-bold text-orange-400 text-2xl mr-2">{analytics.auto_clean_report.duplicates_removed}</span>
                    duplicate rows were removed permanently.
                  </>
                ) : (
                  "No identical duplicate rows were found."
                )}
              </div>
            </div>
          </div>
        </Section>
      )}

      {/* IMPORTANCE */}
      <Section title="Column Importance">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={importanceData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#818cf8" stopOpacity={1} />
                  <stop offset="100%" stopColor="#4f46e5" stopOpacity={0.8} />
                </linearGradient>
              </defs>
              <Tooltip
                cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                content={<CustomTooltip />}
              />
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={false}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                domain={[0, 100]}
              />
              <Bar
                dataKey="value"
                fill="url(#barGradient)"
                radius={[8, 8, 0, 0]}
                animationDuration={1500}
                barSize={40}
              />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </Section>


      {/* CORRELATION */}
      <Section title="Correlation Analysis">
        <CorrelationHeatmap matrix={analytics.correlation?.matrix} />
        <StrongCorrelationPairs pairs={analytics.correlation?.strong_pairs} />
      </Section>

      {/* AI RECOMMENDATIONS (Restored) */}
      <Section title="AI Recommendation System">
        <AIReview review={analytics.ai_review} />
      </Section>

      {/* ATTRIBUTE DROPPING (Priority 1) */}
      <Section title="Drop Attributes">
        <p className="text-gray-400 mb-6 text-sm">
          Select attributes that you want to exclude from the final dataset and further analysis.
        </p>
        <div className="flex flex-wrap gap-3 max-h-72 overflow-y-auto p-1">
          {allColumns.map((col) => {
            const selected = dropColumns.includes(col);
            return (
              <motion.div
                key={col}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => toggleColumn(col)}
                className={`cursor-pointer px-4 py-2 rounded-xl border text-sm font-semibold transition-all duration-300 flex items-center gap-2
                  ${selected
                    ? "bg-red-500/20 border-red-500/50 text-red-300 shadow-lg shadow-red-500/10"
                    : "bg-white/5 border-white/10 hover:border-indigo-500/50 hover:bg-indigo-500/5 text-gray-300"
                  }`}
              >
                {selected ? <AlertOctagon className="w-3 h-3" /> : <div className="w-1.5 h-1.5 rounded-full bg-gray-500" />}
                {col}
              </motion.div>
            );
          })}
        </div>
      </Section>

      {/* CLEANING CONTROLS */}
      <Section title="Smart Cleaning Controls">
        <div className="space-y-10">

          {/* 1. Missing Data Handling */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-blue-500/20 rounded-lg">
                <ShieldCheck className="w-4 h-4 text-blue-400" />
              </div>
              <h3 className="text-gray-200 font-bold uppercase tracking-widest text-[10px]">Handle Missing Values</h3>
            </div>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
              {[
                { label: "None", value: "none", icon: <AlertOctagon className="w-3 h-3" /> },
                { label: "Mean", value: "mean", icon: <Info className="w-3 h-3" /> },
                { label: "Median", value: "median", icon: <Info className="w-3 h-3" /> },
                { label: "Mode", value: "mode", icon: <Info className="w-3 h-3" /> },
                { label: "KNN", value: "knn", icon: <Sparkles className="w-3 h-3" /> },
                { label: "Smart", value: "smart", icon: <Sparkles className="w-3 h-3" /> },
              ].map((m) => (
                <MethodButton
                  key={m.value}
                  active={missingMethod === m.value}
                  onClick={() => setMissingMethod(m.value)}
                  label={m.label}
                  icon={m.icon}
                />
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-10">
            {/* 2. Outlier Detection */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-orange-500/20 rounded-lg">
                    <AlertTriangle className="w-4 h-4 text-orange-400" />
                  </div>
                  <h3 className="text-gray-200 font-bold uppercase tracking-widest text-[10px]">Outlier Handling</h3>
                </div>
                <ActionToggle active={outlierAction} onClick={setOutlierAction} />
              </div>
              <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                {[
                  { label: "None", value: "none" },
                  { label: "IQR", value: "iqr" },
                  { label: "Isolation", value: "isolation" },
                  { label: "MAD", value: "mad" },
                  { label: "LOF", value: "lof" },
                  { label: "Hybrid", value: "hybrid" },
                ].map((m) => (
                  <MethodButton
                    key={m.value}
                    active={outlierMethod === m.value}
                    onClick={() => setOutlierMethod(m.value)}
                    label={m.label}
                  />
                ))}
              </div>
            </div>

            {/* 3. Noisy Data Detection (Conditional) */}
            {analytics.outliers?.noisy_percentage > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-purple-500/20 rounded-lg">
                      <Sparkles className="w-4 h-4 text-purple-400" />
                    </div>
                    <h3 className="text-gray-200 font-bold uppercase tracking-widest text-[10px]">Noisy Data Handling</h3>
                  </div>
                  <ActionToggle active={noisyAction} onClick={setNoisyAction} />
                </div>
                <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                  {[
                    { label: "None", value: "none" },
                    { label: "Z-Score", value: "zscore" },
                    { label: "MAD", value: "mad" },
                  ].map((m) => (
                    <MethodButton
                      key={m.value}
                      active={noisyMethod === m.value}
                      onClick={() => setNoisyMethod(m.value)}
                      label={m.label}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>

        <div className="mt-10 flex justify-end">
          <motion.button
            whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(79, 70, 229, 0.4)" }}
            whileTap={{ scale: 0.98 }}
            disabled={cleaningLoading}
            onClick={runCleaning}
            className="flex items-center gap-3 px-10 py-4 rounded-2xl font-black uppercase tracking-widest text-sm bg-gradient-to-r from-indigo-600 to-purple-600 shadow-xl shadow-indigo-500/20 transition-all duration-300 overflow-hidden relative group"
          >
            <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
            {cleaningLoading ? "Processing Optimization..." : "Execute Cleaning Pipeline"}
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        </div>
      </Section>

      {/* CLEANING RESULTS */}
      {cleanResult && (
        <>
          <Section title="Cleaning Results">

            {/* AFTER CLEANING SCORE CARD */}
            <div className="mb-8">
              {(() => {
                const score = cleanResult.score_after;
                let colorClasses = "bg-green-500/10 border-green-500/20 text-green-400 shadow-green-500/10";
                if (score < 60) colorClasses = "bg-red-500/10 border-red-500/20 text-red-400 shadow-red-500/10";
                else if (score < 85) colorClasses = "bg-orange-500/10 border-orange-500/20 text-orange-400 shadow-orange-500/10";

                return (
                  <div className={`${colorClasses} border rounded-xl p-6 text-center shadow-lg transition-all duration-500`}>
                    <div className="opacity-60 text-sm font-medium uppercase tracking-widest mb-1">
                      After Cleaning Score
                    </div>
                    <div className="text-4xl font-bold font-outfit mt-2">
                      {animatedAfterScore}
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* BEFORE vs AFTER CHART */}
            <ComparisonChart
              before={cleanResult.score_before}
              after={cleanResult.score_after}
              rowsRemoved={
                cleanResult.rows_before - cleanResult.rows_after
              }
            />

            {/* IMPROVEMENT SECTION & EFFICIENCY CARD */}
            <div className="grid md:grid-cols-2 gap-6 mt-12">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-green-500/5 border border-green-500/20 rounded-2xl p-8 flex flex-col items-center justify-center text-center space-y-2"
              >
                <div className="p-3 bg-green-500/20 rounded-full mb-2">
                  <Sparkles className="w-6 h-6 text-green-400" />
                </div>
                <div className="text-3xl font-bold text-green-400">
                  +{animatedImprovement}%
                </div>
                <div className="text-gray-400 text-sm font-medium uppercase tracking-widest">
                  Quality Optimization
                </div>
              </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`${correctedWithoutDrops ? 'bg-blue-500/5 border-blue-500/20 shadow-blue-500/5' : 'bg-red-500/5 border-red-500/20 shadow-red-500/5'} rounded-2xl p-8 flex flex-col items-center justify-center text-center space-y-2 transition-colors duration-500`}
                >
                  <div className={`p-3 ${correctedWithoutDrops ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'} rounded-full mb-2`}>
                  {correctedWithoutDrops ? <CheckCircle className="w-6 h-6" /> : <AlertOctagon className="w-6 h-6" />}
                  </div>
                  <div className={`text-3xl font-bold ${correctedWithoutDrops ? 'text-blue-400' : 'text-red-400'}`}>
                  {correctedWithoutDrops ? pointsFixed : cleanResult.rows_removed}
                  </div>
                  <div className="text-gray-400 text-sm font-medium uppercase tracking-widest">
                  {correctedWithoutDrops ? "Data Points Corrected" : "Redundant Rows Stripped"}
                  </div>
                </motion.div>
            </div>

            {/* DOWNLOAD BUTTON */}
            <div className="flex justify-center mt-8">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleDownload}
                className="bg-green-600 px-6 py-3 rounded-xl font-semibold shadow-lg shadow-green-500/20 hover:bg-green-700 transition"
              >
                Download Cleaned CSV
              </motion.button>
            </div>

          </Section>

          <MLSection datasetId={datasetId} columns={allColumns} />

          {/* CLEANED DATA PREVIEW */}
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

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-[#1e1b4b] border border-indigo-500/50 backdrop-blur-xl p-4 rounded-xl shadow-2xl">
        <div className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-1">Column Name</div>
        <div className="text-white font-bold text-lg mb-2">{data.name}</div>
        <div className="h-[1px] bg-white/10 w-full mb-2" />
        <div className="flex items-center gap-2">
          <div className="text-indigo-400 text-sm font-medium">Importance Score:</div>
          <div className="text-white font-bold">{data.value}%</div>
        </div>
      </div>
    );
  }
  return null;
}

function Section({ title, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.95 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: false, amount: 0.1 }}
      transition={{
        duration: 0.8,
        ease: [0.16, 1, 0.3, 1] // Custom spring-like ease
      }}
      className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition duration-300"
    >
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

function MethodButton({ label, active, onClick, icon }) {
  return (
    <motion.div
      whileTap={{ scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl cursor-pointer text-xs font-bold transition-all duration-300 border
        ${active
          ? "bg-indigo-500/20 border-indigo-400 text-white shadow-lg shadow-indigo-500/20"
          : "bg-white/5 border-white/5 text-gray-500 hover:bg-white/10 hover:border-white/10"
        }`}
    >
      {icon}
      {label}
    </motion.div>
  );
}

function ActionToggle({ active, onClick }) {
  return (
    <div className="flex bg-white/5 p-1 rounded-xl border border-white/10 w-fit">
      <button
        onClick={() => onClick("fix")}
        className={`px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all ${active === "fix" ? "bg-indigo-500 text-white shadow-lg" : "text-gray-500 hover:text-gray-300"
          }`}
      >
        FIX (IMPUTE)
      </button>
      <button
        onClick={() => onClick("remove")}
        className={`px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all ${active === "remove" ? "bg-red-500 text-white shadow-lg" : "text-gray-500 hover:text-gray-400"
          }`}
      >
        REMOVE (DROP ROW)
      </button>
    </div>
  );
}



function StatsGrid({ profile, outlierPercentage, noisyPercentage }) {
  if (!profile) return null;

  const stats = [
    { label: "Rows", value: profile.rows, icon: <ArrowRight className="w-3 h-3" /> },
    { label: "Columns", value: profile.columns, icon: <ArrowRight className="w-3 h-3" /> },
    { label: "Missing Rows", value: profile.missing_count, icon: <AlertOctagon className="w-3 h-3" /> },
    { label: "Duplicates", value: profile.duplicate_count, icon: <AlertOctagon className="w-3 h-3" /> },
    {
      label: "Outlier Percentage",
      value:
        typeof outlierPercentage === "number"
          ? `${outlierPercentage.toFixed(1)}%`
          : "0%",
      icon: <AlertTriangle className="w-3 h-3" />,
    },
    {
      label: "Noise Level",
      value:
        typeof noisyPercentage === "number"
          ? `${noisyPercentage.toFixed(1)}%`
          : "0%",
      icon: <Sparkles className="w-3 h-3" />,
    },
    {
      label: "Quality Score",
      value: profile.quality_score,
      isQuality: true
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-7 gap-4">
      {stats.map((item, index) => {
        let qualityClasses = "bg-white/5 border-white/5";
        let scoreTextColor = "text-white";

        if (item.isQuality) {
          const scoreValue = parseFloat(item.value);
          if (scoreValue < 60) {
            qualityClasses = "bg-red-500/10 border-red-500/20";
            scoreTextColor = "text-red-400";
          } else if (scoreValue < 85) {
            qualityClasses = "bg-orange-500/10 border-orange-500/20";
            scoreTextColor = "text-orange-400";
          } else {
            qualityClasses = "bg-green-500/10 border-green-500/20";
            scoreTextColor = "text-green-400";
          }
        }

        return (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: false }}
            transition={{ delay: index * 0.05, duration: 0.5 }}
            whileHover={{ y: -5, backgroundColor: "rgba(255,255,255,0.08)" }}
            className={`rounded-3xl p-5 border transition-all duration-300 ${qualityClasses}`}
          >
            <div className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest text-gray-500 mb-2">
              {item.label}
            </div>
            <div className={`text-xl font-outfit font-bold ${scoreTextColor}`}>
              {item.value}
            </div>
            {item.label === "Quality Score" && (
              <div className="mt-2 flex items-center gap-1 opacity-50">
                <div className="w-1 h-1 rounded-full bg-current" />
                <span className="text-[8px] font-bold uppercase tracking-tighter">Unified Index</span>
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}

function ComparisonChart({ before, after, rowsRemoved }) {
  const data = [
    { stage: "Pre-Clean", score: before, color: "#f87171" },
    { stage: "Post-Clean", score: after, color: "#34d399" }
  ];

  return (
    <div className="bg-white/[0.03] border border-white/5 rounded-[2.5rem] p-10 mb-8 relative overflow-hidden group">
      {/* Subtle Background Glow */}
      <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <div className="flex items-center justify-between mb-12">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold text-white tracking-tight">Quality Lift Analysis</h2>
          <p className="text-gray-500 text-[10px] uppercase font-black tracking-[0.2em]">Comparative Performance Delta</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-400" />
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Initial</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Optimized</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 40, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="beforeGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f87171" stopOpacity={1} />
              <stop offset="100%" stopColor="#ef4444" stopOpacity={0.6} />
            </linearGradient>
            <linearGradient id="afterGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#34d399" stopOpacity={1} />
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.6} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="stage"
            hide={true}
          />
          <YAxis
            domain={[0, 100]}
            hide={true}
          />
          <Tooltip
            cursor={{ fill: 'rgba(255,255,255,0.03)' }}
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const isAfter = payload[0].payload.stage === "Post-Clean";
                return (
                  <div className="bg-slate-900/90 backdrop-blur-md border border-white/10 p-4 rounded-2xl shadow-2xl">
                    <p className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-1">{payload[0].payload.stage}</p>
                    <p className={`text-2xl font-outfit font-black ${isAfter ? 'text-green-400' : 'text-red-400'}`}>
                      {payload[0].value} <span className="text-sm font-medium opacity-50">pts</span>
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar
            dataKey="score"
            radius={[20, 20, 15, 15]}
            barSize={140}
            animationDuration={1500}
            animationBegin={300}
          >
            <LabelList
              dataKey="stage"
              position="top"
              offset={20}
              content={({ x, y, width, value }) => (
                <text
                  x={x + width / 2}
                  y={y - 20}
                  fill="#fff"
                  textAnchor="middle"
                  className="text-[11px] font-black uppercase tracking-[0.2em] opacity-80"
                >
                  {value === "Pre-Clean" ? "Initial" : "Optimized"}
                </text>
              )}
            />
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={index === 0 ? "url(#beforeGrad)" : "url(#afterGrad)"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="text-center pt-10 border-t border-white/5">
        <div className="inline-flex items-center gap-10 px-10 py-5 rounded-3xl bg-white/[0.02] border border-white/5 shadow-inner">
          <div className="text-left leading-none">
            <div className="text-[10px] uppercase font-black tracking-widest text-gray-500 mb-2">Efficiency</div>
            <div className="text-2xl font-outfit font-black text-red-400">-{rowsRemoved} <span className="text-sm font-medium opacity-50">Rows</span></div>
          </div>
          <div className="w-[1px] h-10 bg-white/10" />
          <div className="text-left leading-none">
            <div className="text-[10px] uppercase font-black tracking-widest text-gray-500 mb-2">Lift Score</div>
            <div className="text-2xl font-outfit font-black text-green-400">+{(after - before).toFixed(1)} <span className="text-sm font-medium opacity-50">%</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
function DataTypeBlock({ title, items }) {
  if (!items || items.length === 0) return null;

  // Define colors based on data type to make it visually distinct
  const getColorClasses = (type) => {
    switch (type.toLowerCase()) {
      case "numeric":
        return "bg-blue-500/10 border-blue-500/30 text-blue-300 hover:bg-blue-500/20";
      case "categorical":
        return "bg-purple-500/10 border-purple-500/30 text-purple-300 hover:bg-purple-500/20";
      case "alphanumeric":
        return "bg-orange-500/10 border-orange-500/30 text-orange-300 hover:bg-orange-500/20";
      case "boolean":
        return "bg-green-500/10 border-green-500/30 text-green-300 hover:bg-green-500/20";
      case "datetime":
        return "bg-pink-500/10 border-pink-500/30 text-pink-300 hover:bg-pink-500/20";
      default:
        return "bg-indigo-500/10 border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/20";
    }
  };

  const colorClasses = getColorClasses(title);

  return (
    <div className="mb-8 last:mb-0">
      <div className="flex items-center gap-3 mb-4">
        <h3 className="text-lg font-medium text-gray-200">{title}</h3>
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-white/10 text-gray-400">
          {items.length}
        </span>
      </div>
      <div className="flex flex-wrap gap-2.5">
        {items.map((col) => (
          <motion.span
            whileHover={{ scale: 1.05, y: -2 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
            key={col}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors duration-300 cursor-default ${colorClasses} shadow-sm`}
          >
            {col}
          </motion.span>
        ))}
      </div>
    </div>
  );
}

function AIReview({ review }) {
  if (!review) return null;

  const levelConfig = {
    critical: {
      accent: "from-red-600 to-red-400",
      bg: "bg-red-500/10",
      border: "border-red-500/20",
      text: "text-red-400",
      icon: <AlertOctagon className="w-5 h-5" />,
      shadow: "hover:shadow-red-500/20"
    },
    warning: {
      accent: "from-orange-600 to-orange-400",
      bg: "bg-orange-500/10",
      border: "border-orange-500/20",
      text: "text-orange-400",
      icon: <AlertTriangle className="w-5 h-5" />,
      shadow: "hover:shadow-orange-500/20"
    },
    info: {
      accent: "from-blue-600 to-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
      text: "text-blue-400",
      icon: <Info className="w-5 h-5" />,
      shadow: "hover:shadow-blue-500/20"
    },
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2
      }
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.8 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 260,
        damping: 20
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2 bg-indigo-500/20 rounded-lg">
          <Sparkles className="w-5 h-5 text-indigo-400" />
        </div>
        <p className="text-gray-400 text-sm font-medium tracking-wide">
          Our AI analyzed your dataset and found <span className="text-white font-bold">{review.length} focus areas</span> for quality improvement.
        </p>
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: false, amount: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {review.map((item, index) => {
          const config = levelConfig[item.level] || levelConfig.info;
          return (
            <motion.div
              variants={cardVariants}
              whileHover={{ y: -10, scale: 1.05, transition: { duration: 0.2 } }}
              key={index}
              className={`relative overflow-hidden group border rounded-2xl p-6 transition-all duration-300 backdrop-blur-xl bg-white/5 ${config.border} ${config.shadow} flex flex-col justify-between`}
            >
              {/* Left Accent Strip */}
              <div className={`absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b ${config.accent}`} />

              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${config.bg} ${config.text}`}>
                    {config.icon}
                    {item.category}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="text-gray-500 text-[10px] font-bold uppercase tracking-widest flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                    Observation
                  </div>
                  <div className="text-white font-semibold leading-snug text-lg">
                    {item.insight}
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-5 border border-white/10 group-hover:border-indigo-500/30 transition-colors">
                  <div className="text-gray-500 text-[10px] font-bold uppercase tracking-widest mb-3">Recommended Fix</div>
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 p-1 bg-indigo-500/20 rounded text-indigo-400">
                      <ArrowRight className="w-4 h-4" />
                    </div>
                    <div className="text-indigo-200 text-sm font-medium leading-relaxed">
                      {item.action}
                    </div>
                  </div>
                </div>
              </div>

              {/* Decorative Subtle Background Circle */}
              <div className={`absolute -right-12 -top-12 w-32 h-32 rounded-full opacity-[0.03] bg-white group-hover:opacity-[0.07] transition-opacity`} />
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
}

function CorrelationHeatmap({ matrix }) {
  if (!matrix) return null;
  const columns = Object.keys(matrix);

  return (
    <div className="space-y-8">
      <div className="overflow-x-auto rounded-[2rem] border border-white/5 bg-white/[0.01]">
        <table className="w-full text-[10px] border-collapse">
          <thead>
            <tr className="bg-white/[0.02]">
              <th className="p-4 border-b border-r border-white/5"></th>
              {columns.map((col) => (
                <th key={col} className="p-4 border-b border-white/5 text-[#6366f1] font-black uppercase tracking-widest text-center">
                  {col.slice(0, 3)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {columns.map((row) => (
              <tr key={row}>
                <td className="p-4 font-black uppercase tracking-widest text-gray-500 border-r border-white/5 bg-white/[0.01]">
                  {row}
                </td>
                {columns.map((col) => {
                  const val = matrix[row][col] || 0;
                  const bg =
                    val >= 0
                      ? `rgba(99,102,241,${Math.abs(val) * 0.8})`
                      : `rgba(239,68,68,${Math.abs(val) * 0.8})`;
                  return (
                    <td
                      key={col}
                      style={{ backgroundColor: bg }}
                      className="p-4 text-center font-bold text-white border-b border-white/5"
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



function DataTable({ rows, columns, page, totalRows, loadPreview }) {
  const totalPages = Math.ceil(totalRows / PAGE_SIZE);
  if (!rows.length) return <div className="text-gray-500 py-10 text-center">No data records available</div>;

  return (
    <div className="space-y-6">
      <div className="overflow-x-auto rounded-3xl border border-white/5 bg-white/[0.02]">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-white/10 bg-white/[0.02]">
              {columns.map((col) => (
                <th key={col} className="px-6 py-4 font-black uppercase tracking-widest text-[#6366f1] whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {rows.map((row, i) => (
              <tr key={i} className="hover:bg-indigo-500/5 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-6 py-4 text-gray-400 font-medium">
                    {row[col] === null ? <span className="text-red-500/50">null</span> : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modern Pagination */}
      <div className="flex items-center justify-between px-2">
        <div className="text-[10px] font-black uppercase tracking-widest text-gray-500">
          Showing <span className="text-white">{rows.length}</span> of <span className="text-white">{totalRows}</span> records
        </div>
        <div className="flex gap-2">
          <button
            disabled={page === 1}
            onClick={() => loadPreview(page - 1)}
            className="p-2 rounded-xl bg-white/5 border border-white/10 disabled:opacity-30 hover:bg-white/10 transition"
          >
            <ArrowRight className="w-4 h-4 rotate-180" />
          </button>
          <div className="flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 px-4 rounded-xl text-xs font-bold">
            <span className="text-indigo-400">Page</span> {page} <span className="text-gray-600">/</span> {totalPages}
          </div>
          <button
            disabled={page === totalPages}
            onClick={() => loadPreview(page + 1)}
            className="p-2 rounded-xl bg-white/5 border border-white/10 disabled:opacity-30 hover:bg-white/10 transition"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}


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
              {metrics.mae !== undefined && (
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
                  <div className="text-xs text-gray-400 uppercase">MAE</div>
                  <div className="text-2xl font-bold">{metrics.mae.toFixed(4)}</div>
                </div>
              )}
              {metrics.r2_score !== undefined && (
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
                  <div className="text-xs text-gray-400 uppercase">R²</div>
                  <div className="text-2xl font-bold">{metrics.r2_score.toFixed(4)}</div>
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
                    {metrics.explainability?.plot_base64 && <img src={`data:image/png;base64,${metrics.explainability.plot_base64}`} alt="SHAP Summary" className="w-full h-auto rounded-lg border border-white/10 bg-white" />}
                  </div>
                  <div>
                    <h4 className="text-sm text-gray-400 uppercase tracking-widest mb-4">Feature Importance</h4>
                    {metrics.explainability?.bar_plot_base64 && <img src={`data:image/png;base64,${metrics.explainability.bar_plot_base64}`} alt="SHAP Bar" className="w-full h-auto rounded-lg border border-white/10 bg-white" />}
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
