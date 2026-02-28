import axios from "axios";

/* ================= AXIOS INSTANCE ================= */

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000, // 30s safety timeout
});

/* ================= GLOBAL ERROR HANDLER ================= */

API.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/* ================= UPLOAD ================= */

export const uploadFile = async (formData) => {
  return await API.post("/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

/* ================= UNIFIED ANALYTICS ================= */

export const getAnalytics = async (datasetId) => {
  return await API.get(`/analytics/${datasetId}`);
};

/* ================= SIMULATION ================= */

export const simulateCleaning = async (datasetId, payload) => {
  return await API.post(`/simulate/${datasetId}`, payload);
};

/* ================= PREVIEW PAGINATION ================= */

export const fetchDatasetPage = async (
  datasetId,
  page = 1,
  pageSize = 20
) => {
  return await API.get(
    `/download/preview/${datasetId}?page=${page}&page_size=${pageSize}`
  );
};

/* ================= DOWNLOAD CLEANED DATASET ================= */

export const downloadCleanedDataset = async (datasetId) => {
  const response = await API.get(`/download/${datasetId}`, {
    responseType: "blob",
  });

  // Auto download helper
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `cleaned_${datasetId}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();

  return response;
};

export default API;