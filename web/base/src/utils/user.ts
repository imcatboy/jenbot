import type { UserResponse } from "@/api/schemas";

export function isStaffRole(role: UserResponse["role"]): boolean {
  return role === "admin" || role === "moderator";
}
