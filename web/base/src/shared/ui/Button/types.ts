interface ButtonProps {
  icon?: React.ReactNode;
  label?: string;
  onClick: () => void;
  disabled?: boolean;
  type?: "standard" | "floating";
  isLoading?: boolean;
  fullWidth?: boolean;
}

export type { ButtonProps };
