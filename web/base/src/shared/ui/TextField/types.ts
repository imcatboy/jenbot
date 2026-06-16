export interface TextFieldProps {
  placeholder: string;
  value: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  type?: "text" | "number" | "username";
  onDelete?: () => void;
  isError?: boolean;
}
