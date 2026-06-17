import type { TextFieldProps } from "./types";
import styles from "./TextField.module.scss";
import { TrashIcon } from "@/assets";
import clsx from "clsx";

export const TextField = ({
  placeholder,
  value,
  onChange,
  disabled,
  isError,
  type = "text",
  onDelete,
}: TextFieldProps) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (type === "number") {
      const value = e.target.value.replace(/[^0-9]/g, "");
      onChange?.(value);
    } else if (type === "username") {
      const value = e.target.value.replace(/[^a-zA-Z0-9_]/g, "");
      onChange?.(value);
    } else {
      onChange?.(e.target.value);
    }
  };

  return (
    <div
      className={clsx(
        styles.textField,
        disabled && styles.disabled,
        isError && styles.error,
      )}
    >
      <input
        className={styles.input}
        type="text"
        inputMode={type === "number" ? "numeric" : "text"}
        pattern={
          type === "number"
            ? "[0-9]*"
            : type === "username"
              ? "^[a-zA-Z0-9_]+$"
              : undefined
        }
        value={value}
        onChange={handleChange}
        disabled={disabled}
        placeholder={placeholder}
      />
      {onDelete && (
        <button className={styles.deleteButton} onClick={onDelete}>
          <TrashIcon />
        </button>
      )}
    </div>
  );
};
