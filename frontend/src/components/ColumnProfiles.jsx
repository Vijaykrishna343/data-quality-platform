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
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 transition-all duration-300">
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
              className="
                relative group
                bg-white/5 border border-white/10
                rounded-xl p-5
                transition-all duration-300 ease-out
                hover:scale-105
                hover:-translate-y-2
                hover:shadow-2xl
                hover:shadow-cyan-500/20
                hover:border-cyan-400/40
              "
            >
              {/* Hover Gradient Glow */}
              <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition duration-300 bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-transparent pointer-events-none"></div>

              <div className="relative z-10">

                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-cyan-500/20 transition-all duration-300 group-hover:bg-cyan-500/30">
                    {type === "Numeric" ? (
                      <Hash size={16} className="text-cyan-400 group-hover:rotate-6 transition-transform duration-300" />
                    ) : (
                      <Type size={16} className="text-cyan-400 group-hover:rotate-6 transition-transform duration-300" />
                    )}
                  </div>

                  <h3 className="font-medium transition-all duration-300 group-hover:text-cyan-300">
                    {column}
                  </h3>
                </div>

                <p className="text-sm text-white/60 mb-4">
                  {type} • {missing}% Missing
                </p>

                {/* Missing Percentage Progress Bar */}
                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-400 to-purple-500 transition-all duration-500"
                    style={{ width: `${missing}%` }}
                  ></div>
                </div>

              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}