import { useCallback, useState } from "react";
import clsx from "clsx";
import { useUIStore } from "@/stores";
import styles from "./ErrorAlert.module.scss";

const ANIMATION_MS = 250;

export const ErrorAlert = () => {
  const error = useUIStore((state) => state.error);
  const setError = useUIStore((state) => state.setError);
  const [isClosing, setIsClosing] = useState(false);

  const dismiss = useCallback(() => {
    setIsClosing(true);
    window.setTimeout(() => {
      setError(null);
      setIsClosing(false);
    }, ANIMATION_MS);
  }, [setError]);

  if (!error) return null;

  return (
    <div
      className={clsx(styles.errorAlert, isClosing && styles.closing)}
      role="alert"
      aria-live="assertive"
    >
      <p className={styles.errorAlertText}>{error}</p>
      <button
        type="button"
        className={styles.errorAlertButton}
        onClick={dismiss}
      >
        Закрыть
      </button>
    </div>
  );
};
