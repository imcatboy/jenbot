import { useEffect } from "react";
import WebApp from "@twa-dev/sdk";
import { useUIStore } from "@/stores";


export const BackButtonController = () => {
  const backButtonConfig = useUIStore((state) => state.backButtonConfig);

  useEffect(() => {
    const backButton = WebApp.BackButton;
    
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