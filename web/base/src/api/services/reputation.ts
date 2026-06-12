import { apiClient } from "../client";
import type { CreateReputationUserRequest, ReputationUserResponse, UpdateReputationUserRequest } from "@/api/schemas";

export const reputationService = {
  createReputationUser: async (request: CreateReputationUserRequest): Promise<ReputationUserResponse> => {
    const response = await apiClient.post("/reputation/", request);
    return response.data;
  },

  updateReputationUser: async (id: number, request: UpdateReputationUserRequest): Promise<ReputationUserResponse> => {
    const response = await apiClient.put(`/reputation/${id}`, request);
    return response.data;
  },

  getReputationUser: async (id: number): Promise<ReputationUserResponse> => {
    const response = await apiClient.get(`/reputation/${id}`);
    return response.data;
  },

  getReputationUsers: async (search: string): Promise<ReputationUserResponse[]> => {
    const response = await apiClient.get("/reputation/", { params: { search } });
    return response.data;
  },
}