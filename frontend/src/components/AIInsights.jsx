import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export default function AIInsights({ insights }) {
  if (!insights || insights.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-purple-500/10 to-cyan-500/10 backdrop-blur-xl border border-white/10 rounded-2xl p-8"
    >
      <div className="flex items-center gap-3 mb-4">
        <Sparkles className="text-purple-400" />
        <h2 className="text-xl font-semibold">
          AI Insights
        </h2>
      </div>

      <ul className="space-y-3 text-gray-300">
        {insights.map((item, i) => (
          <li key={i} className="flex gap-2">
            <span className="text-cyan-400">•</span>
            {item}
          </li>
        ))}
      </ul>
    </motion.div>
  );
}