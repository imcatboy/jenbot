import type { UserResponse } from "@/api/schemas";

export interface LinkedUserProps {
  user: UserResponse;
  onEdit: () => void;
  onRemove: () => void;
}
