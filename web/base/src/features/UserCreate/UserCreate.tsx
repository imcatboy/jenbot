import styles from "./UserCreate.module.scss";
import { useUIStore } from "@/stores";
import { useCreateUser, useUpdateUser, useUser } from "@/hooks";
import { useCallback, useEffect, useState } from "react";
import { Sceleton, TextField, TextFieldList } from "@/shared/ui";
import { hasDuplicates } from "@/mappers";
import { WarningIcon } from "@/assets/icons";
import type { UserResponse } from "@/api/schemas";

const UserCreateForm = ({
  user,
  isEdit,
}: {
  user?: UserResponse;
  isEdit: boolean;
}) => {
  const setMainButtonConfig = useUIStore((state) => state.setMainButtonConfig);
  const setBackButtonConfig = useUIStore((state) => state.setBackButtonConfig);
  const setUserId = useUIStore((state) => state.setUserId);
  const setView = useUIStore((state) => state.setView);
  const updateUserInDraft = useUIStore((state) => state.updateUserInDraft);
  const addUserToDraft = useUIStore((state) => state.addUserToDraft);
  const [usernames, setUsernames] = useState<string[]>(
    user?.usernames.map((username) => username.username) ?? [],
  );
  const { mutate: updateUser } = useUpdateUser();
  const { mutate: createUser } = useCreateUser();
  const [createTelegramId, setCreateTelegramId] = useState<
    number | undefined
  >();
  const telegramIdStr = isEdit
    ? (user?.telegram_id?.toString() ?? "")
    : (createTelegramId?.toString() ?? "");
  const isValid = !hasDuplicates(usernames);

  const handleSave = useCallback(() => {
    if (!isValid) return;

    if (isEdit) {
      if (!user) return;

      updateUser(
        {
          id: user.id,
          request: {
            telegram_id: createTelegramId,
            usernames: usernames,
          },
        },
        {
          onSuccess: (data) => {
            updateUserInDraft(data);
            setView("card");
          },
        },
      );
    } else {
      createUser(
        {
          telegram_id: createTelegramId ?? 0,
          usernames: usernames,
        },
        {
          onSuccess: (data) => {
            addUserToDraft(data);
            setView("card");
          },
        },
      );
    }
  }, [
    isEdit,
    user,
    createTelegramId,
    usernames,
    updateUser,
    updateUserInDraft,
    createUser,
    addUserToDraft,
    setView,
    isValid,
  ]);

  const handleBack = useCallback(() => {
    setView("card");
    setUserId(null);
  }, [setView, setUserId]);

  useEffect(() => {
    setMainButtonConfig({
      isVisible: true,
      isEnabled: isValid,
      label: "Сохранить",
      onClick: handleSave,
    });
  }, [setMainButtonConfig, isValid, handleSave]);

  useEffect(() => {
    setBackButtonConfig({
      isVisible: true,
      onClick: handleBack,
    });
  }, [setBackButtonConfig, handleBack]);

  return (
    <div className={styles.form}>
      <TextField
        placeholder="Telegram ID"
        value={telegramIdStr}
        onChange={(value) => setCreateTelegramId(Number(value))}
        disabled={isEdit}
        type="number"
      />
      <hr className={styles.separator} />
      <TextFieldList
        placeholder="Имя пользователя"
        buttonLabel="Добавить имя пользователя"
        values={usernames}
        onSave={(values) => setUsernames(values)}
      />
    </div>
  );
};

export const UserCreate = () => {
  const userId = useUIStore((state) => state.userId);
  const { data: user, isLoading, isError } = useUser(userId);
  const isEdit = userId !== null;

  return (
    <div className={styles.userCreate}>
      <h1 className={styles.title}>
        {isEdit ? "Изменение пользователя" : "Создание пользователя"}
      </h1>
      {!isLoading && !isError && <UserCreateForm user={user} isEdit={isEdit} />}
      {isLoading && !isError && (
        <div className={styles.loading}>
          {Array.from({ length: 2 }).map((_, index) => (
            <Sceleton key={index} width="100%" height="50px" />
          ))}
        </div>
      )}
      {isError && (
        <div className={styles.error}>
          <WarningIcon />
          <p className={styles.errorText}>
            Произошла ошибка при загрузке пользователя
          </p>
        </div>
      )}
    </div>
  );
};
