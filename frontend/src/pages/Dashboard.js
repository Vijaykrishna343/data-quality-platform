import React, { useState } from "react";
import { motion } from "framer-motion";
import FileUploader from "../components/FileUploader";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import { Bar } from "react-chartjs-2";
import "react-circular-progressbar/dist/styles.css";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function Dashboard() {
  const [data, setData] = useState(null);

  const chartData =
    data && data.column_importance
      ? {
          labels: Object.keys(data.column_importance),
          datasets: [
            {
              data: Object.values(data.column_importance),
              backgroundColor: "#00f5a0",
              borderRadius: 8,
            },
          ],
        }
      : null;

  return (
    <motion.div
      initial={{ x: 100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -100, opacity: 0 }}
      transition={{ duration: 0.6 }}
      style={styles.page}
    >
      <h1 style={styles.header}>Dashboard</h1>

      <FileUploader setData={setData} />

      {data && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div style={styles.scoreSection}>
            <div style={{ width: 180 }}>
              <CircularProgressbar
                value={data.quality_score}
                text={`${data.quality_score}%`}
                styles={buildStyles({
                  pathColor: "#00f5a0",
                  textColor: "#fff",
                  trailColor: "rgba(255,255,255,0.1)",
                })}
              />
            </div>

            <div style={{ marginLeft: 40 }}>
              <h2>Dataset Quality Score</h2>
              <p style={{ opacity: 0.6 }}>
                AI-based evaluation of dataset health.
              </p>
            </div>
          </div>

          {chartData && (
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
              style={styles.chart}
            >
              <Bar data={chartData} />
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#0b0f19",
    color: "white",
    padding: 60,
    fontFamily: "Inter, sans-serif",
  },
  header: {
    marginBottom: 40,
  },
  scoreSection: {
    display: "flex",
    alignItems: "center",
    marginTop: 40,
  },
  chart: {
    marginTop: 60,
    background: "rgba(255,255,255,0.05)",
    padding: 30,
    borderRadius: 20,
  },
};

export default Dashboard;