export interface ReadableFieldProps {
  title: string;
  value: string;
  onSave: (value: string) => void;
  disabled?: boolean;
  type?: "number" | "string";
}
