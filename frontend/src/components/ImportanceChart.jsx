import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function ImportanceChart({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return <p>No importance data available</p>;
  }

  const chartData = Object.entries(data).map(([key, value]) => ({
    name: key,
    value: Number(value),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <XAxis dataKey="name" stroke="#ccc" />
        <YAxis stroke="#ccc" />
        <Tooltip />
        <Bar dataKey="value" fill="#22c55e" />
      </BarChart>
    </ResponsiveContainer>
  );
}