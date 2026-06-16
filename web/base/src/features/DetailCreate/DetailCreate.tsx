import styles from "./DetailCreate.module.scss";
import { useUIStore } from "@/stores";
import { useCallback, useEffect, useState } from "react";
import { TextField, Checkbox } from "@/shared/ui";

export const DetailCreate = () => {
  const detailId = useUIStore((state) => state.detailId);
  const draft = useUIStore((state) => state.draft);
  const detail = draft?.user_details.find((detail) => detail.id === detailId);
  const setMainButtonConfig = useUIStore((state) => state.setMainButtonConfig);
  const setBackButtonConfig = useUIStore((state) => state.setBackButtonConfig);
  const setDetailId = useUIStore((state) => state.setDetailId);
  const setView = useUIStore((state) => state.setView);
  const updateUserDetailInDraft = useUIStore(
    (state) => state.updateUserDetailInDraft,
  );
  const addUserDetailToDraft = useUIStore(
    (state) => state.addUserDetailToDraft,
  );
  const [name, setName] = useState<string>(detail?.name ?? "");
  const [value, setValue] = useState<string>(detail?.value ?? "");
  const [isPublic, setIsPublic] = useState<boolean>(detail?.is_public ?? false);
  const isValid = name.length > 0 && value.length > 0;

  const handleSave = useCallback(() => {
    if (!isValid) return;

    if (detailId) {
      if (!detail) return;

      updateUserDetailInDraft({
        id: detailId,
        name,
        value,
        is_public: isPublic,
      });
    } else {
      addUserDetailToDraft({
        id: Date.now(),
        name,
        value,
        is_public: isPublic,
      });
    }

    setView("card");
  }, [
    updateUserDetailInDraft,
    addUserDetailToDraft,
    setView,
    isValid,
    detailId,
    name,
    value,
    isPublic,
    detail,
  ]);

  const handleBack = useCallback(() => {
    setView("card");
    setDetailId(null);
  }, [setView, setDetailId]);

  useEffect(() => {
    setBackButtonConfig({
      isVisible: true,
      onClick: handleBack,
    });
  }, [setBackButtonConfig, handleBack]);

  useEffect(() => {
    setMainButtonConfig({
      isVisible: true,
      isEnabled: isValid,
      label: "Сохранить",
      onClick: handleSave,
    });
  }, [setMainButtonConfig, isValid, handleSave]);

  return (
    <div className={styles.detailCreate}>
      <h1 className={styles.title}>
        {detailId ? "Изменение реквизита" : "Создание реквизита"}
      </h1>
      <TextField
        placeholder="Название"
        value={name}
        onChange={(value) => setName(value)}
        type="text"
      />
      <TextField
        placeholder="Значение"
        value={value}
        onChange={(value) => setValue(value)}
        type="text"
      />
      <Checkbox
        label="Отображать для всех"
        value={isPublic}
        onChange={(value) => setIsPublic(value)}
      />
    </div>
  );
};
