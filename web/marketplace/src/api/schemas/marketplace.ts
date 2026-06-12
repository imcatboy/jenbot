export function getIdKey(obj: AdvertisementSuggestionResponse): string {
  return `${obj.kind}_ids`;
}


export interface SellerResponse {
  name: string | null
  username: string | null
  rating: number
  avatar_id: number | null
  advertisement_count: number
  review_count: number
  deal_count: number
}

export interface AdvertisementOptionShortResponse {
  id: number
  name: string
  category_path: string
  has_trades: boolean
  image_url: string
  user: SellerResponse
  options: string[]
  prices: string[]
}

export interface CatalogResponse {
  items: AdvertisementOptionShortResponse[]
  has_more: boolean
}


export interface AdvertisementSuggestionResponse {
  id: number
  kind: "category" | "product" | "product_option" | "seller"
  title: string
}


export interface GetCatalogRequest {
  limit: number
  offset: number
  category_ids: number[] | null
  product_ids: number[] | null
  seller_ids: number[] | null
  product_option_ids: number[] | null
  min_count: number | null
  high_rating: boolean | null
  sort_type: "popularity" | "new" | "old"
}


export interface GetAdvertisementSuggestionsRequest {
  limit: number
  offset: number
  category_ids: number[] | null
  product_ids: number[] | null
  seller_ids: number[] | null
  product_option_ids: number[] | null
  search: string
}