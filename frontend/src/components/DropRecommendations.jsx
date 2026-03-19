function DropRecommendations({ cols }) {
  if (!cols.length) return null;

  return (
    <div className="bg-white/10 p-6 rounded-xl">
      <h3 className="text-xl mb-4">Drop Recommendations</h3>
      {cols.map((c) => (
        <span key={c} className="bg-red-600 px-3 py-1 rounded-full mr-2">
          {c}
        </span>
      ))}
    </div>
  );
}

export default DropRecommendations;