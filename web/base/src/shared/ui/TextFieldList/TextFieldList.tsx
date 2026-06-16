import { TextField } from "../TextField";
import type { TextFieldListProps } from "./types";
import styles from "./TextFieldList.module.scss";
import { CreateButton } from "../CreateButton";

export const TextFieldList = ({
  placeholder,
  values,
  buttonLabel,
  onSave,
}: TextFieldListProps) => {
  const handleChange = (index: number, value: string) => {
    const newValues = values.map((v, i) => (i === index ? value : v));
    onSave(newValues);
  };

  const handleDelete = (index: number) => {
    const newValues = values.filter((_, i) => i !== index);
    onSave(newValues);
  };

  const handleCreate = () => {
    const newValues = [...values, ""];
    onSave(newValues);
  };

  const isDuplicate = (index: number, value: string) => {
    if (value.trim() === "") return false;
    return values.some(
      (v, i) =>
        v.trim().toLowerCase() === value.trim().toLowerCase() && index !== i,
    );
  };

  return (
    <div className={styles.textFieldList}>
      {values.map((value, index) => (
        <TextField
          key={`text-field-${index}`}
          placeholder={placeholder}
          value={value}
          onChange={(value) => handleChange(index, value)}
          onDelete={() => handleDelete(index)}
          type="username"
          isError={isDuplicate(index, value)}
        />
      ))}
      <CreateButton label={buttonLabel} onClick={handleCreate} />
    </div>
  );
};
