import { useEffect, useState } from "react";
import { fetchDatasetPage } from "../services/api";

export default function DatasetPreview({ datasetId }) {

  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const pageSize = 20;

  useEffect(() => {
    if (!datasetId) return;

    fetchDatasetPage(datasetId, page, pageSize)
      .then((res) => {
        setData(res.data.data || []);
        setColumns(res.data.columns || []);
        setTotalPages(res.data.total_pages || 1);
      })
      .catch((err) => console.error(err));

  }, [datasetId, page]);

  if (!data || data.length === 0)
    return <div className="text-gray-400">No preview data available</div>;

  return (
    <div className="overflow-x-auto mt-6">

      <table className="min-w-full border border-white/10">
        <thead className="bg-indigo-600/20">
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                className="px-4 py-2 border border-white/10 text-left"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-white/5 transition">
              {columns.map((col) => (
                <td
                  key={col}
                  className="px-4 py-2 border border-white/10"
                >
                  {row[col]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination Controls */}
      <div className="flex justify-between items-center mt-6">

        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
          className="px-4 py-2 bg-indigo-600 rounded disabled:opacity-40 hover:scale-105 transition"
        >
          Previous
        </button>

        <span>
          Page {page} of {totalPages}
        </span>

        <button
          disabled={page === totalPages}
          onClick={() => setPage(page + 1)}
          className="px-4 py-2 bg-indigo-600 rounded disabled:opacity-40 hover:scale-105 transition"
        >
          Next
        </button>

      </div>
    </div>
  );
}