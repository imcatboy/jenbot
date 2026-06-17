import { useEffect } from "react";
import { useUIStore } from "@/stores";

export const MainButtonController = () => {
  const config = useUIStore((state) => state.mainButtonConfig);

  useEffect(() => {
    const telegramWebApp = window.Telegram?.WebApp;
    const mainButton = telegramWebApp?.MainButton;

    if (!mainButton) return;

    mainButton.setText(config.label);

    if (config.isEnabled && !mainButton.isActive) {
      mainButton.setParams({
        is_active: true,
        color: telegramWebApp.themeParams.button_color || "#3390EC",
        text_color: telegramWebApp.themeParams.button_text_color || "#FFFFFF",
      });
    } else if (!config.isEnabled && mainButton.isActive) {
      mainButton.setParams({
        is_active: false,
        color: telegramWebApp.themeParams.hint_color || "#8E8E93",
        text_color: telegramWebApp.themeParams.button_text_color || "#FFFFFF",
      });
    }

    if (config.isVisible && !mainButton.isVisible) mainButton.show();
    else if (!config.isVisible && mainButton.isVisible) mainButton.hide();

    if (config.isLoading && !mainButton.isProgressVisible)
      mainButton.showProgress();
    else if (!config.isLoading && mainButton.isProgressVisible)
      mainButton.hideProgress();

    const handleMainClick = () => {
      if (config.onClick && config.isEnabled && !config.isLoading) {
        config.onClick();
      }
    };

    mainButton.onClick(handleMainClick);

    return () => {
      mainButton.offClick(handleMainClick);
    };
  }, [config]);

  return null;
};
