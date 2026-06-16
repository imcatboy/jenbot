import { useUIStore } from "@/stores";
import WebApp from "@twa-dev/sdk";
import { Button } from "@/shared/ui";
import styles from "./MainButtonMock.module.scss";

export const MainButtonMock = () => {
  const config = useUIStore((state) => state.mainButtonConfig);

  if (!config.isVisible || WebApp.initData) {
    return null;
  }

  return (
    <div className={styles.mainButtonMock}>
      <Button
        label={config.label}
        onClick={config.onClick}
        disabled={!config.isEnabled || config.isLoading}
        isLoading={config.isLoading}
        fullWidth
        type="standard"
      />
    </div>
  );
};
