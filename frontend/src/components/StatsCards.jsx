import { motion } from "framer-motion";

export default function StatsCards({ data }) {

  if (!data?.quality_metrics) return null;

  const { missing_percentage, duplicate_count } = data.quality_metrics;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">

      <motion.div
        whileHover={{ scale: 1.05 }}
        className="bg-gray-800 p-6 rounded-xl shadow-xl text-center"
      >
        <h3 className="text-gray-400">Missing %</h3>
        <p className="text-3xl font-bold text-red-400">
          {missing_percentage}%
        </p>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.05 }}
        className="bg-gray-800 p-6 rounded-xl shadow-xl text-center"
      >
        <h3 className="text-gray-400">Duplicates</h3>
        <p className="text-3xl font-bold text-yellow-400">
          {duplicate_count}
        </p>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.05 }}
        className="bg-gray-800 p-6 rounded-xl shadow-xl text-center"
      >
        <h3 className="text-gray-400">Readiness</h3>
        <p className="text-2xl font-bold text-green-400">
          {data.readiness_status}
        </p>
      </motion.div>

    </div>
  );
}