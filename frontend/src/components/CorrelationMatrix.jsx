import { motion } from "framer-motion";

// Utility: Calculate correlation between two arrays
function calculateCorrelation(x, y) {
  const n = x.length;
  if (n === 0) return 0;

  const meanX = x.reduce((a, b) => a + b, 0) / n;
  const meanY = y.reduce((a, b) => a + b, 0) / n;

  const numerator = x.reduce(
    (sum, xi, i) => sum + (xi - meanX) * (y[i] - meanY),
    0
  );

  const denominatorX = Math.sqrt(
    x.reduce((sum, xi) => sum + Math.pow(xi - meanX, 2), 0)
  );

  const denominatorY = Math.sqrt(
    y.reduce((sum, yi) => sum + Math.pow(yi - meanY, 2), 0)
  );

  const denominator = denominatorX * denominatorY;

  if (denominator === 0) return 0;

  return numerator / denominator;
}

export default function CorrelationMatrix({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }

  // Extract numeric columns only
  const columns = Object.keys(data[0]).filter((col) =>
    data.every((row) => !isNaN(parseFloat(row[col])))
  );

  if (columns.length === 0) return null;

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

                {columns.map((col, colIndex) => {
                  if (rowCol === col) {
                    return (
                      <td key={colIndex} className="p-3 text-cyan-400">
                        1.00
                      </td>
                    );
                  }

                  const x = data.map((row) =>
                    parseFloat(row[rowCol])
                  );
                  const y = data.map((row) =>
                    parseFloat(row[col])
                  );

                  const corr = calculateCorrelation(x, y);
                  const value = corr.toFixed(2);

                  return (
                    <td
                      key={colIndex}
                      className={`p-3 ${
                        Math.abs(corr) > 0.7
                          ? "text-green-400"
                          : Math.abs(corr) > 0.4
                          ? "text-yellow-400"
                          : "text-white/70"
                      }`}
                    >
                      {value}
                    </td>
                  );
                })}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}