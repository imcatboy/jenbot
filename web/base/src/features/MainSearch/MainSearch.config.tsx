import { StaffIcon, ScammerIcon, GuarantorIcon, UserIcon } from "@/assets";

export const ROLE_ICONS: Record<string, React.ReactNode> = {
  admin: <StaffIcon />,
  guarantor: <GuarantorIcon />,
  depositor: <GuarantorIcon />,
  scammer: <ScammerIcon />,
  clean_user: <UserIcon />,
  small_guarantor: <GuarantorIcon />,
  big_guarantor: <GuarantorIcon />,
};

export const ROLE_NAMES: Record<string, string> = {
  admin: "Администратор",
  guarantor: "Гарант",
  depositor: "Депозитор",
  scammer: "Скамер",
  clean_user: "Чистый пользователь",
  small_guarantor: "Младший гарант",
  big_guarantor: "Большой гарант",
};
