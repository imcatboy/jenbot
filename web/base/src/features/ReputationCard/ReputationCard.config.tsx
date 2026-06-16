import {
  SmallGuarantorIcon,
  SmallScammerIcon,
  SmallStaffIcon,
  SmallUserIcon,
} from "@/assets";
import type { SelectOption } from "@/shared/ui/Select";
import type { ReputationUserDraft } from "@/types/draft";

export const REPUTATION_ROLES: SelectOption[] = [
  {
    value: "scammer",
    label: "Скамер",
    icon: <SmallScammerIcon />,
  },
  {
    value: "guarantor",
    label: "Гарант",
    icon: <SmallGuarantorIcon />,
  },
  {
    value: "big_guarantor",
    label: "Большой гарант",
    icon: <SmallGuarantorIcon />,
  },
  {
    value: "small_guarantor",
    label: "Младший гарант",
    icon: <SmallGuarantorIcon />,
  },
  {
    value: "depositor",
    label: "Депозитчик",
    icon: <SmallGuarantorIcon />,
  },
  {
    value: "admin",
    label: "Администратор",
    icon: <SmallStaffIcon />,
  },
  {
    value: "clean_user",
    label: "Чистый пользователь",
    icon: <SmallUserIcon />,
  },
];

export const DISABLED_MODERATION_ROLES: ReputationUserDraft["role"][] = [
  "guarantor",
  "big_guarantor",
  "small_guarantor",
  "depositor",
  "admin",
];
