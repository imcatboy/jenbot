import styles from "./Button.module.scss";
import type { ButtonProps } from "./types";
import clsx from "clsx";


export const Button = ({ icon, label, onClick, disabled, type, isLoading = false, fullWidth = false }: ButtonProps) => {
  return (
    <button className={clsx(styles.button, type && styles[type], isLoading && styles.loading, fullWidth && styles.fullWidth)} onClick={onClick} disabled={disabled}>
      {icon}
      {label && <span className={styles.label}>{label}</span>}
    </button>
  );
};