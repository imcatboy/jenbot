import { create } from "zustand";
import type { ReputationUserDraft, UserDetailDraft } from "@/types/draft";
import type {
  ReputationUserWithRelationsResponse,
  UserResponse,
} from "@/api/schemas/user";
import type { ScamReportResponse } from "@/api/schemas/trading";

type View = "home" | "card" | "userSearch" | "createUser" | "createDetail";

interface MainButtonConfig {
  label: string;
  isEnabled: boolean;
  isVisible: boolean;
  isLoading: boolean;
  onClick: () => void;
}

interface BackButtonConfig {
  isVisible: boolean;
  onClick: () => void;
}

interface UIStore {
  error: string | null;
  setError: (error: string | null) => void;
  view: View;
  cardId: number | null;
  setCardId: (cardId: number | null) => void;
  userId: number | null;
  setUserId: (userId: number | null) => void;
  detailId: number | null;
  setDetailId: (detailId: number | null) => void;
  backButtonConfig: BackButtonConfig;
  setBackButtonConfig: (config: Partial<BackButtonConfig>) => void;
  setView: (view: View) => void;
  mainButtonConfig: MainButtonConfig;
  setMainButtonConfig: (config: Partial<MainButtonConfig>) => void;
  draft: ReputationUserDraft | null;
  isDirty: boolean;
  initDraft: (reputationUser: ReputationUserWithRelationsResponse) => void;
  initEmptyDraft: () => void;
  updateDraft: (draft: Partial<ReputationUserDraft>) => void;
  clearDraft: () => void;
  addUserToDraft: (user: UserResponse) => void;
  updateUserInDraft: (user: UserResponse) => void;
  removeUserFromDraft: (id: number) => void;
  addUserDetailToDraft: (userDetail: UserDetailDraft) => void;
  updateUserDetailInDraft: (userDetail: UserDetailDraft) => void;
  removeUserDetailFromDraft: (id: number) => void;
  addAccusedReportToDraft: (accusedReport: ScamReportResponse) => void;
  removeAccusedReportFromDraft: (id: number) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  error: null,
  setError: (error: string | null) => set({ error: error }),
  view: "home",
  cardId: null,
  setCardId: (cardId: number | null) => set({ cardId: cardId }),
  userId: null,
  setUserId: (userId: number | null) => set({ userId: userId }),
  detailId: null,
  setDetailId: (detailId: number | null) => set({ detailId: detailId }),
  backButtonConfig: {
    isVisible: false,
    onClick: () => {},
  },
  setBackButtonConfig: (config: Partial<BackButtonConfig>) =>
    set((state) => ({
      backButtonConfig: { ...state.backButtonConfig, ...config },
    })),
  setView: (view: View) => set({ view: view }),
  mainButtonConfig: {
    label: "MainButton",
    isEnabled: true,
    isVisible: false,
    isLoading: false,
    onClick: () => {},
  },
  setMainButtonConfig: (config: Partial<MainButtonConfig>) =>
    set((state) => ({
      mainButtonConfig: { ...state.mainButtonConfig, ...config },
    })),
  draft: null,
  isDirty: false,
  initDraft: (reputationUser: ReputationUserWithRelationsResponse) =>
    set({ draft: { ...reputationUser }, isDirty: false }),
  initEmptyDraft: () =>
    set({
      draft: {
        version: 1,
        amount: 0.0,
        role: "clean_user",
        users: [],
        user_details: [],
        accused_reports: [],
      },
      isDirty: false,
    }),
  updateDraft: (draft: Partial<ReputationUserDraft>) =>
    set((state) => ({
      draft: state.draft ? { ...state.draft, ...draft } : null,
      isDirty: true,
    })),
  clearDraft: () => set({ draft: null, isDirty: false }),
  addUserToDraft: (user: UserResponse) =>
    set((state) => ({
      draft: state.draft
        ? { ...state.draft, users: [...state.draft.users, user] }
        : null,
      isDirty: true,
    })),
  updateUserInDraft: (user: UserResponse) =>
    set((state) => ({
      draft: state.draft
        ? {
            ...state.draft,
            users: state.draft.users.map((u) => (u.id === user.id ? user : u)),
          }
        : null,
      isDirty: true,
    })),
  removeUserFromDraft: (id: number) =>
    set((state) => ({
      draft: state.draft
        ? {
            ...state.draft,
            users: state.draft.users.filter((u) => u.id !== id),
          }
        : null,
      isDirty: true,
    })),
  addUserDetailToDraft: (userDetail: UserDetailDraft) =>
    set((state) => ({
      draft: state.draft
        ? {
            ...state.draft,
            user_details: [...state.draft.user_details, userDetail],
          }
        : null,
      isDirty: true,
    })),
  updateUserDetailInDraft: (userDetail: UserDetailDraft) =>
    set((state) => ({
      draft: state.draft
        ? {
            ...state.draft,
            user_details: state.draft.user_details.map((d) =>
              d.id === userDetail.id ? userDetail : d,
            ),
          }
        : null,
      isDirty: true,
    })),
  removeUserDetailFromDraft: (id: number) =>
    set((state) => ({
      draft: state.draft
        ? {
            ...state.draft,
            user_details: state.draft.user_details.filter((d) => d.id !== id),
          }
        : null,
      isDirty: true,
    })),
  addAccusedReportToDraft: (accusedReport: ScamReportResponse) =>
    set((state) => ({
      draft: state.draft
        ? {
            ...state.draft,
            accused_reports: [...state.draft.accused_reports, accusedReport],
          }
        : null,
      isDirty: true,
    })),
  removeAccusedReportFromDraft: (id: number) =>
    set((state) => ({
      draft: state.draft
        ? {
            ...state.draft,
            accused_reports: state.draft.accused_reports.filter(
              (r) => r.id !== id,
            ),
          }
        : null,
      isDirty: true,
    })),
}));
