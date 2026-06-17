import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@/styles/global.scss";
import { getTelegramWebApp, isTelegramWebApp } from "@/utils";
import App from "./App.tsx";

declare global {
  interface Window {
    Telegram?: {
      WebApp: typeof import("@twa-dev/sdk").default;
    };
  }
}

const telegramWebApp = getTelegramWebApp();

if (isTelegramWebApp() && telegramWebApp) {
  telegramWebApp.expand();

  const updateViewportHeight = () => {
    const tgHeight = `${telegramWebApp.viewportHeight}px`;
    document.documentElement.style.setProperty(
      "--tg-viewport-height",
      tgHeight,
    );
  };

  updateViewportHeight();
  telegramWebApp.onEvent("viewportChanged", updateViewportHeight);
} else {
  document.documentElement.style.setProperty("--tg-viewport-height", "100vh");
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
);
