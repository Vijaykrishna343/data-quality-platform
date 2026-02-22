import React from "react";

function QualitySection({ data }) {
  if (!data) return null;

  return (
    <div>
      <h2>Quality Score</h2>
      <p>Score: {data.quality_score}</p>
    </div>
  );
}

export default QualitySection;