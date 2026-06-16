import type { UserDetailDraft } from "@/types";

export interface DetailProps {
  detail: UserDetailDraft;
  onEdit: () => void;
  onRemove: () => void;
}
