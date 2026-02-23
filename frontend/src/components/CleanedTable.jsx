export default function CleanedTable({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }

  const headers = Object.keys(data[0]);

  const escapeCSVValue = (value) => {
    if (value === null || value === undefined) return "";

    const stringValue = String(value);

    if (stringValue.includes(",") || stringValue.includes('"')) {
      return `"${stringValue.replace(/"/g, '""')}"`;
    }

    return stringValue;
  };

  const downloadCSV = () => {
    const csvContent =
      headers.join(",") +
      "\n" +
      data
        .map((row) =>
          headers.map((h) => escapeCSVValue(row[h])).join(",")
        )
        .join("\n");

    const blob = new Blob([csvContent], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = "cleaned_dataset.csv";
    a.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">
          Cleaned Dataset Preview
        </h2>

        <button
          onClick={downloadCSV}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 hover:opacity-90 transition"
        >
          Download CSV
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-white/80">
          <thead>
            <tr>
              {headers.map((header) => (
                <th
                  key={header}
                  className="pb-3 pr-6 text-left text-gray-400"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {data.slice(0, 15).map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className="border-t border-white/10"
              >
                {headers.map((header) => (
                  <td key={header} className="py-2 pr-6">
                    {row[header] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.length > 15 && (
        <p className="mt-4 text-xs text-white/50">
          Showing first 15 rows of {data.length}
        </p>
      )}
    </div>
  );
}