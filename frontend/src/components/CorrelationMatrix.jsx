import { motion } from "framer-motion";

export default function CorrelationMatrix({ data }) {
  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);

  // Simple fake correlation generator (demo style)
  const generateValue = () => {
    return (Math.random() * 0.8 + 0.1).toFixed(2);
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-6">
        Correlation Matrix
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-white/70">
          <thead>
            <tr>
              <th className="p-3"></th>
              {columns.map((col) => (
                <th key={col} className="p-3 text-left">
                  {col}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {columns.map((rowCol, rowIndex) => (
              <motion.tr
                key={rowCol}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: rowIndex * 0.05 }}
              >
                <td className="p-3 font-medium text-white">
                  {rowCol}
                </td>

                {columns.map((col, colIndex) => (
                  <td key={colIndex} className="p-3">
                    {rowCol === col ? "1.00" : generateValue()}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}