import { useCallback } from "react";
import { isAxiosError } from "axios";
import { useUIStore } from "@/stores";

const KNOWN_DETAIL_MESSAGES: Record<string, string> = {
  "Version mismatch":
    "Карточка уже изменена на сервере. Закройте и откройте её снова, затем повторите сохранение.",
  "Object not found": "Объект не найден.",
  "User not allowed to set reputation user":
    "Недостаточно прав для изменения этой карточки.",
  "User not allowed to update": "Недостаточно прав для изменения.",
  "An unexpected error occurred":
    "На сервере произошла ошибка. Попробуйте позже.",
  "Error occurred while processing the request":
    "Запрос не выполнен. Проверьте данные и попробуйте снова.",
};

const FIELD_TRANSLATIONS: Record<string, string> = {
  username: "Имя пользователя",
  telegram_id: "Telegram ID",
  user_details: "Реквизиты",
  name: "Название",
  value: "Значение",
};

interface ValidationErrorItem {
  loc?: unknown[];
  msg?: string;
}

function formatValidationDetail(items: ValidationErrorItem[]): string {
  return items
    .map((item) => {
      const hasLoc = Array.isArray(item.loc) && item.loc.length > 0;
      const rawPath = hasLoc ? String(item.loc?.[item.loc.length - 1]) : "";

      const path = FIELD_TRANSLATIONS[rawPath] ?? rawPath ?? "поле";
      const msg = item.msg?.trim() || "ошибка валидации";

      return `${path}: ${msg}`;
    })
    .join("\n");
}

export function formatAlertError(error: unknown): string {
  if (isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data as
      | Record<string, unknown>
      | undefined
      | null;

    if (data && typeof data === "object" && "detail" in data) {
      const detail = data.detail;

      if (typeof detail === "string") {
        return KNOWN_DETAIL_MESSAGES[detail] ?? detail;
      }

      if (Array.isArray(detail)) {
        return formatValidationDetail(detail as ValidationErrorItem[]);
      }
    }

    if (error.code === "ERR_NETWORK") {
      return "Нет соединения с сервером. Проверьте интернет и попробуйте снова.";
    }

    switch (status) {
      case 401:
      case 403:
        return "Недостаточно прав или сессия устарела. Откройте приложение заново.";
      case 404:
        return KNOWN_DETAIL_MESSAGES["Object not found"] ?? "Не найдено.";
      case 409:
        return (
          KNOWN_DETAIL_MESSAGES["Version mismatch"] ??
          "Конфликт данных. Обновите страницу и попробуйте снова."
        );
      default:
        if (status && status >= 500) {
          return (
            KNOWN_DETAIL_MESSAGES["An unexpected error occurred"] ??
            "Ошибка сервера."
          );
        }
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return "Не удалось выполнить операцию. Попробуйте ещё раз.";
}

export function showAlertError(error: unknown) {
  useUIStore.getState().setError(formatAlertError(error));
}

export function useAlertError() {
  const setError = useUIStore((state) => state.setError);

  return useCallback(
    (error: unknown) => {
      setError(formatAlertError(error));
    },
    [setError],
  );
}
