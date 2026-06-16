import type { ScamReportResponse } from "@/api/schemas";

export interface ReportCardProps {
  report: ScamReportResponse;
  onRemove: () => void;
}

export interface ReportAddCardProps {
  onAdd: (report: ScamReportResponse) => void;
  existingReports: ScamReportResponse[];
}
