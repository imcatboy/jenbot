import axios from 'axios';
import WebApp from '@twa-dev/sdk';
import qs from 'qs';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:4000',
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: (params) => {
    return qs.stringify(params, { arrayFormat: 'repeat', skipNulls: true });
  },
});

apiClient.interceptors.request.use(
  (config) => {
    let initData;
    if (import.meta.env.PROD) {
      initData = WebApp.initData;
    } else {
      initData = "XXXX";
    }

    if (initData) {
      config.headers['X-Telegram-Init-Data'] = initData;
    }

    return config;
    },
    (error) => {
      return Promise.reject(error);
    }
);