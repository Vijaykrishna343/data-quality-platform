import React from "react";
import { motion } from "framer-motion";

const Section = ({ title, columns }) => {
  const safeColumns = columns || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white/5 backdrop-blur-md rounded-xl p-5 border border-white/10"
    >
      <h3 className="text-lg font-semibold mb-3 text-purple-300">
        {title} ({safeColumns.length})
      </h3>

      {safeColumns.length === 0 ? (
        <p className="text-gray-400 text-sm">None</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {safeColumns.map((col, idx) => (
            <span
              key={idx}
              className="px-3 py-1 text-sm rounded-full bg-purple-600/30 text-purple-200 border border-purple-400/20"
            >
              {col}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
};

const ColumnClassification = ({ classification }) => {
  if (!classification) {
    return (
      <div className="bg-white/5 backdrop-blur-md rounded-xl p-5 border border-white/10 text-gray-400">
        Loading classification...
      </div>
    );
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
      <Section title="Numeric" columns={classification.numeric} />
      <Section title="Categorical" columns={classification.categorical} />
      <Section title="Boolean" columns={classification.boolean} />
      <Section title="Datetime" columns={classification.datetime} />
      <Section title="Identifier" columns={classification.identifier} />
      <Section title="Text" columns={classification.text} />
    </div>
  );
};

export default ColumnClassification;