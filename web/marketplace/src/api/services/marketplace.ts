import { apiClient } from '../client';
import type { AdvertisementSuggestionResponse, CatalogResponse, GetAdvertisementSuggestionsRequest, GetCatalogRequest } from '../schemas';


export const marketplaceService = {
  getCatalog: async (request: GetCatalogRequest): Promise<CatalogResponse> => {
    const response = await apiClient.get<CatalogResponse>('/api/v1/advertisements', {
      params: request,
    });
    return response.data;
  },

  getAdvertisementSuggestions: async (request: GetAdvertisementSuggestionsRequest): Promise<AdvertisementSuggestionResponse[]> => {
    const response = await apiClient.get<AdvertisementSuggestionResponse[]>('/api/v1/advertisements/suggestions', {
      params: request,
    });
    return response.data;
  },
}