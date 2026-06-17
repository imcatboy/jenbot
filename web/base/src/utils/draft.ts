import type {
  UpdateReputationUserRequest,
  CreateReputationUserRequest,
} from "@/api";
import type { ReputationUserDraft } from "@/types/draft";

export function draftToUpdateRequest(
  draft: ReputationUserDraft,
): UpdateReputationUserRequest {
  return {
    user_ids: draft.users.map((u) => u.id),
    amount: draft.amount,
    version: draft.version,
    description: draft.description,
    role: draft.role,
    details: draft.user_details.map((d) => ({
      id: d.id < 1000000 ? d.id : undefined,
      name: d.name,
      value: d.value,
      is_public: d.is_public,
    })),
    scam_report_ids: draft.accused_reports.map((r) => r.id),
  };
}

export function draftToCreateRequest(
  draft: ReputationUserDraft,
): CreateReputationUserRequest {
  return {
    user_ids: draft.users.map((u) => u.id),
    amount: draft.amount,
    description: draft.description,
    role: draft.role,
    details: draft.user_details.map((d) => ({
      name: d.name,
      value: d.value,
      is_public: d.is_public,
    })),
    scam_report_ids: draft.accused_reports.map((r) => r.id),
  };
}

export const hasDuplicates = (array: string[]): boolean => {
  const filtered = array
    .map((value) => value.trim().toLowerCase())
    .filter(Boolean);
  return new Set(filtered).size !== filtered.length;
};
