import type { DetailProps } from "./types";
import styles from "./Detail.module.scss";
import { EditIcon, ExternalIcon, FilterIcon, TrashIcon } from "@/assets/icons";
import clsx from "clsx";

export const Detail = ({ detail, onEdit, onRemove }: DetailProps) => {
  return (
    <div className={styles.detail}>
      <div className={styles.info}>
        <div className={clsx(styles.icon, detail.is_public && styles.public)}>
          {detail.is_public ? <ExternalIcon /> : <FilterIcon />}
        </div>
        <div className={styles.valueContainer}>
          <h3 className={styles.title}>{detail.name}</h3>
          <p className={styles.value}>{detail.value}</p>
        </div>
      </div>
      <div className={styles.actions}>
        <button className={styles.editButton} onClick={onEdit}>
          <EditIcon />
        </button>
        <button className={styles.removeButton} onClick={onRemove}>
          <TrashIcon />
        </button>
      </div>
    </div>
  );
};
