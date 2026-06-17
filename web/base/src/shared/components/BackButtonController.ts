import { useEffect } from "react";
import { useUIStore } from "@/stores";

export const BackButtonController = () => {
  const backButtonConfig = useUIStore((state) => state.backButtonConfig);

  useEffect(() => {
    const telegramWebApp = window.Telegram?.WebApp;
    const backButton = telegramWebApp?.BackButton;

    if (!backButton) return;

    if (backButtonConfig.isVisible) {
      backButton.show();
    } else {
      backButton.hide();
    }

    backButton.onClick(backButtonConfig.onClick);
    return () => {
      backButton.offClick(backButtonConfig.onClick);
    };
  }, [backButtonConfig]);

  return null;
};
