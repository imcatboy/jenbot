import { useEffect } from "react";
import { useUIStore } from "../../stores";
import WebApp from "@twa-dev/sdk";


export const MainButtonController = () => {
  const config = useUIStore((state) => state.mainButtonConfig);

  useEffect(() => {
    const mainButton = WebApp.MainButton;
    
    if (!mainButton) return;

    mainButton.setText(config.label);

    if (config.isEnabled) mainButton.enable(); else mainButton.disable();
    if (config.isVisible) mainButton.show(); else mainButton.hide();
    if (config.isLoading) mainButton.showProgress(); else mainButton.hideProgress();
    mainButton.onClick(config.onClick);

    return () => {
      mainButton.offClick(config.onClick);
    };
  }, [config]);

  return null;
};


