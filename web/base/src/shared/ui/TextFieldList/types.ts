export interface TextFieldListProps {
  placeholder: string;
  buttonLabel: string;
  values: string[];
  onSave: (values: string[]) => void;
}
