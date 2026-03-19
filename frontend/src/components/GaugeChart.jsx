import { RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";
import { motion } from "framer-motion";

function GaugeChart({ value }) {
  const data = [{ name: "score", value }];

  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 0.8 }}
      className="flex justify-center"
    >
      <RadialBarChart
        width={250}
        height={250}
        innerRadius="70%"
        outerRadius="100%"
        data={data}
        startAngle={180}
        endAngle={0}
      >
        <PolarAngleAxis
          type="number"
          domain={[0, 100]}
          angleAxisId={0}
          tick={false}
        />
        <RadialBar
          background
          dataKey="value"
          cornerRadius={10}
          fill="#22c55e"
        />
      </RadialBarChart>

      <div className="absolute mt-24 text-3xl font-bold text-green-400">
        {value}
      </div>
    </motion.div>
  );
}

export default GaugeChart;