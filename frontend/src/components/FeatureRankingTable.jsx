export default function FeatureRankingTable({ data }) {
  if (!data || Object.keys(data).length === 0) return null;

  const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);

  return (
    <div className="bg-gray-800 p-6 rounded-xl">
      <h2 className="text-xl font-semibold mb-4">Feature Ranking</h2>

      <table className="w-full text-sm text-left">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="p-2">Rank</th>
            <th className="p-2">Feature</th>
            <th className="p-2">Importance</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map(([feature, value], index) => (
            <tr key={feature} className="border-b border-gray-700">
              <td className="p-2">{index + 1}</td>
              <td className="p-2">{feature}</td>
              <td className="p-2">{value.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}