import React from "react";

const FeatureImportanceChart = ({ data }) => {

  if (!data || Object.keys(data).length === 0) {
    return (
      <p className="text-gray-400">
        No importance data available.
      </p>
    );
  }

  const maxValue = Math.max(...Object.values(data));

  return (
    <div className="space-y-4">
      {Object.entries(data).map(([col, value]) => (
        <div key={col}>
          <div className="flex justify-between mb-1">
            <span className="text-sm">{col}</span>
            <span className="text-sm font-semibold">{value}</span>
          </div>

          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-500 to-indigo-500 h-3 rounded-full transition-all duration-700"
              style={{
                width: `${(value / maxValue) * 100}%`
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default FeatureImportanceChart;