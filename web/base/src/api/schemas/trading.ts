export interface ScamReportResponse {
  id: number;
  description?: string;
  contact_info?: string;
  attachments: string[];
  comment?: string;
  status: "pending" | "approved" | "rejected" | "cancelled";
  user_id: number;
  accused_reputation_user_id?: number;
  applied_by_user_id?: number;
}