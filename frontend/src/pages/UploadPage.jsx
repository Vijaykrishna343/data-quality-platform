import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFile, pollTaskStatus } from "../services/api";

/* ─── Stage metadata ──────────────────────────────────────────────────────── */
const STAGES = [
  { key: "uploading",  label: "Uploading file",            pct: 5  },
  { key: "reading",    label: "Reading dataset",            pct: 20 },
  { key: "cleaning",   label: "Running cleaning pipeline",  pct: 45 },
  { key: "scoring",    label: "Calculating quality score",  pct: 65 },
  { key: "analytics",  label: "Generating analytics report",pct: 85 },
  { key: "completed",  label: "Completed ✓",               pct: 100 },
];

/* ─── Helpers ─────────────────────────────────────────────────────────────── */
function humanSize(bytes) {
  if (!bytes) return "";
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

/* ─── Sub-components ──────────────────────────────────────────────────────── */

function ProgressBar({ pct }) {
  return (
    <div className="relative w-full h-3 bg-white/5 rounded-full overflow-hidden border border-white/10">
      <div
        className="absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out"
        style={{
          width: `${pct}%`,
          background:
            "linear-gradient(90deg, #6366f1 0%, #a855f7 60%, #ec4899 100%)",
          boxShadow: "0 0 12px rgba(139,92,246,0.6)",
        }}
      />
    </div>
  );
}

function StepIndicator({ stage }) {
  const currentIdx = STAGES.findIndex((s) => s.key === stage);

  return (
    <div className="flex flex-col gap-1.5 w-full mt-3">
      {STAGES.map((s, i) => {
        const isDone    = i < currentIdx;
        const isActive  = i === currentIdx;
        const isPending = i > currentIdx;

        return (
          <div
            key={s.key}
            className={`flex items-center gap-3 px-3 py-2 rounded-xl transition-all duration-300 ${
              isActive
                ? "bg-indigo-500/15 border border-indigo-400/40"
                : isDone
                ? "opacity-60"
                : "opacity-25"
            }`}
          >
            {/* Dot */}
            <div
              className={`w-2.5 h-2.5 rounded-full flex-shrink-0 transition-all duration-300 ${
                isDone
                  ? "bg-green-400"
                  : isActive
                  ? "bg-indigo-400 animate-pulse"
                  : "bg-white/20"
              }`}
            />
            <span
              className={`text-xs font-semibold tracking-wide ${
                isActive ? "text-indigo-300" : isDone ? "text-green-400" : "text-gray-500"
              }`}
            >
              {s.label}
            </span>
            {isDone && (
              <span className="ml-auto text-green-400 text-xs font-bold">✓</span>
            )}
            {isActive && (
              <span className="ml-auto text-[10px] text-indigo-400 font-bold uppercase tracking-widest animate-pulse">
                Running…
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ─── Main Component ──────────────────────────────────────────────────────── */

const UploadPage = () => {
  const [selectedFile, setSelectedFile]   = useState(null);
  const [dragActive,   setDragActive]     = useState(false);
  const [loading,      setLoading]        = useState(false);
  const [uploadPct,    setUploadPct]      = useState(0);
  const [stage,        setStage]          = useState("uploading");
  const [progress,     setProgress]       = useState(0);
  const [statusMsg,    setStatusMsg]      = useState("");
  const [error,        setError]          = useState("");
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setError("");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a CSV file before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    setError("");
    setStage("uploading");
    setProgress(5);
    setStatusMsg("Uploading file…");

    try {
      /* ── 1. Upload ── */
      const response = await uploadFile(formData, (pct) => {
        setUploadPct(pct);
      });

      const data = response.data;

      /* ── 2. Large file → async polling ── */
      if (data.mode === "async") {
        const taskId = data.task_id;

        await pollTaskStatus(
          taskId,
          (s, p, msg) => {
            setStage(s);
            setProgress(p);
            setStatusMsg(msg);
          },
          2000
        );

        // Retrieve final dataset_id from completed task
        const statusRes  = await import("../services/api").then((m) =>
          m.default.get(`/upload/status/${taskId}`)
        );
        const datasetId  = statusRes.data?.result?.dataset_id;
        if (!datasetId) throw new Error("Could not retrieve dataset ID after processing");

        navigate(`/dashboard/${datasetId}`);
        return;
      }

      /* ── 3. Small file → direct ── */
      setStage("completed");
      setProgress(100);
      setStatusMsg("Completed ✓");
      navigate(`/dashboard/${data.dataset_id}`);

    } catch (err) {
      console.error(err);
      const msg =
        err.response?.data?.detail || err.message || "Upload failed. Please try a valid CSV.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const fileSizeLabel = selectedFile ? humanSize(selectedFile.size) : "";
  const isLargeFile   = selectedFile ? selectedFile.size > 5 * 1024 * 1024 : false;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-black flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-xl">

        {/* Card */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-10 shadow-2xl shadow-indigo-900/30">

          {/* Header */}
          <h1 className="text-3xl font-bold text-white text-center mb-2">
            Upload Your Dataset
          </h1>
          <p className="text-center text-gray-500 text-sm mb-8">
            CSV files up to 200 MB supported &bull; Large files processed in background
          </p>

          {/* Drop Zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300 cursor-pointer ${
              dragActive
                ? "border-purple-400 bg-purple-500/10 scale-[1.01]"
                : selectedFile
                ? "border-indigo-400/60 bg-indigo-500/5"
                : "border-white/20 hover:border-white/40"
            }`}
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="fileUpload"
            />
            <label htmlFor="fileUpload" className="cursor-pointer">
              {selectedFile ? (
                <div className="space-y-1">
                  <div className="text-green-400 font-semibold text-lg">
                    {selectedFile.name}
                  </div>
                  <div className="text-gray-500 text-sm">
                    {fileSizeLabel}
                    {isLargeFile && (
                      <span className="ml-2 px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 text-xs font-bold">
                        Large file — async mode
                      </span>
                    )}
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-3xl">
                    📁
                  </div>
                  <p className="text-gray-300 text-sm">
                    Drag &amp; drop a CSV file here, or{" "}
                    <span className="text-indigo-400 font-semibold underline underline-offset-2">
                      click to browse
                    </span>
                  </p>
                </div>
              )}
            </label>
          </div>

          {/* Error */}
          {error && (
            <div className="mt-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm text-center">
              {error}
            </div>
          )}

          {/* Progress Section */}
          {loading && (
            <div className="mt-8 space-y-4">
              {/* Upload byte progress */}
              {uploadPct > 0 && uploadPct < 100 && (
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-gray-500 font-medium">
                    <span>Uploading bytes</span>
                    <span>{uploadPct}%</span>
                  </div>
                  <ProgressBar pct={uploadPct} />
                </div>
              )}

              {/* Pipeline progress */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-indigo-300 font-bold">
                  <span>{statusMsg}</span>
                  <span>{progress}%</span>
                </div>
                <ProgressBar pct={progress} />
              </div>

              {/* Step indicator — only shown for async large-file mode */}
              {isLargeFile && <StepIndicator stage={stage} />}
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={loading}
            id="uploadBtn"
            className="w-full mt-8 py-4 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold uppercase tracking-widest text-xs hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-indigo-500/20"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing…
              </span>
            ) : (
              "Secure Upload & Smart Analyze"
            )}
          </button>
        </div>

        {/* Feature chips */}
        <div className="flex flex-wrap justify-center gap-3 mt-6">
          {[
            "⚡ Chunked Upload",
            "🔄 Real-Time Progress",
            "🤖 Auto Cleaning",
            "📊 Instant Analytics",
            "🔒 Secure Processing",
          ].map((f) => (
            <div
              key={f}
              className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-gray-400 text-[11px] font-medium"
            >
              {f}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UploadPage;