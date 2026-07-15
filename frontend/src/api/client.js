import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // OCR + LLM analysis can take a little while
});

/**
 * Sends a resume file to the backend for parsing.
 * Throws an Error with a user-friendly message on failure.
 */
export async function parseResume(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await client.post("/api/parse", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (err) {
    if (err.response?.data?.detail) {
      throw new Error(err.response.data.detail);
    }
    if (err.code === "ECONNABORTED") {
      throw new Error("That took too long. Please try again.");
    }
    if (err.message === "Network Error") {
      throw new Error("Can't reach the server. Is the backend running?");
    }
    throw new Error("Something went wrong. Please try again.");
  }
}
