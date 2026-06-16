import {
  reputationService,
  type CreateReputationUserRequest,
  type ReputationUserResponse,
  type UpdateReputationUserRequest,
} from "@/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export const REPUTATION_KEYS = {
  all: ["reputation"],
  list: (search: string) => [...REPUTATION_KEYS.all, "list", search],
  user: (id: number) => [...REPUTATION_KEYS.all, "user", id],
};

export const useReputationUsers = (search: string) => {
  return useQuery({
    queryKey: REPUTATION_KEYS.list(search),
    queryFn: () => reputationService.getReputationUsers(search),
    staleTime: 1000 * 60 * 5,
    enabled: search.length >= 3,
  });
};

export const useReputationUser = (id: number | null) => {
  return useQuery({
    queryKey: REPUTATION_KEYS.user(id!),
    queryFn: () => reputationService.getReputationUser(id!),
    staleTime: 1000 * 60 * 5,
    enabled: id !== null,
  });
};

export const useCreateReputationUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateReputationUserRequest) =>
      reputationService.createReputationUser(request),
    onSuccess: (data: ReputationUserResponse) => {
      queryClient.invalidateQueries({ queryKey: REPUTATION_KEYS.all });
      queryClient.setQueryData(REPUTATION_KEYS.user(data.id), data);
    },
    onError: (error: Error) => {
      console.error(error);
    },
  });
};

export const useUpdateReputationUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      request,
    }: {
      id: number;
      request: UpdateReputationUserRequest;
    }) => reputationService.updateReputationUser(id, request),
    onSuccess: (data: ReputationUserResponse) => {
      queryClient.invalidateQueries({ queryKey: REPUTATION_KEYS.all });
      queryClient.setQueryData(REPUTATION_KEYS.user(data.id), data);
    },
    onError: (error: Error) => {
      console.error(error);
    },
  });
};
