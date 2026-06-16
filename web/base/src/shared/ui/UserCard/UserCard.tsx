import type { UserCardProps } from "./types";
import styles from "./UserCard.module.scss";

export const UserCard = ({
  icon,
  iconColor,
  title,
  description,
  onClick,
}: UserCardProps) => {
  return (
    <div className={styles.userCard} onClick={onClick}>
      <div style={{ color: iconColor }}>{icon}</div>
      <div className={styles.content}>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.description}>{description}</p>
      </div>
    </div>
  );
};
