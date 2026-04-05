import axios from "axios";

/* ================= AXIOS INSTANCE ================= */

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000, // 30s safety timeout
});

/* ================= GLOBAL ERROR HANDLER & RETRY ================= */

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Auto-retry specifically for simulation or ML queries on timeout or 500+ errors
    if ((error.response?.status >= 500 || error.code === 'ECONNABORTED') && !originalRequest._retryCount) {
      originalRequest._retryCount = 1;
      console.warn("API Error detected. Retrying request immediately...");
      // Wait 1 second before retrying
      await new Promise(res => setTimeout(res, 1000));
      return API(originalRequest);
    }
    
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

/* ================= MACHINE LEARNING ================= */

export const trainModel = async (datasetId, targetColumn, taskType = "classification") => {
  return await API.post(`/ml/train/${datasetId}`, {
    target_column: targetColumn,
    task_type: taskType
  });
};

export const getPlotUrl = (plotType) => {
  return `http://127.0.0.1:8000/ml/plot/${plotType}?t=${new Date().getTime()}`;
};

export default API;