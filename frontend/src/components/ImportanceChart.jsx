import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function ImportanceChart({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }

  // Convert backend structure into chart score
  const formattedData = data.map((item) => {
    const missing = Number(item.missing_values) || 0;
    const unique = Number(item.unique_values) || 0;

    // Simple importance score formula
    const score = Math.max(0, Math.min(100, unique - missing));

    return {
      column: item.column.length > 15
        ? item.column.substring(0, 15) + "..."
        : item.column,
      score,
    };
  });

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-6">
        Column Importance Chart
      </h2>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={formattedData}>
          <XAxis dataKey="column" stroke="#ccc" />
          <YAxis stroke="#ccc" domain={[0, 100]} />
          <Tooltip />
          <Bar
            dataKey="score"
            fill="#06b6d4"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}