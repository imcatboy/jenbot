import { useUIStore } from "@/stores";
import { useEffect } from "react";
import { FiltersIcon, WarningIcon } from "@/assets/icons";
import styles from "./Catalog.module.scss";
import { useCatalogStore } from "@/stores/catalog";
import { useMarketplace } from "@/hooks";
import { AdCard, Sceleton } from "@/shared/ui";

export const Catalog = () => {
  const setSubView = useUIStore((state) => state.setSubView);
  const setHeaderConfig = useUIStore((state) => state.setHeaderConfig);
  const resetHeaderConfig = useUIStore((state) => state.resetHeaderConfig);
  const activeFilters = useCatalogStore((state) => state.activeFilters);
  const { data, isLoading, isError } = useMarketplace(activeFilters);

  useEffect(() => {
    setHeaderConfig({
      search: {
        placeholder: "Найти объявление...",
        onFocus: () => setSubView("search"),
      },
      rightButton: {
        icon: <FiltersIcon />,
        onClick: () => setSubView("filters"),
      },
    });
    return () => {
      resetHeaderConfig();
    };
  }, [setHeaderConfig, resetHeaderConfig, setSubView]);

  return (
    <div className={styles.catalog}>
      {isLoading && <div className={styles.ads}>{Array.from({ length: 6 }).map((_, index) => (
        <Sceleton key={index} width="100%" height="300px" />
      ))}</div>}
      {isError && <div className={styles.error}>
        <WarningIcon />
        <p>Произошла ошибка при загрузке объявлений</p>
      </div>}
      {data && data.items.length === 0 && <div className={styles.error}>
        <p>Ничего не найдено</p>
      </div>}
      {data && <div className={styles.ads}>{data.items.map((ad) => (
        <AdCard key={ad.id} advertisementOption={ad} onClick={() => {}} />
      ))}</div>}
    </div>
  );
};