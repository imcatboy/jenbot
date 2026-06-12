import { apiClient } from "@/api/client";
import type { CreateUserRequest, GetRequest, UpdateUserRequest, UserResponse } from "@/api/schemas";

export const userService = {
  createUser: async (request: CreateUserRequest): Promise<UserResponse> => {
    const response = await apiClient.post("/users/", request);
    return response.data;
  },
  
  updateUser: async (id: number, request: UpdateUserRequest): Promise<UserResponse> => {
    const response = await apiClient.put(`/users/${id}`, request);
    return response.data;
  },

  getUser: async (id: number): Promise<UserResponse> => {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  },

  getUsers: async (request: GetRequest): Promise<UserResponse[]> => {
    const response = await apiClient.get("/users/", { params: request });
    return response.data;
  },
}