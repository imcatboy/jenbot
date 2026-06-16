import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@/styles/global.scss";
import App from "./App.tsx";
import WebApp from "@twa-dev/sdk";

const isTelegram = WebApp.platform !== "unknown";

if (isTelegram) {
  WebApp.expand();

  const updateViewportHeight = () => {
    const tgHeight = `${WebApp.viewportHeight}px`;
    document.documentElement.style.setProperty(
      "--tg-viewport-height",
      tgHeight,
    );
  };

  updateViewportHeight();
  WebApp.onEvent("viewportChanged", updateViewportHeight);
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
