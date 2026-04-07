import axios from "axios";

/* ================= AXIOS INSTANCE ================= */

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 120000, // 2 min for large-file processing
});

/* ================= GLOBAL ERROR HANDLER & RETRY ================= */

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      (error.response?.status >= 500 || error.code === "ECONNABORTED") &&
      !originalRequest._retryCount
    ) {
      originalRequest._retryCount = 1;
      console.warn("API Error detected. Retrying in 1 s…");
      await new Promise((res) => setTimeout(res, 1000));
      return API(originalRequest);
    }

    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/* ================= UPLOAD ================= */

export const uploadFile = async (formData, onProgress) => {
  return await API.post("/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        const pct = Math.round((e.loaded / e.total) * 100);
        onProgress(pct);
      }
    },
  });
};

/* ================= TASK STATUS POLLING ================= */

/**
 * Poll /upload/status/{taskId} until stage === "completed" or "failed".
 * Calls onStageChange(stage, progress, message) on every update.
 * Returns the final task object.
 */
export const pollTaskStatus = async (taskId, onStageChange, intervalMs = 2000) => {
  return new Promise((resolve, reject) => {
    const timer = setInterval(async () => {
      try {
        const res = await API.get(`/upload/status/${taskId}`);
        const task = res.data;

        if (onStageChange) {
          onStageChange(task.stage, task.progress, task.message);
        }

        if (task.stage === "completed") {
          clearInterval(timer);
          resolve(task);
        } else if (task.stage === "failed") {
          clearInterval(timer);
          reject(new Error(task.error || "Background processing failed"));
        }
      } catch (err) {
        clearInterval(timer);
        reject(err);
      }
    }, intervalMs);
  });
};

/* ================= UNIFIED ANALYTICS ================= */

export const getAnalytics = async (datasetId, invalidateCache = false) => {
  const params = invalidateCache ? "?invalidate_cache=true" : "";
  return await API.get(`/analytics/${datasetId}${params}`);
};

/* ================= SIMULATION ================= */

export const simulateCleaning = async (datasetId, payload) => {
  return await API.post(`/simulate/${datasetId}`, payload);
};

/* ================= PREVIEW PAGINATION ================= */

export const fetchDatasetPage = async (datasetId, page = 1, pageSize = 20) => {
  return await API.get(
    `/download/preview/${datasetId}?page=${page}&page_size=${pageSize}`
  );
};

/* ================= DOWNLOAD CLEANED DATASET ================= */

export const downloadCleanedDataset = async (datasetId) => {
  const response = await API.get(`/download/${datasetId}`, {
    responseType: "blob",
  });

  const url  = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href  = url;
  link.setAttribute("download", `cleaned_${datasetId}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();

  return response;
};

/* ================= MACHINE LEARNING ================= */

export const trainModel = async (
  datasetId,
  targetColumn,
  taskType = "classification"
) => {
  return await API.post(`/ml/train/${datasetId}`, {
    target_column: targetColumn,
    task_type: taskType,
  });
};

export const getPlotUrl = (plotType) =>
  `http://127.0.0.1:8000/ml/plot/${plotType}?t=${new Date().getTime()}`;

export default API;