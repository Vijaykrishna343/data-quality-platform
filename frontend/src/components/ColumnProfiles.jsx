import { Hash, Type } from "lucide-react";

export default function ColumnProfiles({ data }) {
  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);

  const getColumnType = (column) => {
    const sample = data.find(row => row[column] !== null && row[column] !== "");
    if (!sample) return "Unknown";

    return typeof sample[column] === "number" ? "Numeric" : "Categorical";
  };

  const calculateMissing = (column) => {
    const total = data.length;

    const missingCount = data.filter(row => {
      const value = row[column];
      return (
        value === null ||
        value === undefined ||
        value === "" ||
        value === " " ||
        (typeof value === "number" && isNaN(value))
      );
    }).length;

    return ((missingCount / total) * 100).toFixed(2);
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <h2 className="text-xl font-semibold mb-8">
        Column Profiles
      </h2>

      <div className="grid md:grid-cols-3 gap-6">
        {columns.map((column) => {
          const type = getColumnType(column);
          const missing = calculateMissing(column);

          return (
            <div
              key={column}
              className="bg-white/5 border border-white/10 rounded-xl p-5"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-cyan-500/20">
                  {type === "Numeric" ? (
                    <Hash size={16} className="text-cyan-400" />
                  ) : (
                    <Type size={16} className="text-cyan-400" />
                  )}
                </div>

                <h3 className="font-medium">{column}</h3>
              </div>

              <p className="text-sm text-white/60">
                {type} • {missing}% Missing
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}