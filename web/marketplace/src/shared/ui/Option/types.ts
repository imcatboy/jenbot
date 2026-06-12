interface OptionProps {
  label: string;
  type: 'checkbox' | 'radio';
  checked?: boolean;
  disabled?: boolean;
  onClick: () => void;
}

export type { OptionProps };