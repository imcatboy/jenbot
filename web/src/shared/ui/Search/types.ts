interface SearchProps {
  placeholder: string;
  onChange?: (value: string) => void;
  value?: string;
  onCancel?: () => void;
  onFocus?: () => void;
}

export type { SearchProps };