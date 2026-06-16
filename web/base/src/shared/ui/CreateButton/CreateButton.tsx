import type { CreateButtonProps } from "./types";
import styles from "./CreateButton.module.scss";
import { PlusIcon } from "@/assets";

export const CreateButton = ({ onClick, label }: CreateButtonProps) => {
  return (
    <button className={styles.createButton} onClick={onClick}>
      <PlusIcon />
      <span className={styles.label}>{label}</span>
    </button>
  );
};
