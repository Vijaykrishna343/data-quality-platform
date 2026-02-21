import React from "react";

function ImportanceChart({ data }) {
  if (!data) return null;

  return (
    <div>
      <h2>Column Importance</h2>
      <pre>{JSON.stringify(data.column_importance, null, 2)}</pre>
    </div>
  );
}

export default ImportanceChart;