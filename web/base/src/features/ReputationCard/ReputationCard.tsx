import {
  AreaField,
  Dropdown,
  LinkedUser,
  ReadableField,
  Select,
  CreateButton,
  Sceleton,
  Detail,
  ReportCardAdd,
  ReportCard,
} from "@/shared/ui";
import styles from "./ReputationCard.module.scss";
import {
  DISABLED_MODERATION_ROLES,
  REPUTATION_ROLES,
} from "./ReputationCard.config";
import { useUIStore } from "@/stores";
import type { ReputationUserDraft } from "@/types/draft";
import {
  useReputationUser,
  useCreateReputationUser,
  useUpdateReputationUser,
  useMyUser,
} from "@/hooks";
import { useCallback, useEffect } from "react";
import { draftToCreateRequest, draftToUpdateRequest } from "@/utils";
import { WarningIcon } from "@/assets/icons";
import type { ScamReportResponse } from "@/api";

export const ReputationCard = () => {
  const draft = useUIStore((state) => state.draft);
  const cardId = useUIStore((state) => state.cardId);
  const isDirty = useUIStore((state) => state.isDirty);
  const setView = useUIStore((state) => state.setView);
  const setUserId = useUIStore((state) => state.setUserId);
  const setDetailId = useUIStore((state) => state.setDetailId);
  const setCardId = useUIStore((state) => state.setCardId);
  const updateDraft = useUIStore((state) => state.updateDraft);
  const initDraft = useUIStore((state) => state.initDraft);
  const initEmptyDraft = useUIStore((state) => state.initEmptyDraft);
  const clearDraft = useUIStore((state) => state.clearDraft);
  const setMainButtonConfig = useUIStore((state) => state.setMainButtonConfig);
  const setBackButtonConfig = useUIStore((state) => state.setBackButtonConfig);
  const {
    data: reputationUser,
    isLoading,
    isError,
  } = useReputationUser(cardId);
  const { data: currentUser } = useMyUser();
  const { mutate: updateReputationUser } = useUpdateReputationUser();
  const { mutate: createReputationUser } = useCreateReputationUser();
  const isAdmin = currentUser?.role === "admin";

  const handleCreateUser = () => {
    setUserId(null);
    setView("userSearch");
  };

  const handleEditUser = (id: number) => {
    setUserId(id);
    setView("createUser");
  };

  const handleRemoveUser = useCallback(
    (id: number) => {
      updateDraft({ users: draft?.users.filter((user) => user.id !== id) });
    },
    [updateDraft, draft],
  );

  const handleEditDetail = (id: number) => {
    setDetailId(id);
    setView("createDetail");
  };

  const handleRemoveDetail = useCallback(
    (id: number) => {
      updateDraft({
        user_details: draft?.user_details.filter((detail) => detail.id !== id),
      });
    },
    [updateDraft, draft],
  );

  const handleCreateDetail = () => {
    setDetailId(null);
    setView("createDetail");
  };

  const handleAddReport = useCallback(
    (report: ScamReportResponse) => {
      updateDraft({
        accused_reports: [...(draft?.accused_reports || []), report],
      });
    },
    [updateDraft, draft],
  );

  const handleRemoveReport = useCallback(
    (id: number) => {
      updateDraft({
        accused_reports: draft?.accused_reports.filter(
          (report) => report.id !== id,
        ),
      });
    },
    [updateDraft, draft],
  );

  const handleSave = useCallback(() => {
    if (!draft) return;

    const onSuccess = () => {
      clearDraft();
      setView("home");
    };

    if (cardId) {
      updateReputationUser(
        {
          id: cardId,
          request: draftToUpdateRequest(draft),
        },
        { onSuccess },
      );
    } else {
      createReputationUser(draftToCreateRequest(draft), { onSuccess });
    }
  }, [
    draft,
    cardId,
    updateReputationUser,
    createReputationUser,
    clearDraft,
    setView,
  ]);

  const handleBack = useCallback(() => {
    setView("home");
    setCardId(null);
    clearDraft();
  }, [setView, setCardId, clearDraft]);

  useEffect(() => {
    setMainButtonConfig({
      isVisible: true,
      isEnabled: isDirty,
      label: "Сохранить",
      onClick: handleSave,
    });
  }, [setMainButtonConfig, handleSave, isDirty]);

  useEffect(() => {
    if (reputationUser && !draft) {
      initDraft(reputationUser);
    } else if (!cardId && !draft) {
      initEmptyDraft();
    }
  }, [reputationUser, initDraft, draft, initEmptyDraft, cardId]);

  useEffect(() => {
    setBackButtonConfig({
      isVisible: true,
      onClick: handleBack,
    });
  }, [setBackButtonConfig, handleBack]);

  return (
    <div className={styles.reputationCard}>
      <h1 className={styles.title}>Информация</h1>
      {isLoading && (
        <div className={styles.loading}>
          {Array.from({ length: 6 }).map((_, index) => (
            <Sceleton key={index} width="100%" height="57px" />
          ))}
        </div>
      )}
      {isError && (
        <div className={styles.error}>
          <WarningIcon />
          <p className={styles.errorText}>
            Произошла ошибка при загрузке информации
          </p>
        </div>
      )}
      {!isLoading && !isError && draft && (
        <>
          <div className={styles.info}>
            <Select
              options={REPUTATION_ROLES}
              title="Роль"
              placeholder="Выберите роль..."
              value={draft?.role}
              onChange={(value) =>
                updateDraft({ role: value as ReputationUserDraft["role"] })
              }
              disabled={
                DISABLED_MODERATION_ROLES.includes(draft?.role) && !isAdmin
              }
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
              disabled={!isAdmin}
            />
            <AreaField
              title="Комментарий пользователя"
              value={draft?.about ?? ""}
              disabled
            />
          </div>
          <Dropdown title="Пользователи" className={styles.dropdown}>
            {draft?.users.map((user) => (
              <LinkedUser
                key={`user-${user.id}`}
                user={user}
                onEdit={() => handleEditUser(user.id)}
                onRemove={() => handleRemoveUser(user.id)}
              />
            ))}
            <CreateButton
              label="Добавить пользователя"
              onClick={handleCreateUser}
            />
          </Dropdown>
          <Dropdown title="Реквизиты" className={styles.dropdown}>
            {draft?.user_details.map((detail) => (
              <Detail
                key={`detail-${detail.id}`}
                detail={detail}
                onEdit={() => handleEditDetail(detail.id)}
                onRemove={() => handleRemoveDetail(detail.id)}
              />
            ))}
            <CreateButton
              label="Добавить реквизит"
              onClick={handleCreateDetail}
            />
          </Dropdown>
          <Dropdown title="Жалобы" className={styles.dropdown}>
            {draft?.accused_reports.map((report) => (
              <ReportCard
                key={`report-${report.id}`}
                report={report}
                onRemove={() => handleRemoveReport(report.id)}
              />
            ))}
            <ReportCardAdd
              onAdd={handleAddReport}
              existingReports={draft?.accused_reports || []}
            />
          </Dropdown>
        </>
      )}
    </div>
  );
};
