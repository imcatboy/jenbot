export interface SelectOption {
  icon: React.ReactNode;
  label: string;
  value: string;
}

export type SelectProps = {
  options: SelectOption[];
  placeholder: string;
  title: string;
  value?: string | null;
  onChange: (value: string) => void;
  disabled?: boolean;
};
