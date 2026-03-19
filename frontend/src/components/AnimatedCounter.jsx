import { motion } from "framer-motion";

export default function AnimatedCounter({ value }) {
  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="text-5xl font-bold text-indigo-400"
    >
      {value}
    </motion.span>
  );
}