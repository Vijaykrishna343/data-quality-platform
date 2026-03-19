import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export default function Navbar() {
  const [dark, setDark] = useState(
    localStorage.getItem("theme") === "dark"
  );

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [dark]);

  return (
    <nav className="flex justify-between items-center px-10 py-5 border-b border-gray-200 dark:border-slate-700">

      <h1 className="text-2xl font-bold tracking-wide">
        Intelligent Cleaner
      </h1>

      <div className="flex items-center gap-6">
        <Link to="/">Home</Link>
        <Link to="/upload">Upload</Link>

        <motion.button
          whileTap={{ scale: 0.9 }}
          whileHover={{ scale: 1.05 }}
          onClick={() => setDark(!dark)}
          className="px-5 py-2 rounded-full font-medium bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-lg"
        >
          {dark ? "🌙 Dark" : "☀ Light"}
        </motion.button>
      </div>
    </nav>
  );
}