import { motion } from "framer-motion";

export default function ImportanceTable({ data }) {
  if (!data) return null;

  const rows = Object.entries(data)
    .map(([key, value]) => ({
      name: key,
      value: Number(value),
    }))
    .sort((a, b) => b.value - a.value);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="overflow-x-auto mt-6"
    >
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-300 dark:border-gray-700">
            <th className="p-3 text-left">Feature</th>
            <th className="p-3 text-left">Importance</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr
              key={index}
              className="hover:bg-indigo-100 dark:hover:bg-indigo-900/30 transition"
            >
              <td className="p-3">{row.name}</td>
              <td className="p-3 font-semibold text-indigo-600 dark:text-indigo-400">
                {row.value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}