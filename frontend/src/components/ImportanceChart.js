function ImportanceChart({ data }) {
  if (!data) return null;

  const importance = data.column_importance;

  return (
    <div>
      <h3>Column Importance</h3>
      {Object.keys(importance).map((col) => (
        <p key={col}>
          {col}: {importance[col]}
        </p>
      ))}
    </div>
  );
}