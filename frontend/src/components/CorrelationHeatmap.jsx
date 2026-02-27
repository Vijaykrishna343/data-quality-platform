import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

const CorrelationHeatmap = ({ correlation }) => {
  if (!correlation || Object.keys(correlation).length === 0) {
    return <p className="text-gray-400">No correlation data available</p>;
  }

  const numericCols = Object.keys(correlation);

  const data = numericCols.map((col) => {
    const values = Object.values(correlation[col] || {});
    const avgCorr =
      values.reduce((sum, val) => sum + Math.abs(val || 0), 0) /
      (values.length || 1);

    return {
      name: col,
      score: parseFloat(avgCorr.toFixed(2)),
    };
  });

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="name" />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Bar dataKey="score" fill="#8b5cf6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CorrelationHeatmap;