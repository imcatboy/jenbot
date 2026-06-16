import { apiClient } from "../client";
import type {
  CreateReputationUserRequest,
  ReputationUserResponse,
  ReputationUserWithRelationsResponse,
  UpdateReputationUserRequest,
} from "@/api/schemas";

export const reputationService = {
  createReputationUser: async (
    request: CreateReputationUserRequest,
  ): Promise<ReputationUserResponse> => {
    const response = await apiClient.post("api/v1/reputation/", request);
    return response.data;
  },

  updateReputationUser: async (
    id: number,
    request: UpdateReputationUserRequest,
  ): Promise<ReputationUserResponse> => {
    const response = await apiClient.put(`api/v1/reputation/${id}`, request);
    return response.data;
  },

  getReputationUser: async (
    id: number,
  ): Promise<ReputationUserWithRelationsResponse> => {
    const response = await apiClient.get(`api/v1/reputation/${id}`);
    return response.data;
  },

  getReputationUsers: async (
    search: string,
  ): Promise<ReputationUserResponse[]> => {
    const response = await apiClient.get("api/v1/reputation/", {
      params: { search },
    });
    return response.data;
  },
};
