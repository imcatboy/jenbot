import { create } from "zustand";
import type { AdvertisementSuggestionResponse, GetCatalogRequest } from "@/api/schemas";
import { getIdKey } from "@/api/schemas/marketplace";


const initialFilters: GetCatalogRequest = {
  limit: 20,
  offset: 0,
  category_ids: [],
  product_ids: [],
  seller_ids: [],
  product_option_ids: [],
  min_count: null,
  high_rating: null,
  sort_type: "popularity",
};


interface CatalogStore {
  activeFilters: GetCatalogRequest;
  draftFilters: GetCatalogRequest;
  selectedSuggestions: AdvertisementSuggestionResponse[];
  addSelectedSuggestion: (suggestion: AdvertisementSuggestionResponse) => void;
  removeSelectedSuggestion: (suggestion: AdvertisementSuggestionResponse) => void;
  setDraftFilters: (filters: Partial<GetCatalogRequest>) => void;
  applyDraftFilters: () => void;
  resetFilters: () => void;
}


export const useCatalogStore = create<CatalogStore>((set) => ({
  activeFilters: initialFilters,
  draftFilters: initialFilters,
  selectedSuggestions: [],
  addSelectedSuggestion: (suggestion: AdvertisementSuggestionResponse) => set((state) => {
    const currentIds = state.draftFilters[getIdKey(suggestion) as keyof GetCatalogRequest] as number[] || [];

    if (currentIds.includes(suggestion.id)) return state;

    return {
      draftFilters: {
        ...state.draftFilters,
        [getIdKey(suggestion) as keyof GetCatalogRequest]: [...currentIds, suggestion.id],
      },
      selectedSuggestions: [...state.selectedSuggestions, suggestion],
    };
  }),
  removeSelectedSuggestion: (suggestion: AdvertisementSuggestionResponse) => set((state) => {
    const currentIds = state.draftFilters[getIdKey(suggestion) as keyof GetCatalogRequest] as number[] || [];

    if (!currentIds.includes(suggestion.id)) return state;

    return {
      draftFilters: {
        ...state.draftFilters,
        [getIdKey(suggestion) as keyof GetCatalogRequest]: currentIds.filter((id) => id !== suggestion.id),
      },
      selectedSuggestions: state.selectedSuggestions.filter((s) => s.id !== suggestion.id),
    };
  }),
  setDraftFilters: (filters: Partial<GetCatalogRequest>) => set((state) => ({ draftFilters: { ...state.draftFilters, ...filters } })),
  applyDraftFilters: () => set((state) => ({ activeFilters: state.draftFilters })),
  resetFilters: () => set(() => ({ activeFilters: initialFilters, draftFilters: initialFilters, selectedSuggestions: [] })),
}));