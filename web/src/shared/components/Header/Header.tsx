import clsx from "clsx";
import { Button } from "@/shared/ui";
import styles from "./Header.module.scss";
import type { HeaderProps } from "./types";
import { Search } from "@/shared/ui";
import { useUIStore } from "@/stores";


export const Header = ({ children }: HeaderProps) => {
  const config = useUIStore((state) => state.headerConfig);
  const separatedElements = config.leftButton && !config.search && config.rightButton;

  return (
    <div className={styles.header}>
      <header className={styles.headerContent}>
        <h1 className={styles.headerLabel}>Larion</h1>
        <div className={clsx(styles.elements, separatedElements && styles.separatedElements)}>
          {config.leftButton && <Button {...config.leftButton} type="floating" />}
          {config.search && <Search {...config.search} />}
          {config.rightButton && <Button {...config.rightButton} type="floating" />}
        </div>
      </header>
      <main className={styles.content}>
        {children}
      </main>
    </div>
  );
};