import type { AreaFieldProps } from "./types";
import styles from "./AreaField.module.scss";
import { EditIcon } from "@/assets";
import { useState } from "react";

export const AreaField = ({
  title,
  value,
  onSave,
  disabled,
}: AreaFieldProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedValue, setEditedValue] = useState("");

  const handleClick = () => {
    if (disabled) return;

    setIsEditing(true);
    setEditedValue(value);
  };

  const handleSave = () => {
    if (editedValue.trim() !== value.trim()) {
      onSave?.(editedValue);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter") handleSave();
    if (e.key === "Escape") handleCancel();
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditedValue(e.target.value);
  };

  return (
    <div className={styles.areaField}>
      <div className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        {!disabled && !isEditing && (
          <button className={styles.editIcon} onClick={handleClick}>
            <EditIcon />
          </button>
        )}
      </div>
      {isEditing ? (
        <textarea
          className={styles.textarea}
          value={editedValue}
          onChange={handleChange}
          onBlur={handleSave}
          onKeyDown={handleKeyDown}
          autoFocus
          rows={4}
        />
      ) : value.length > 0 ? (
        <p className={styles.value}>{value}</p>
      ) : (
        <p className={styles.placeholder}>Пустое поле</p>
      )}
    </div>
  );
};
