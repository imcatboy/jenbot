import type { TabProps } from "./types";
import clsx from "clsx";
import styles from "./Tab.module.scss";

export const Tab = ({ icon, label, onClick, isActive }: TabProps) => {
  return (
    <button className={clsx(styles.tab, isActive && styles.tabActive)} onClick={onClick} disabled={isActive}>
      {icon}
      <span className={styles.tabLabel}>{label}</span>
    </button>
  );
};