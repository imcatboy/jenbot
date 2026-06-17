import axios from "axios";
import qs from "qs";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:4000",
  headers: {
    "Content-Type": "application/json",
  },
  paramsSerializer: (params) => {
    return qs.stringify(params, { arrayFormat: "repeat", skipNulls: true });
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const telegramWebApp = window.Telegram?.WebApp;
    let initData = telegramWebApp?.initData;

    if (!initData && !import.meta.env.PROD) {
      initData = import.meta.env.VITE_TELEGRAM_INIT_DATA || "XXXX";
    }

    if (initData) {
      config.headers.set("X-Telegram-Init-Data", initData);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);
