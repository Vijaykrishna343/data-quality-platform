export default function StatsCards({ rows, columns, duplicates }) {
  if (
    rows === undefined ||
    columns === undefined ||
    duplicates === undefined
  ) {
    return null;
  }

  return (
    <div className="grid md:grid-cols-3 gap-6">
      
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-white/60 text-sm mb-2">
          Total Rows
        </h3>
        <p className="text-2xl font-semibold text-cyan-400">
          {rows.toLocaleString()}
        </p>
      </div>

      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-white/60 text-sm mb-2">
          Total Columns
        </h3>
        <p className="text-2xl font-semibold text-purple-400">
          {columns}
        </p>
      </div>

      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-white/60 text-sm mb-2">
          Duplicate Rows
        </h3>
        <p className="text-2xl font-semibold text-red-400">
          {duplicates.toLocaleString()}
        </p>
      </div>

    </div>
  );
}