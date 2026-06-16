import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  userService,
  type CreateUserRequest,
  type GetRequest,
  type UpdateUserRequest,
  type UserResponse,
} from "@/api";
import { showAlertError } from "./useAlertError";

export const USER_KEYS = {
  all: ["users"],
  myUser: () => [...USER_KEYS.all, "myUser"],
  list: (request: GetRequest) => [...USER_KEYS.all, "list", request],
  user: (id: number) => [...USER_KEYS.all, "user", id],
};

export const useUsers = (request: GetRequest) => {
  return useQuery({
    queryKey: USER_KEYS.list(request),
    queryFn: () => userService.getUsers(request),
    staleTime: 1000 * 60 * 5,
    enabled: request.search.length >= 3,
  });
};

export const useUser = (id?: number | null) => {
  return useQuery({
    queryKey: USER_KEYS.user(id!),
    queryFn: () => userService.getUser(id!),
    staleTime: 1000 * 60 * 5,
    enabled: !!id,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateUserRequest) => userService.createUser(request),
    onSuccess: (data: UserResponse) => {
      queryClient.invalidateQueries({ queryKey: USER_KEYS.all });
      queryClient.setQueryData(USER_KEYS.user(data.id), data);
    },
    onError: (error) => {
      console.error(error);
      showAlertError(error);
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, request }: { id: number; request: UpdateUserRequest }) =>
      userService.updateUser(id, request),
    onSuccess: (data: UserResponse) => {
      queryClient.invalidateQueries({ queryKey: USER_KEYS.all });
      queryClient.setQueryData(USER_KEYS.user(data.id), data);
    },
    onError: (error) => {
      console.error(error);
      showAlertError(error);
    },
  });
};

export const useMyUser = () => {
  return useQuery({
    queryKey: USER_KEYS.myUser(),
    queryFn: () => userService.getMyUser(),
    staleTime: 1000 * 60 * 5,
  });
};
