function QualitySection({ data }) {
  if (!data) return null;

  return (
    <div>
      <h3>Quality Score</h3>
      <h2>{data.quality_score}%</h2>

      <ul>
        {data.reasons.map((reason, index) => (
          <li key={index}>{reason}</li>
        ))}
      </ul>
    </div>
  );
}