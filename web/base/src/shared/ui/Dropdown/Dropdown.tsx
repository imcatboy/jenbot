import type { DropdownProps } from "./types";
import { ArrowDownIcon } from "@/assets";
import styles from "./Dropdown.module.scss";
import { useState } from "react";
import clsx from "clsx";

export const Dropdown = ({ title, children }: DropdownProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.dropdown}>
      <div className={styles.header} onClick={() => setIsOpen(!isOpen)}>
        <h3 className={styles.title}>{title}</h3>
        <div className={clsx(styles.dropdownIcon, isOpen && styles.open)}>
          <ArrowDownIcon />
        </div>
      </div>
      {isOpen && <div className={styles.content}>{children}</div>}
    </div>
  );
};
