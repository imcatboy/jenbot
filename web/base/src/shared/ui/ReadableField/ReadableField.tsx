import type { ReadableFieldProps } from "./types";
import styles from "./ReadableField.module.scss";
import { useState } from "react";
import { EditIcon } from "@/assets";

export const ReadableField = ({
  title,
  value,
  onSave,
  disabled,
  type = "string",
}: ReadableFieldProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedValue, setEditedValue] = useState("");

  const handleClick = () => {
    if (disabled) return;

    setEditedValue(value);
    setIsEditing(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (type === "number") {
      const value = e.target.value.replace(/[^0-9]/g, "");
      setEditedValue(value);
    } else {
      setEditedValue(e.target.value);
    }
  };

  const handleSave = (value: string) => {
    if (type === "number" && value !== "") {
      onSave(value);
    }

    if (type === "string" && value.trim() !== editedValue.trim()) {
      onSave(value);
    }

    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSave(editedValue);
    if (e.key === "Escape") handleCancel();
  };

  return (
    <div className={styles.readableField}>
      <h3 className={styles.title}>{title}</h3>
      {isEditing ? (
        <div className={styles.inputContainer}>
          <input
            type="text"
            inputMode={type === "number" ? "numeric" : "text"}
            pattern={type === "number" ? "[0-9]*" : undefined}
            className={styles.input}
            value={editedValue}
            autoFocus
            onChange={handleChange}
            onBlur={() => handleSave(editedValue)}
            onKeyDown={handleKeyDown}
          />
        </div>
      ) : (
        <button className={styles.value} onClick={handleClick}>
          <p className={styles.valueText}>{value}</p>
          {!disabled && (
            <div className={styles.editIcon}>
              <EditIcon />
            </div>
          )}
        </button>
      )}
    </div>
  );
};
