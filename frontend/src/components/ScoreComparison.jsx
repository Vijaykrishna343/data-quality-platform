import { motion } from "framer-motion";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

export default function ScoreComparison({ data }) {
  if (!data) return null;

  const before = Number(data.before_score) || 0;
  const after = Number(data.after_score) || 0;

  const improvementValue = after - before;
  const improvement = improvementValue.toFixed(2);

  const Card = ({ title, score, color }) => (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 w-full">
      <h3 className="text-center text-white/60 mb-6">{title}</h3>

      <div className="w-40 mx-auto">
        <CircularProgressbar
          value={score}
          maxValue={100}
          text={`${score}%`}
          styles={buildStyles({
            pathColor: color,
            textColor: color,
            trailColor: "#0f172a",
          })}
        />
      </div>

      <p className="text-center mt-4 text-white/70">
        Quality Score
      </p>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="grid md:grid-cols-2 gap-8">
        <Card title="Before Cleaning" score={before} color="#f97316" />
        <Card title="After Cleaning" score={after} color="#22c55e" />
      </div>

      {/* Improvement Badge */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center"
      >
        <span
          className={`px-5 py-2 rounded-full border ${
            improvementValue >= 0
              ? "bg-green-500/20 text-green-400 border-green-500/30"
              : "bg-red-500/20 text-red-400 border-red-500/30"
          }`}
        >
          Improvement: {improvementValue > 0 ? "+" : ""}
          {improvement}%
        </span>
      </motion.div>
    </div>
  );
}