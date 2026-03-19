import { useEffect, useState } from "react";

export default function AnimatedGauge({ score }) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const interval = setInterval(() => {
      start += 2;
      if (start >= score) {
        start = score;
        clearInterval(interval);
      }
      setDisplayScore(start);
    }, 15);

    return () => clearInterval(interval);
  }, [score]);

  return (
    <div className="flex flex-col items-center justify-center p-6">
      <div className="text-6xl font-bold text-green-400 animate-pulse">
        {displayScore}
      </div>
      <p className="mt-2 text-gray-400">Quality Score</p>
    </div>
  );
}