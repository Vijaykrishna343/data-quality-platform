import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const [dark, setDark] = useState(
    localStorage.getItem("theme") === "dark"
  );

  const location = useLocation();

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [dark]);

  // ✅ Active link style
  const linkStyle = (path) =>
    `transition duration-200 ${
      location.pathname === path
        ? "text-indigo-400 font-semibold"
        : "hover:text-indigo-300"
    }`;

  return (
    <nav className="flex justify-between items-center px-10 py-5 border-b border-gray-200 dark:border-slate-700">

      {/* Logo */}
      <h1 className="text-2xl font-bold tracking-wide">
        Intelligent Cleaner
      </h1>

      {/* Navigation Links */}
      <div className="flex items-center gap-6">

        <Link to="/" className={linkStyle("/")}>
          Home
        </Link>

        <Link to="/upload" className={linkStyle("/upload")}>
          Upload
        </Link>

        {/* ✅ Added History */}
        <Link to="/history" className={linkStyle("/history")}>
          History
        </Link>

        {/* Theme Toggle */}
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