import React from "react";

function DatasetOverview({ data }) {
  if (!data) return null;

  return (
    <div>
      <h2>Dataset Overview</h2>
      <p>Rows: {data.rows}</p>
      <p>Columns: {data.columns}</p>
    </div>
  );
}

export default DatasetOverview;