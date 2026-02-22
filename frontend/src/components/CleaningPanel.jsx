import { useState } from "react";
import { motion } from "framer-motion";
import { Zap } from "lucide-react";

export default function CleaningPanel({ onRunAnalysis, loading }) {
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [missingStrategy, setMissingStrategy] = useState("Smart");
  const [outlierMethod, setOutlierMethod] = useState("IQR");

  const missingOptions = ["Smart", "Mean", "Median", "Mode", "Drop"];
  const outlierOptions = ["None", "IQR", "Isolation Forest"];

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-8">
        Cleaning Configuration
      </h2>

      {/* Remove Duplicates */}
      <div className="flex items-center justify-between mb-8">
        <span className="text-white/80 font-medium">
          Remove Duplicates
        </span>

        <div
          onClick={() => setRemoveDuplicates(!removeDuplicates)}
          className={`w-14 h-7 flex items-center rounded-full cursor-pointer transition-all duration-300 ${
            removeDuplicates ? "bg-cyan-500" : "bg-white/20"
          }`}
        >
          <motion.div
            layout
            className="w-6 h-6 bg-white rounded-full"
            animate={{ x: removeDuplicates ? 28 : 2 }}
            transition={{ type: "spring", stiffness: 300 }}
          />
        </div>
      </div>

      {/* Missing Strategy */}
      <div className="mb-8">
        <h3 className="text-sm text-white/60 mb-3 uppercase tracking-wider">
          Missing Value Strategy
        </h3>

        <div className="grid md:grid-cols-5 gap-3">
          {missingOptions.map((option) => (
            <button
              key={option}
              onClick={() => setMissingStrategy(option)}
              className={`py-2 rounded-lg transition-all duration-300 ${
                missingStrategy === option
                  ? "bg-cyan-500 text-white"
                  : "bg-white/10 text-white/60 hover:bg-white/20"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      {/* Outlier Detection */}
      <div className="mb-10">
        <h3 className="text-sm text-white/60 mb-3 uppercase tracking-wider">
          Outlier Detection
        </h3>

        <div className="grid md:grid-cols-3 gap-3">
          {outlierOptions.map((option) => (
            <button
              key={option}
              onClick={() => setOutlierMethod(option)}
              className={`py-2 rounded-lg transition-all duration-300 ${
                outlierMethod === option
                  ? "bg-cyan-500 text-white"
                  : "bg-white/10 text-white/60 hover:bg-white/20"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      {/* Run Button */}
      <motion.button
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={() =>
          onRunAnalysis({
            removeDuplicates,
            missingStrategy,
            outlierMethod,
          })
        }
        disabled={loading}
        className="w-full py-4 rounded-xl font-semibold flex items-center justify-center gap-3 bg-gradient-to-r from-cyan-500 to-purple-500 shadow-lg hover:shadow-cyan-500/40 transition-all duration-300 disabled:opacity-50"
      >
        <Zap size={18} />
        {loading ? "Running Analysis..." : "Run Analysis"}
      </motion.button>
    </div>
  );
}