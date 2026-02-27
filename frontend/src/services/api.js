import axios from "axios";

/* ================= AXIOS INSTANCE ================= */

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

/* ================= UPLOAD ================= */

export const uploadFile = (formData) =>
  API.post("/upload/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

/* ================= PROFILE ================= */

export const getProfile = (datasetId) =>
  API.get(`/profile/${datasetId}`);

/* ================= CLASSIFICATION ================= */

export const getClassification = (datasetId) =>
  API.get(`/classify/${datasetId}`);

/* ================= RECOMMENDATION ================= */

export const getRecommendation = (datasetId) =>
  API.get(`/recommend/${datasetId}`);

/* ================= SIMULATION ================= */

export const simulateCleaning = (datasetId, payload) =>
  API.post(`/simulate/${datasetId}`, payload);

/* ================= CLEANED DATA PREVIEW (PAGINATION) ================= */

export const fetchDatasetPage = (
  datasetId,
  page = 1,
  pageSize = 20
) =>
  API.get(
    `/download/preview/${datasetId}?page=${page}&page_size=${pageSize}`
  );

/* ================= DOWNLOAD CLEANED DATASET ================= */

export const downloadCleanedDataset = (datasetId) =>
  API.get(`/download/${datasetId}`, {
    responseType: "blob", // important for file download
  });

/* ================= EXPORT DEFAULT ================= */

export default API;