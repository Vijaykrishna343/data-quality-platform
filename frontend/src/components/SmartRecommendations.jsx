import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";

export default function SmartRecommendations({ datasetId, hasCleaned }) {

  const [data, setData] = useState(null);

  useEffect(() => {
    if (!datasetId) return;

    axios
      .get(`http://127.0.0.1:8000/recommend/${datasetId}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));

  }, [datasetId, hasCleaned]);

  if (!data) return null;

  const renderList = (list) => (
    list.length === 0 ? (
      <p className="text-green-400">No major issues detected 🎉</p>
    ) : (
      list.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white/5 p-4 rounded-xl border border-white/10 mb-3"
        >
          <p className="font-semibold text-indigo-300">
            {item.column}
          </p>
          <p className="text-red-400">
            {item.issue}
          </p>
          <p className="text-gray-400">
            {item.suggestion}
          </p>
        </motion.div>
      ))
    )
  );

  return (
    <div className="mt-12">

      <h2 className="text-2xl font-bold mb-6 text-indigo-300">
        Smart Cleaning Recommendations
      </h2>

      <div className="grid md:grid-cols-2 gap-10">

        {/* BEFORE */}
        <div>
          <h3 className="mb-4 text-yellow-400">
            Before Cleaning
          </h3>
          {renderList(data.before)}
        </div>

        {/* AFTER — Only show if cleaning done */}
        {hasCleaned && (
          <div>
            <h3 className="mb-4 text-green-400">
              After Cleaning
            </h3>
            {renderList(data.after)}
          </div>
        )}

      </div>

    </div>
  );
}