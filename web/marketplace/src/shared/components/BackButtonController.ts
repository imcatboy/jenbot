import { useEffect } from "react";
import WebApp from "@twa-dev/sdk";
import { useUIStore } from "../../stores";


export const BackButtonController = () => {
  const history = useUIStore((state) => state.subViewHistory);
  const popSubView = useUIStore((state) => state.popSubView);

  useEffect(() => {
    const backButton = WebApp.BackButton;
    
    if (!backButton) return;

    if (history.length > 1) {
      backButton.show();
    } else {
      backButton.hide();
    }

    backButton.onClick(popSubView);
    return () => {
      backButton.offClick(popSubView);
    };
  }, [history, popSubView]);
  
  return null;
};