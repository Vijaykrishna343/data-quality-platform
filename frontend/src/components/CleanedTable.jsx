export default function CleanedTable({ rows }) {
  if (!rows || rows.length === 0) return null;

  const headers = Object.keys(rows[0]);

  const downloadCSV = () => {
    const csv =
      headers.join(",") +
      "\n" +
      rows.map(row =>
        headers.map(h => row[h]).join(",")
      ).join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "cleaned_dataset.csv";
    a.click();
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      
      <div className="flex justify-between mb-4">
        <h2 className="text-xl font-semibold">
          Cleaned Dataset Preview
        </h2>

        <button
          onClick={downloadCSV}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 hover:opacity-90"
        >
          Download CSV
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr>
              {headers.map((h, i) => (
                <th key={i} className="pb-2 pr-4 text-gray-400">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 10).map((row, i) => (
              <tr key={i} className="border-t border-white/10">
                {headers.map((h, j) => (
                  <td key={j} className="py-2 pr-4">
                    {row[h]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}