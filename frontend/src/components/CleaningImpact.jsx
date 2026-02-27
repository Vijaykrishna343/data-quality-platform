import React from "react";

const CleaningImpact = ({ before, after }) => {
  if (!before || !after) {
    return (
      <p className="text-gray-400">
        Run Smart Cleaning to see impact analysis.
      </p>
    );
  }

  const improvement = (after - before).toFixed(2);

  return (
    <div className="space-y-6">

      {/* Before */}
      <div>
        <div className="flex justify-between mb-2">
          <span>Before Cleaning</span>
          <span>{before}</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-4">
          <div
            className="bg-red-500 h-4 rounded-full transition-all duration-700"
            style={{ width: `${before}%` }}
          />
        </div>
      </div>

      {/* After */}
      <div>
        <div className="flex justify-between mb-2">
          <span>After Cleaning</span>
          <span>{after}</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-4">
          <div
            className="bg-green-500 h-4 rounded-full transition-all duration-700"
            style={{ width: `${after}%` }}
          />
        </div>
      </div>

      {/* Improvement */}
      <div className="text-center text-lg font-semibold text-purple-400">
        Improvement: +{improvement}
      </div>
    </div>
  );
};

export default CleaningImpact;