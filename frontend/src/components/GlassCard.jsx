import { motion } from "framer-motion";

function GlassCard({ children, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ scale: 1.02 }}
      className="
        bg-white/5
        backdrop-blur-lg
        border border-white/10
        rounded-2xl
        p-6
        shadow-lg
        hover:shadow-blue-500/20
        transition-all
        duration-300
      "
    >
      {children}
    </motion.div>
  );
}

export default GlassCard;