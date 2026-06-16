import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@/styles/global.scss";
import App from "./App.tsx";
import WebApp from "@twa-dev/sdk";

if (import.meta.env.PROD) {
  WebApp.expand();

  const tgHeight = `${WebApp.viewportHeight}px`;
  document.documentElement.style.setProperty("--tg-viewport-height", tgHeight);

  WebApp.onEvent("viewportChanged", () => {
    const newHeight = `${WebApp.viewportHeight}px`;
    document.documentElement.style.setProperty(
      "--tg-viewport-height",
      newHeight,
    );
  });
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
