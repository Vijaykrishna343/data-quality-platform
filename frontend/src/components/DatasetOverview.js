function DatasetOverview({ data }) {
  if (!data) return null;

  return (
    <div>
      <h3>Dataset Overview</h3>
      <p>Rows: {data.rows}</p>
      <p>Columns: {data.columns}</p>
      <p>Missing Values: {data.missing_values}</p>
      <p>Duplicate Rows: {data.duplicate_rows}</p>
      <p>Outliers: {data.outlier_count}</p>
    </div>
  );
}