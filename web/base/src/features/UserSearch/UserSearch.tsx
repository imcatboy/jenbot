import styles from "./UserSearch.module.scss";
import { Fragment, useState } from "react";
import { useDebounce, useUsers } from "@/hooks";
import { useUIStore } from "@/stores";
import { useCallback } from "react";
import { useEffect } from "react";
import { Search, Sceleton, UserCard } from "@/shared/ui";
import { LinkedIcon, UnlinkedIcon, WarningIcon } from "@/assets";
import type { UserResponse } from "@/api/schemas";

export const UserSearch = () => {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);
  const { data, isLoading, isError } = useUsers({
    search: debouncedSearch,
    limit: 10,
    offset: 0,
  });
  const setView = useUIStore((state) => state.setView);
  const setMainButtonConfig = useUIStore((state) => state.setMainButtonConfig);
  const setUserId = useUIStore((state) => state.setUserId);
  const setBackButtonConfig = useUIStore((state) => state.setBackButtonConfig);
  const addUserToDraft = useUIStore((state) => state.addUserToDraft);

  const handleCreateUser = useCallback(() => {
    setView("createUser");
    setUserId(null);
  }, [setView, setUserId]);

  const handleBack = useCallback(() => {
    setView("card");
    setUserId(null);
  }, [setView, setUserId]);

  useEffect(() => {
    setBackButtonConfig({
      isVisible: true,
      onClick: handleBack,
    });
  }, [setBackButtonConfig, handleBack]);

  useEffect(() => {
    setMainButtonConfig({
      isVisible: true,
      isEnabled: debouncedSearch.length >= 3,
      label: "Создать нового пользователя",
      onClick: handleCreateUser,
    });
  }, [setMainButtonConfig, handleCreateUser, debouncedSearch.length]);

  const handleClick = useCallback(
    (user: UserResponse) => {
      addUserToDraft(user);
      setView("card");
    },
    [addUserToDraft, setView],
  );

  return (
    <div className={styles.userSearch}>
      <h1 className={styles.title}>Привязка пользователя</h1>
      <Search
        placeholder="Поиск пользователя..."
        value={search}
        onChange={setSearch}
      />
      {isError && (
        <div className={styles.error}>
          <WarningIcon />
          <p className={styles.errorText}>
            Произошла ошибка при загрузке пользователей
          </p>
        </div>
      )}
      {isLoading && (
        <div className={styles.loading}>
          {Array.from({ length: 6 }).map((_, index) => (
            <Sceleton key={index} width="100%" height="57px" />
          ))}
        </div>
      )}
      {debouncedSearch.length < 3 && (
        <div className={styles.error}>
          <p className={styles.errorText}>
            Начните поиск пользователя по имени или Telegram ID...
          </p>
        </div>
      )}
      {data && data.length === 0 && (
        <div className={styles.error}>
          <p className={styles.errorText}>Ничего не найдено</p>
        </div>
      )}
      {data && (
        <div className={styles.users}>
          {data.map((user, index) => (
            <Fragment key={`user-${user.id}`}>
              {index !== 0 && (
                <hr key={`separator-${index}`} className={styles.separator} />
              )}
              <UserCard
                key={user.id}
                icon={
                  user.reputation_user_id ? <LinkedIcon /> : <UnlinkedIcon />
                }
                iconColor={
                  user.reputation_user_id
                    ? "var(--destructive-color)"
                    : "var(--main-color)"
                }
                title={user.usernames
                  .map((username) => `@${username.username.toLowerCase()}`)
                  .join(" ")}
                description={`${user.telegram_id} ID`}
                onClick={() => handleClick(user)}
              />
            </Fragment>
          ))}
        </div>
      )}
    </div>
  );
};
