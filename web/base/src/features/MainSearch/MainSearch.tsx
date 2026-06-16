import { Search, Sceleton, UserCard } from "@/shared/ui";
import styles from "./MainSearch.module.scss";
import { Fragment, useCallback, useState } from "react";
import { useDebounce, useReputationUsers } from "@/hooks";
import { WarningIcon } from "@/assets";
import { ROLE_ICONS, ROLE_NAMES } from "./MainSearch.config";
import { useUIStore } from "@/stores";
import { useEffect } from "react";

export const MainSearch = () => {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);
  const { data, isLoading, isError } = useReputationUsers(debouncedSearch);
  const setView = useUIStore((state) => state.setView);
  const setMainButtonConfig = useUIStore((state) => state.setMainButtonConfig);
  const setCardId = useUIStore((state) => state.setCardId);

  const handleCreateCard = useCallback(() => {
    setView("card");
    setCardId(null);
  }, [setView, setCardId]);

  useEffect(() => {
    setMainButtonConfig({
      isVisible: true,
      isEnabled: debouncedSearch.length >= 3,
      label: "Создать новую карточку",
      onClick: handleCreateCard,
    });
  }, [setMainButtonConfig, handleCreateCard, debouncedSearch.length]);

  const handleClick = (reputationUserId: number) => {
    setCardId(reputationUserId);
    setView("card");
  };

  return (
    <div className={styles.mainSearch}>
      <h1 className={styles.title}>LarionBase</h1>
      <Search
        placeholder="Поиск репутации..."
        value={search}
        onChange={setSearch}
      />
      {isError && (
        <div className={styles.error}>
          <WarningIcon />
          <p className={styles.errorText}>
            Произошла ошибка при загрузке карточек репутаций
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
            Начните поиск карточки репутации по реквизитам или пользователям...
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
                icon={ROLE_ICONS[user.role]}
                iconColor={"var(--main-color)"}
                title={user.users
                  .map((user) =>
                    user.usernames.length > 0
                      ? user.usernames.map(
                          (username) => `@${username.username.toLowerCase()}`,
                        )
                      : [user.telegram_id.toString()],
                  )
                  .join(" ")}
                description={ROLE_NAMES[user.role]}
                onClick={() => handleClick(user.id)}
              />
            </Fragment>
          ))}
        </div>
      )}
    </div>
  );
};
