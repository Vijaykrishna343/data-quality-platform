export default function ImportanceTable({ data }) {
  if (!data) return null;

  const formattedData = Array.isArray(data)
    ? data
    : Object.entries(data).map(([column, score]) => ({
        column,
        score,
      }));

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-6">
        Column Importance Table
      </h2>

      <table className="w-full text-left">
        <thead>
          <tr className="text-gray-400">
            <th className="pb-2">Column</th>
            <th className="pb-2">Score</th>
          </tr>
        </thead>
        <tbody>
          {formattedData.map((col, i) => (
            <tr key={i} className="border-t border-white/10">
              <td className="py-2">{col.column}</td>
              <td className="py-2">{col.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}