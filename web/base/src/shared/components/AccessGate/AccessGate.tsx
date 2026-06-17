import { WarningIcon } from "@/assets";
import { useMyUser } from "@/hooks";
import { isStaffRole, isTelegramWebApp } from "@/utils";
import { Sceleton } from "@/shared/ui";
import styles from "./AccessGate.module.scss";
import type { AccessGateProps, AccessDeniedProps } from "./types";

const AccessDenied = ({ title, message }: AccessDeniedProps) => (
  <div className={styles.accessGate}>
    <WarningIcon />
    <h1 className={styles.title}>{title}</h1>
    <p className={styles.message}>{message}</p>
  </div>
);

export const AccessGate = ({ children }: AccessGateProps) => {
  const isTelegram = isTelegramWebApp();
  const { data: user, isLoading, isError } = useMyUser(isTelegram);

  if (!isTelegram) {
    return (
      <AccessDenied
        title="Только Telegram"
        message="Это приложение доступно только внутри Telegram!"
      />
    );
  }

  if (isLoading) {
    return (
      <div className={styles.accessGate}>
        <Sceleton width="50%" height="40px" />
        {Array.from({ length: 6 }).map((_, index) => (
          <Sceleton key={index} width="100%" height="57px" />
        ))}
      </div>
    );
  }

  if (isError || !user || !isStaffRole(user.role)) {
    return (
      <AccessDenied
        title="Пока сюда нельзя"
        message="Приложение на данный момент создано только для сотрудников, но позже появится функционал и для тебя :]"
      />
    );
  }

  return children;
};
