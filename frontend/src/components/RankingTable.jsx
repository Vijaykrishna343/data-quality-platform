import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle } from "lucide-react";

export default function RankingTable({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }

  // Convert backend structure into usable score
  const formattedData = data.map((item) => {
    const missing = Number(item.missing_values) || 0;
    const unique = Number(item.unique_values) || 0;

    const score = Math.max(0, Math.min(100, unique - missing));

    return {
      column: item.column,
      score,
    };
  });

  // Sort by score descending
  const sortedData = formattedData.sort((a, b) => b.score - a.score);

  const getBadge = (score) => {
    if (score >= 70)
      return { label: "Good", color: "bg-green-500/20 text-green-400" };
    if (score >= 50)
      return { label: "Moderate", color: "bg-yellow-500/20 text-yellow-400" };
    return { label: "Poor", color: "bg-red-500/20 text-red-400" };
  };

  const getRecommendation = (score) => {
    if (score < 50)
      return {
        text: "Needs attention",
        icon: <AlertTriangle size={16} className="text-red-400" />,
      };
    return {
      text: "Keep",
      icon: <CheckCircle size={16} className="text-green-400" />,
    };
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-6">
        Rankings & Recommendations
      </h2>

      <div className="space-y-5">
        {sortedData.map((item, index) => {
          const badge = getBadge(item.score);
          const recommendation = getRecommendation(item.score);

          return (
            <motion.div
              key={item.column}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="grid grid-cols-4 items-center gap-6"
            >
              {/* Column Name */}
              <div className="text-white/80 font-medium truncate">
                {item.column}
              </div>

              {/* Score Bar */}
              <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.score}%` }}
                  transition={{ duration: 0.8 }}
                  className={`h-3 rounded-full ${
                    item.score >= 70
                      ? "bg-green-400"
                      : item.score >= 50
                      ? "bg-yellow-400"
                      : "bg-red-500"
                  }`}
                ></motion.div>
              </div>

              {/* Badge */}
              <div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}
                >
                  {badge.label}
                </span>
              </div>

              {/* Recommendation */}
              <div className="flex items-center gap-2 text-white/70 text-sm">
                {recommendation.icon}
                {recommendation.text}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}