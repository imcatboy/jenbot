import { TrashIcon } from "@/assets/icons";
import styles from "./ReportCard.module.scss";
import type { ReportCardProps } from "./types";

export const ReportCard = ({ report, onRemove }: ReportCardProps) => {
  return (
    <div className={styles.card}>
      <div className={styles.content}>
        <span className={styles.title}>{report.id} ID</span>
        <p className={styles.text}>{report.description}</p>
      </div>
      <button type="button" onClick={onRemove} className={styles.removeButton}>
        <TrashIcon />
      </button>
    </div>
  );
};
