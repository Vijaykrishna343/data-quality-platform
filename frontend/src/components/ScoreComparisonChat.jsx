import { motion } from "framer-motion";

export default function ScoreComparisonChart({ before, after }) {

  if (!before && !after) return null;

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-xl mt-10">

      <h3 className="text-xl mb-6 text-indigo-300">
        Cleaning Impact Comparison
      </h3>

      <div className="space-y-6">

        {/* BEFORE */}
        <div>
          <p className="mb-2">Before Cleaning ({before})</p>
          <div className="w-full bg-gray-800 rounded-full h-4">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${before}%` }}
              transition={{ duration: 1 }}
              className="h-4 bg-red-500 rounded-full"
            />
          </div>
        </div>

        {/* AFTER */}
        <div>
          <p className="mb-2">After Cleaning ({after})</p>
          <div className="w-full bg-gray-800 rounded-full h-4">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${after}%` }}
              transition={{ duration: 1 }}
              className="h-4 bg-green-500 rounded-full"
            />
          </div>
        </div>

      </div>

    </div>
  );
}