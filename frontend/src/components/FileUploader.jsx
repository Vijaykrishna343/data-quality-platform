import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Upload } from "lucide-react";

export default function FileUploader({ setData }) {
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:8000/analyze/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // VERY IMPORTANT — store file + backend response
      setData({
        file, // store file for re-analysis
        ...response.data,
      });

    } catch (error) {
      console.error("Upload error:", error);
      alert("Error uploading file. Check backend.");
    }

    setLoading(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="w-full p-12 border-2 border-dashed border-white/20 rounded-2xl bg-white/5 backdrop-blur-xl hover:border-cyan-400 transition-all duration-300"
    >
      <label className="flex flex-col items-center gap-6 cursor-pointer">
        <div className="p-6 rounded-2xl bg-white/10">
          <Upload size={40} className="text-white/70" />
        </div>

        <div className="text-center">
          <p className="text-lg font-medium">
            {loading ? "Uploading..." : "Drop your CSV file here"}
          </p>
          <p className="text-white/50 text-sm mt-2">
            Supports .csv files up to 50MB
          </p>
        </div>

        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
        />
      </label>
    </motion.div>
  );
}