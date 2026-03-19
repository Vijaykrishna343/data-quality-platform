import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";

export default function AISummaryPanel({ datasetId }) {

  const [data, setData] = useState(null);

  useEffect(() => {
    if (!datasetId) return;

    axios
      .get(`http://127.0.0.1:8000/summary/${datasetId}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));

  }, [datasetId]);

  if (!data) return null;

  return (
    <div className="mt-16">

      <h2 className="text-3xl font-bold mb-8 text-indigo-300">
        AI Executive Summary
      </h2>

      <div className="bg-gradient-to-br from-indigo-900/40 to-purple-900/40 
                      backdrop-blur-xl border border-white/20 
                      rounded-3xl p-8 shadow-xl space-y-4">

        {data.insights.map((text, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/5 p-4 rounded-xl"
          >
            {text}
          </motion.div>
        ))}

      </div>
    </div>
  );
}