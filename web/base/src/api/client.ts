import axios from "axios";
import WebApp from "@twa-dev/sdk";
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
    let initData = WebApp.initData;

    if (!initData && import.meta.env.DEV) {
      initData = import.meta.env.VITE_DEV_TELEGRAM_INIT_DATA || "";
    }

    if (initData) {
      config.headers["X-Telegram-Init-Data"] = initData;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);
