import { useEffect } from "react";
import { useUIStore } from "@/stores";

export const BackButtonController = () => {
  const backButtonConfig = useUIStore((state) => state.backButtonConfig);

  useEffect(() => {
    const telegramWebApp = window.Telegram?.WebApp;
    const backButton = telegramWebApp?.BackButton;

    if (!backButton) return;

    if (backButtonConfig.isVisible && !backButton.isVisible) {
      backButton.show();
    } else if (!backButtonConfig.isVisible && backButton.isVisible) {
      backButton.hide();
    }

    const handleBackClick = () => {
      if (backButtonConfig.onClick) {
        backButtonConfig.onClick();
      }
    };

    backButton.onClick(handleBackClick);
    return () => {
      backButton.offClick(handleBackClick);
    };
  }, [backButtonConfig]);

  return null;
};
