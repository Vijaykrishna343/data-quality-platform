import { CircularProgressbar } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import { motion } from "framer-motion";

export default function QualitySection({ score }) {
  if (score === undefined) return null;

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 flex justify-between items-center">
      
      <div>
        <h2 className="text-xl font-semibold mb-2">
          Dataset Quality Score
        </h2>
        <p className="text-gray-400">
          Higher score indicates better dataset cleanliness.
        </p>
      </div>

      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.6 }}
        className="w-40"
      >
        <CircularProgressbar
          value={score}
          text={`${score}%`}
          styles={{
            path: { stroke: "#22c55e" },
            text: { fill: "#fff" },
            trail: { stroke: "#1e293b" }
          }}
        />
      </motion.div>
    </div>
  );
}