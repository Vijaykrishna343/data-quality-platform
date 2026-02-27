import { useState } from "react";
import { motion } from "framer-motion";

export default function CleaningControls({ onRun }) {

  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [handleMissing, setHandleMissing] = useState("mean");
  const [removeOutliers, setRemoveOutliers] = useState(true);

  const handleSubmit = () => {
    onRun({
      remove_duplicates: removeDuplicates,
      handle_missing: handleMissing,
      remove_outliers: removeOutliers
    });
  };

  return (
    <motion.div
      className="bg-gray-900 p-6 rounded-2xl shadow-2xl mb-8"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold mb-4">
        Cleaning Controls
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div>
          <label className="block mb-2">Handle Missing Values</label>
          <select
            value={handleMissing}
            onChange={(e) => setHandleMissing(e.target.value)}
            className="w-full p-2 bg-gray-800 rounded-lg"
          >
            <option value="mean">Fill with Mean</option>
            <option value="median">Fill with Median</option>
            <option value="mode">Fill with Mode</option>
            <option value="drop">Drop Rows</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={removeDuplicates}
            onChange={() => setRemoveDuplicates(!removeDuplicates)}
          />
          <span>Remove Duplicates</span>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={removeOutliers}
            onChange={() => setRemoveOutliers(!removeOutliers)}
          />
          <span>Remove Outliers</span>
        </div>

      </div>

      <button
        onClick={handleSubmit}
        className="mt-6 bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-xl transition"
      >
        Run Analysis
      </button>
    </motion.div>
  );
}