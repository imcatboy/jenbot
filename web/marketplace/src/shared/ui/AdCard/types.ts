import type { AdvertisementOptionShortResponse } from "@/api/schemas";

interface AdCardProps {
  advertisementOption: AdvertisementOptionShortResponse;
  onClick: () => void;
}

export type { AdCardProps };