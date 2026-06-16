import { apiClient } from "@/api/client";
import type { ScamReportResponse } from "@/api/schemas";

export const tradingService = {
  getScamReport: async (reportId: number): Promise<ScamReportResponse> => {
    const response = await apiClient.get(
      `api/v1/trading/scam-reports/${reportId}`,
    );
    return response.data;
  },
};
