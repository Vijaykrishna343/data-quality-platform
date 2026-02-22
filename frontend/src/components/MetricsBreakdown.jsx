import { motion } from "framer-motion";

export default function MetricsBreakdown({ beforeMetrics, afterMetrics }) {
  if (!beforeMetrics || !afterMetrics) return null;

  const metrics = Object.keys(beforeMetrics);

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-8">
        Quality Metrics Breakdown
      </h2>

      <div className="grid md:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/5 border border-white/10 rounded-xl p-5"
          >
            <h3 className="text-sm text-white/60 capitalize mb-2">
              {metric.replace("_", " ")}
            </h3>

            <p className="text-lg text-orange-400">
              Before: {beforeMetrics[metric]}%
            </p>

            <p className="text-lg text-green-400">
              After: {afterMetrics[metric]}%
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}