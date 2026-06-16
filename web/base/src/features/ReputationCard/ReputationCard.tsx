import { AreaField, Dropdown, ReadableField, Select } from "@/shared/ui";
import styles from "./ReputationCard.module.scss";
import { REPUTATION_ROLES } from "./ReputationCard.config";
import { useUIStore } from "@/stores";
import type { ReputationUserDraft } from "@/types/draft";
import {
  useReputationUser,
  useCreateReputationUser,
  useUpdateReputationUser,
  useMyUser,
} from "@/hooks";
import { useCallback, useEffect } from "react";
import { draftToCreateRequest, draftToUpdateRequest } from "@/mappers";

export const ReputationCard = () => {
  const draft = useUIStore((state) => state.draft);
  const cardId = useUIStore((state) => state.cardId);
  const isDirty = useUIStore((state) => state.isDirty);
  const updateDraft = useUIStore((state) => state.updateDraft);
  const initDraft = useUIStore((state) => state.initDraft);
  const setMainButtonConfig = useUIStore((state) => state.setMainButtonConfig);
  const { data: reputationUser } = useReputationUser(cardId);
  const { data: currentUser } = useMyUser();
  const { mutate: updateReputationUser } = useUpdateReputationUser();
  const { mutate: createReputationUser } = useCreateReputationUser();
  const isAdmin = currentUser?.role === "admin";

  const handleSave = useCallback(() => {
    if (!draft) return;

    if (cardId) {
      updateReputationUser({
        id: cardId,
        request: draftToUpdateRequest(draft),
      });
    } else {
      createReputationUser(draftToCreateRequest(draft));
    }
  }, [draft, cardId, updateReputationUser, createReputationUser]);

  useEffect(() => {
    setMainButtonConfig({
      isVisible: true,
      isEnabled: isDirty,
      label: "Сохранить",
      onClick: handleSave,
    });
  }, [setMainButtonConfig, handleSave, isDirty]);

  useEffect(() => {
    if (reputationUser) {
      initDraft(reputationUser);
    }
  }, [reputationUser, initDraft]);

  return (
    <div className={styles.reputationCard}>
      <h1 className={styles.title}>Информация</h1>
      <div className={styles.info}>
        <Select
          options={REPUTATION_ROLES}
          title="Роль"
          placeholder="Выберите роль..."
          value={draft?.role}
          onChange={(value) =>
            updateDraft({ role: value as ReputationUserDraft["role"] })
          }
          disabled={!isAdmin}
        />
        <ReadableField
          title="Доверенность"
          value={draft?.amount.toString() ?? "0"}
          onSave={(value) => updateDraft({ amount: Number(value) || 0.0 })}
          disabled={!isAdmin}
          type="number"
        />
        <AreaField
          title="Описание"
          value={draft?.description ?? ""}
          onSave={(value) => updateDraft({ description: value })}
        />
        <AreaField
          title="Комментарий пользователя"
          value={draft?.about ?? ""}
          disabled
        />
      </div>
      <Dropdown title="Пользователи">
        <h3 className={styles.dropdownTitle}>Пользователи</h3>
      </Dropdown>
    </div>
  );
};
