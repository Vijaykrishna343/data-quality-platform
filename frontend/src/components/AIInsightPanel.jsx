import { useEffect, useState } from "react";

export default function AIInsightPanel({ insights }) {
  const [displayText, setDisplayText] = useState("");

  useEffect(() => {
    if (!insights) return;

    const fullText = insights.join(" ");
    let i = 0;

    const interval = setInterval(() => {
      setDisplayText(fullText.slice(0, i));
      i++;
      if (i > fullText.length) clearInterval(interval);
    }, 20);

    return () => clearInterval(interval);
  }, [insights]);

  if (!insights) return null;

  return (
    <div className="mt-10 backdrop-blur-xl bg-indigo-500/10 border border-indigo-400/20 rounded-3xl p-6 shadow-2xl">
      <h3 className="text-indigo-300 mb-4">AI Insights</h3>
      <p className="text-gray-300">{displayText}</p>
    </div>
  );
}