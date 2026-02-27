import { motion } from "framer-motion";

function ScoreComparison({ before, after }) {
  const improvement = after - before;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="text-center"
    >
      <p className="text-red-400 text-lg">Before: {before}</p>
      <p className="text-green-400 text-lg">After: {after}</p>

      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${improvement}%` }}
        transition={{ duration: 1 }}
        className="h-3 bg-green-500 rounded mt-3"
      />
    </motion.div>
  );
}

export default ScoreComparison;