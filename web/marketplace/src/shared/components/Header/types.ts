interface ButtonConfig {
  icon: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  isLoading?: boolean;
}

interface SearchConfig {
  placeholder: string;
  onChange?: (value: string) => void;
  value?: string;
  onCancel?: () => void;
  onFocus?: () => void;
}

interface HeaderConfig {
  leftButton?: ButtonConfig;
  search?: SearchConfig;
  rightButton?: ButtonConfig;
}

interface HeaderProps {
  children?: React.ReactNode;
}

export type { HeaderConfig, HeaderProps };