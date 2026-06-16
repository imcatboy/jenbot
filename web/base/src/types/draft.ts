import type { ScamReportResponse } from "@/api/schemas/trading";
import type { UserResponse } from "@/api/schemas/user";

export interface UserDetailDraft {
  id: number;
  name: string;
  value: string;
  is_public: boolean;
}

export interface ReputationUserDraft {
  version: number;
  description?: string;
  about?: string;
  amount: number;
  role:
    | "scammer"
    | "clean_user"
    | "small_guarantor"
    | "guarantor"
    | "big_guarantor"
    | "depositor"
    | "admin";
  users: UserResponse[];
  user_details: UserDetailDraft[];
  accused_reports: ScamReportResponse[];
}
