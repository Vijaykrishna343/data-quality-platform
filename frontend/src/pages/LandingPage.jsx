import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

export default function LandingPage() {

  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-black text-white overflow-hidden">

      {/* Animated Background Blobs */}
      <motion.div
        animate={{ x: [0, 60, 0], y: [0, 60, 0] }}
        transition={{ duration: 12, repeat: Infinity }}
        className="absolute w-96 h-96 bg-purple-600/30 rounded-full blur-3xl -top-40 -left-40"
      />
      <motion.div
        animate={{ x: [0, -60, 0], y: [0, -60, 0] }}
        transition={{ duration: 15, repeat: Infinity }}
        className="absolute w-96 h-96 bg-indigo-600/30 rounded-full blur-3xl bottom-0 right-0"
      />

      {/* HERO SECTION */}
      <section className="relative px-10 pt-32 pb-20 text-center">

        <motion.h1
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-6xl font-bold mb-6"
        >
          AI-Powered Data Quality Platform
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-xl text-gray-300 max-w-3xl mx-auto mb-10"
        >
          Automatically analyze, simulate, and optimize your datasets using
          intelligent quality scoring and advanced anomaly detection.
        </motion.p>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate("/upload")}
          className="px-10 py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 shadow-2xl text-lg"
        >
          Get Started
        </motion.button>

      </section>

      {/* FEATURES SECTION */}
      <section className="px-10 py-20">

        <h2 className="text-4xl font-bold text-center mb-16">
          Powerful Features
        </h2>

        <div className="grid md:grid-cols-3 gap-12">

          {[
            {
              title: "Smart Profiling",
              desc: "Automatic dataset profiling with missing, duplicate & outlier detection."
            },
            {
              title: "What-If Simulation",
              desc: "Test cleaning strategies before applying them permanently."
            },
            {
              title: "AI Insights",
              desc: "Get intelligent recommendations to improve dataset readiness."
            },
          ].map((feature, index) => (
            <motion.div
              key={index}
              whileHover={{ scale: 1.05 }}
              className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-xl"
            >
              <h3 className="text-xl font-semibold mb-4 text-indigo-300">
                {feature.title}
              </h3>
              <p className="text-gray-400">
                {feature.desc}
              </p>
            </motion.div>
          ))}

        </div>

      </section>

      {/* HOW IT WORKS */}
      <section className="px-10 py-20 bg-black/40">

        <h2 className="text-4xl font-bold text-center mb-16">
          How It Works
        </h2>

        <div className="grid md:grid-cols-3 gap-12 text-center">

          {["Upload Dataset", "Analyze & Simulate", "Download Cleaned Data"]
            .map((step, i) => (
              <motion.div
                key={i}
                whileInView={{ opacity: 1, y: 0 }}
                initial={{ opacity: 0, y: 40 }}
                transition={{ duration: 0.6 }}
                className="bg-white/5 backdrop-blur-xl rounded-2xl p-8 shadow-xl"
              >
                <div className="text-5xl font-bold text-indigo-400 mb-4">
                  {i + 1}
                </div>
                <p className="text-lg text-gray-300">{step}</p>
              </motion.div>
            ))}

        </div>

      </section>

      {/* CTA */}
      <section className="px-10 py-20 text-center">

        <motion.h2
          whileInView={{ opacity: 1, y: 0 }}
          initial={{ opacity: 0, y: 40 }}
          className="text-4xl font-bold mb-6"
        >
          Ready to Optimize Your Data?
        </motion.h2>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate("/upload")}
          className="px-10 py-4 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 shadow-2xl text-lg"
        >
          Start Free
        </motion.button>

      </section>

    </div>
  );
}