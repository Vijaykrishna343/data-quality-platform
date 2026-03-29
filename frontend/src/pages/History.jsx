import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

export default function History() {
  const [data, setData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/history")
      .then((res) => setData(res.data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="min-h-screen p-10 bg-gradient-to-br from-[#0f172a] via-[#1e1b4b] to-black text-white">

      <h2 className="text-3xl font-bold mb-8 flex items-center gap-2">
        📊 Dataset History
      </h2>

      {data.length === 0 ? (
        <p className="text-gray-400">No datasets found</p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.map((item, index) => (
            <motion.div
              key={item.dataset_id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate(`/dashboard/${item.dataset_id}`)}
              className="cursor-pointer p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl hover:border-indigo-500 hover:bg-indigo-500/10 transition-all duration-300 shadow-lg"
            >
              {/* Dataset Name */}
              <h3 className="text-lg font-semibold mb-2">
                {item.name}
              </h3>

              {/* Meta Info */}
              <p className="text-xs text-gray-400">
                ID: {item.dataset_id}
              </p>
              <p className="text-xs text-gray-400 mb-3">
                Date: {new Date(item.created_at).toLocaleString()}
              </p>

              {/* Analysis Data */}
              {item.analysis?.profile ? (
                <div className="space-y-1 text-sm">
                  <p>⭐ Quality Score: <span className="text-indigo-400">{item.analysis.profile.quality_score}</span></p>
                  <p>📊 Rows: {item.analysis.profile.rows}</p>
                  <p>📈 Columns: {item.analysis.profile.columns}</p>
                </div>
              ) : (
                <p className="text-yellow-400 text-sm mt-2">
                  ⚠ No analysis yet
                </p>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}