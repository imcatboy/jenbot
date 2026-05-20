import type { SceletonProps } from "./types";
import styles from "./Sceleton.module.scss";

export const Sceleton = ({ width, height }: SceletonProps) => {
  return (
    <div className={styles.sceleton} style={{ width, height }}>
    </div>
  );
};