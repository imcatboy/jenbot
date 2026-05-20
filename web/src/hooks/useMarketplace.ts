import { marketplaceService } from "@/api";
import type { GetAdvertisementSuggestionsRequest, GetCatalogRequest } from "@/api/schemas";
import { useQuery } from "@tanstack/react-query";

export const ADVERTISEMENT_KEYS = {
  all: ['advertisement'],
  lists: () => [...ADVERTISEMENT_KEYS.all, 'list'],
  suggestions: () => [...ADVERTISEMENT_KEYS.all, 'suggestion'],
  list: (params: GetCatalogRequest) => [...ADVERTISEMENT_KEYS.lists(), params],
  suggestion: (params: GetAdvertisementSuggestionsRequest) => [...ADVERTISEMENT_KEYS.suggestions(), params],
}

export const useMarketplace = (filters: GetCatalogRequest) => {
  return useQuery({
    queryKey: ADVERTISEMENT_KEYS.list(filters),
    queryFn: () => marketplaceService.getCatalog(filters),
    staleTime: 1000 * 60 * 5,
  });
};


export const useAdvertisementSuggestions = (request: GetAdvertisementSuggestionsRequest) => {
  return useQuery({
    queryKey: ADVERTISEMENT_KEYS.suggestion(request),
    queryFn: () => marketplaceService.getAdvertisementSuggestions(request),
    staleTime: 1000 * 60 * 5,
    enabled: request.search.length >= 3,
  });
};