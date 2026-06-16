import type { ScamReportResponse } from "./trading";

export interface UsernameResponse {
  id: number;
  username: string;
  user_id: number;
}

export interface UserResponse {
  id: number;
  telegram_id: number;
  usernames: UsernameResponse[];
  reputation_user_id?: number;
  role: "admin" | "user" | "moderator";
}

export interface ReputationUserResponse {
  id: number;
  description?: string;
  about?: string;
  version: number;
  amount: number;
  search_count: number;
  applied_report_count: number;
  review_count: number;
  role:
    | "scammer"
    | "clean_user"
    | "small_guarantor"
    | "guarantor"
    | "big_guarantor"
    | "depositor"
    | "admin";
  added_by_user_id: number;
  users: UserResponse[];
}

export interface UserDetailResponse {
  id: number;
  name: string;
  value: string;
  is_public: boolean;
  reputation_user_id: number;
}

export interface ReputationUserWithRelationsResponse extends ReputationUserResponse {
  users: UserResponse[];
  user_details: UserDetailResponse[];
  added_by_user: UserResponse;
  accused_reports: ScamReportResponse[];
}

export interface CreateUserDetailRequest {
  name: string;
  value: string;
  is_public: boolean;
}

export interface CreateReputationUserRequest {
  user_ids: number[];
  amount?: number;
  description?: string;
  role:
    | "scammer"
    | "clean_user"
    | "small_guarantor"
    | "guarantor"
    | "big_guarantor"
    | "depositor"
    | "admin";
  details: CreateUserDetailRequest[];
  scam_report_ids: number[];
}

export interface UpdateUserDetailRequest {
  id?: number;
  name: string;
  value: string;
  is_public: boolean;
}

export interface UpdateReputationUserRequest {
  user_ids?: number[];
  amount?: number;
  description?: string;
  role?:
    | "scammer"
    | "clean_user"
    | "small_guarantor"
    | "guarantor"
    | "big_guarantor"
    | "depositor"
    | "admin";
  details?: UpdateUserDetailRequest[];
  scam_report_ids?: number[];
  version: number;
}

export interface CreateUserRequest {
  telegram_id: number;
  usernames: UsernameResponse[];
}

export interface UpdateUserRequest {
  telegram_id?: number;
  usernames?: UsernameResponse[];
}

export interface GetRequest {
  limit: number;
  offset: number;
  search: string;
}
