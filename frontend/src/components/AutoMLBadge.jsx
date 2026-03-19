import { motion } from "framer-motion";

export default function AutoMLBadge({ score, badge, color }) {

  const colorMap = {
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    red: "bg-red-500"
  };

  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-xl text-center"
    >
      <h3 className="text-indigo-300 mb-4">
        AutoML Readiness
      </h3>

      <div
        className={`inline-block px-6 py-2 rounded-full text-white font-semibold ${colorMap[color]}`}
      >
        {badge}
      </div>

      <p className="mt-4 text-4xl font-bold text-indigo-400">
        {score}
      </p>
    </motion.div>
  );
}