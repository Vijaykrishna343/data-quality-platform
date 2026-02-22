import { motion } from "framer-motion";
import { useDropzone } from "react-dropzone";
import axios from "axios";

export default function FileUploader({ setData }) {
  const onDrop = async (files) => {
    const file = files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post(
      "http://127.0.0.1:8000/analyze/",
      formData
    );

    setData(res.data);
  };

  const { getRootProps, getInputProps, isDragActive } =
    useDropzone({ onDrop });

  return (
    <motion.div
      {...getRootProps()}
      whileHover={{ scale: 1.03 }}
      animate={{ borderColor: isDragActive ? "#00f5a0" : "#444" }}
      style={{
        padding: 60,
        borderRadius: 25,
        border: "2px dashed",
        textAlign: "center",
        cursor: "pointer",
        background: "rgba(255,255,255,0.04)",
        transition: "all 0.3s ease",
      }}
    >
      <input {...getInputProps()} />
      <h3>Drag & Drop CSV File</h3>
      <p style={{ opacity: 0.6 }}>or click to upload</p>
    </motion.div>
  );
}