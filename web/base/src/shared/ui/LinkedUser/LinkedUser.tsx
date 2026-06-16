import type { LinkedUserProps } from "./types";
import styles from "./LinkedUser.module.scss";
import { EditIcon, TrashIcon } from "@/assets";

export const LinkedUser = ({ user, onEdit, onRemove }: LinkedUserProps) => {
  return (
    <div className={styles.linkedUser}>
      <div className={styles.userInfo}>
        <h3 className={styles.title}>
          {user.usernames
            .map((username) => `@${username.username.toLowerCase()}`)
            .join(" ")}
        </h3>
        <p className={styles.description}>{`${user.telegram_id} ID`}</p>
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
