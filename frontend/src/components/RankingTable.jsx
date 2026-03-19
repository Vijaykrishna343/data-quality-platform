function RankingTable({ profiles }) {
  return (
    <div className="bg-white/10 p-6 rounded-xl">
      <h3 className="text-xl mb-4">Column Rankings</h3>
      <table className="w-full">
        <tbody>
          {Object.entries(profiles).map(([col, val]) => (
            <tr key={col} className="border-t border-white/10">
              <td>{col}</td>
              <td>{val.importance}</td>
              <td>{val.badge}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default RankingTable;