import type { CheckboxProps } from "./types";
import styles from "./Checkbox.module.scss";
import { CheckboxIcon, CheckedCheckboxIcon } from "@/assets/icons";

export const Checkbox = ({ label, value, onChange }: CheckboxProps) => {
  return (
    <button className={styles.checkbox} onClick={() => onChange(!value)}>
      <label className={styles.label}>{label}</label>
      {value ? <CheckedCheckboxIcon /> : <CheckboxIcon />}
    </button>
  );
};
