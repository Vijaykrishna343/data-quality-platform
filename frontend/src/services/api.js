import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

/* ================= UPLOAD ================= */
export const uploadFile = (formData) =>
  API.post("/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

/* ================= UNIFIED ANALYTICS ================= */
export const getAnalytics = (datasetId) =>
  API.get(`/analytics/${datasetId}`);

/* ================= SIMULATION ================= */
export const simulateCleaning = (datasetId, payload) =>
  API.post(`/simulate/${datasetId}`, payload);

/* ================= PREVIEW PAGINATION ================= */
export const fetchDatasetPage = (datasetId, page = 1, pageSize = 20) =>
  API.get(
    `/download/preview/${datasetId}?page=${page}&page_size=${pageSize}`
  );

/* ================= DOWNLOAD ================= */
export const downloadCleanedDataset = (datasetId) =>
  API.get(`/download/${datasetId}`, {
    responseType: "blob",
  });

export default API;