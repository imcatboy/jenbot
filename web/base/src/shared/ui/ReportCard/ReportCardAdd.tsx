import { useState } from "react";
import styles from "./ReportCard.module.scss";
import type { ReportAddCardProps } from "./types";
import { useScamReport } from "@/hooks";
import { clsx } from "clsx";
import type { ScamReportResponse } from "@/api";

export const ReportCardAdd = ({
  onAdd,
  existingReports,
}: ReportAddCardProps) => {
  const [searchId, setSearchId] = useState<string>("");

  const handleAdd = (report: ScamReportResponse) => {
    onAdd(report);
    setSearchId("");
  };

  const { mutate: checkReport, isPending, isError } = useScamReport(handleAdd);

  const handleCheck = () => {
    const numericId = Number(searchId?.trim());

    if (!searchId || isNaN(numericId)) return;

    if (existingReports.some((report) => report.id === numericId)) {
      return;
    }

    checkReport(numericId);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/[^0-9]/g, "");
    setSearchId(value);
  };

  return (
    <div
      className={clsx(
        styles.card,
        isPending && styles.loading,
        isError && styles.error,
      )}
    >
      <input
        type="text"
        inputMode="numeric"
        pattern="[0-9]*"
        placeholder="Введите ID жалобы..."
        value={searchId}
        onChange={handleChange}
        onBlur={handleCheck}
        onKeyDown={(e) => e.key === "Enter" && handleCheck()}
        disabled={isPending}
        className={styles.input}
      />
    </div>
  );
};
