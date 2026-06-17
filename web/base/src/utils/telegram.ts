export function getTelegramWebApp() {
  return window.Telegram?.WebApp;
}

export function isTelegramWebApp(): boolean {
  if (!import.meta.env.PROD) {
    return true;
  }

  const webApp = getTelegramWebApp();

  return Boolean(
    webApp && webApp.platform !== "unknown" && webApp.initData.length > 0,
  );
}
