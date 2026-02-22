import { motion } from "framer-motion";
import { Database, Columns, Copy } from "lucide-react";

export default function StatsCards({ data }) {
  // Safety guard
  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }

  const rows = data.length;
  const columns = Object.keys(data[0] || {}).length;

  const duplicates =
    data.length -
    new Set(data.map((row) => JSON.stringify(row))).size;

  const stats = [
    {
      label: "Total Rows",
      value: rows,
      icon: <Database size={20} className="text-cyan-400" />,
      color: "bg-cyan-500/20",
    },
    {
      label: "Columns",
      value: columns,
      icon: <Columns size={20} className="text-purple-400" />,
      color: "bg-purple-500/20",
    },
    {
      label: "Duplicate Rows",
      value: duplicates,
      icon: <Copy size={20} className="text-yellow-400" />,
      color: "bg-yellow-500/20",
    },
  ];

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6"
        >
          <div className={`p-3 rounded-xl w-fit ${stat.color}`}>
            {stat.icon}
          </div>

          <h3 className="text-2xl font-bold mt-4">
            {stat.value.toLocaleString()}
          </h3>

          <p className="text-white/50 text-sm mt-1">
            {stat.label}
          </p>
        </motion.div>
      ))}
    </div>
  );
}