import type { OptionProps } from "./types";
import clsx from "clsx";
import styles from "./Option.module.scss";

export const Option = ({ label, type, checked, disabled, onClick }: OptionProps) => {
  return (
    <button className={clsx(styles.option, type && styles[type], checked && styles.checked, disabled && styles.disabled)} onClick={onClick}>
      {label}
    </button>
  );
};