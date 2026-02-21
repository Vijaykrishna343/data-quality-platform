import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const analyzeDataset = (formData) =>
  API.post("/analyze/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const cleanDataset = (formData) =>
  API.post("/clean/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const getRecommendations = (formData) =>
  API.post("/recommend/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export default API;