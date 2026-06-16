import { apiClient } from "@/api/client";
import type {
  CreateUserRequest,
  GetRequest,
  UpdateUserRequest,
  UserResponse,
} from "@/api/schemas";

export const userService = {
  createUser: async (request: CreateUserRequest): Promise<UserResponse> => {
    const response = await apiClient.post("api/v1/users/", request);
    return response.data;
  },

  updateUser: async (
    id: number,
    request: UpdateUserRequest,
  ): Promise<UserResponse> => {
    const response = await apiClient.put(`api/v1/users/${id}`, request);
    return response.data;
  },

  getUser: async (id: number): Promise<UserResponse> => {
    const response = await apiClient.get(`api/v1/users/${id}`);
    return response.data;
  },

  getUsers: async (request: GetRequest): Promise<UserResponse[]> => {
    const response = await apiClient.get("api/v1/users/", { params: request });
    return response.data;
  },

  getMyUser: async (): Promise<UserResponse> => {
    const response = await apiClient.get("api/v1/users/me");
    return response.data;
  },
};
