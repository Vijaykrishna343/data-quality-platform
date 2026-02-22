import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6 }}
      style={styles.page}
    >
      <div style={styles.glow1}></div>
      <div style={styles.glow2}></div>

      <motion.div
        initial={{ y: 60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        style={styles.hero}
      >
        <h1 style={styles.title}>
          AI Data Quality Intelligence
        </h1>

        <p style={styles.subtitle}>
          Analyze, clean and optimize datasets instantly
          with intelligent automation.
        </p>

        <motion.button
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.95 }}
          style={styles.button}
          onClick={() => navigate("/dashboard")}
        >
          Launch Dashboard →
        </motion.button>
      </motion.div>
    </motion.div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#0b0f19",
    color: "white",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
    overflow: "hidden",
    fontFamily: "Inter, sans-serif",
  },
  hero: { textAlign: "center", zIndex: 2 },
  title: {
    fontSize: 48,
    fontWeight: 700,
    background: "linear-gradient(90deg,#00f5a0,#00d9f5)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: { marginTop: 20, opacity: 0.7, fontSize: 18 },
  button: {
    marginTop: 40,
    padding: "14px 30px",
    borderRadius: 30,
    border: "none",
    background: "linear-gradient(135deg,#00f5a0,#00d9f5)",
    fontWeight: 600,
    cursor: "pointer",
  },
  glow1: {
    position: "absolute",
    width: 500,
    height: 500,
    background: "radial-gradient(circle,#00f5a0,transparent)",
    top: -100,
    left: -100,
    filter: "blur(120px)",
    opacity: 0.3,
  },
  glow2: {
    position: "absolute",
    width: 400,
    height: 400,
    background: "radial-gradient(circle,#00d9f5,transparent)",
    bottom: -100,
    right: -100,
    filter: "blur(120px)",
    opacity: 0.3,
  },
};