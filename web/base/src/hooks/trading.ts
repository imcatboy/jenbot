import { useMutation, useQueryClient } from "@tanstack/react-query";
import { tradingService, type ScamReportResponse } from "@/api";
import { showAlertError } from "./useAlertError";

export const TRADING_KEYS = {
  all: ["trading"],
  scamReport: (reportId: number) => [
    ...TRADING_KEYS.all,
    "scamReport",
    reportId,
  ],
};

export const useScamReport = (
  onSuccess?: (data: ScamReportResponse) => void,
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reportId: number) => tradingService.getScamReport(reportId),
    onSuccess: (data: ScamReportResponse) => {
      queryClient.setQueryData(TRADING_KEYS.scamReport(data.id), data);
      onSuccess?.(data);
    },
    onError: (error) => {
      console.error(error);
      showAlertError(error);
    },
  });
};
