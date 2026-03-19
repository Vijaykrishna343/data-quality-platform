import { motion } from "framer-motion";

export default function Heatmap({ data }) {

  if (!data || Object.keys(data).length === 0) {
    return null;
  }

  const columns = Object.keys(data);

  return (
    <motion.div
      className="bg-gray-900 p-6 rounded-2xl shadow-2xl mt-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <h2 className="text-xl font-semibold mb-4">
        Correlation Heatmap
      </h2>

      <div className="overflow-auto">
        <table className="border-collapse text-sm">
          <thead>
            <tr>
              <th className="px-2 py-1"></th>
              {columns.map((col) => (
                <th key={col} className="px-2 py-1 text-gray-400">
                  {col}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {columns.map((row) => (
              <tr key={row}>
                <td className="px-2 py-1 text-gray-400">
                  {row}
                </td>

                {columns.map((col) => {
                  const value =
                    data[row] && data[row][col]
                      ? data[row][col]
                      : 0;

                  const intensity = Math.abs(value);

                  return (
                    <td
                      key={col}
                      className="px-2 py-1 text-center"
                      style={{
                        backgroundColor: `rgba(59,130,246,${intensity})`
                      }}
                    >
                      {Number(value).toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}