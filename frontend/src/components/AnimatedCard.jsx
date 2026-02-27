import { motion } from "framer-motion";

export default function AnimatedCard({ children, className = "" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className={`
        p-6 rounded-2xl shadow-md
        bg-white dark:bg-gray-800
        text-gray-900 dark:text-white
        transition-colors duration-300
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
}