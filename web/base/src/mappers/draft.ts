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
    details: draft.user_details,
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
    details: draft.user_details,
    scam_report_ids: draft.accused_reports.map((r) => r.id),
  };
}
