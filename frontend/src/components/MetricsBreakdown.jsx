import { motion } from "framer-motion";

export default function MetricsBreakdown({ beforeMetrics, afterMetrics }) {
  if (
    !beforeMetrics ||
    !afterMetrics ||
    Object.keys(beforeMetrics).length === 0
  ) {
    return null;
  }

  const metrics = Object.keys(beforeMetrics);

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-8">
        Quality Metrics Breakdown
      </h2>

      <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => {
          const beforeValue = Number(beforeMetrics[metric]) || 0;
          const afterValue = Number(afterMetrics?.[metric]) || 0;

          const improvement = (afterValue - beforeValue).toFixed(2);

          return (
            <motion.div
              key={metric}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
              className="bg-white/5 border border-white/10 rounded-xl p-5"
            >
              <h3 className="text-sm text-white/60 capitalize mb-3">
                {metric.replace(/_/g, " ")}
              </h3>

              <p className="text-lg text-orange-400">
                Before: {beforeValue}%
              </p>

              <p className="text-lg text-green-400">
                After: {afterValue}%
              </p>

              <p
                className={`mt-2 text-sm ${
                  afterValue >= beforeValue
                    ? "text-green-400"
                    : "text-red-400"
                }`}
              >
                Change: {improvement > 0 ? "+" : ""}
                {improvement}%
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}