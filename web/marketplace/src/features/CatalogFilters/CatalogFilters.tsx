import { useEffect } from "react";
import { useUIStore } from "@/stores";
import { ArrowUpIcon } from "@/assets/icons";

export const CatalogFilters = () => {
  const setHeaderConfig = useUIStore((state) => state.setHeaderConfig);
  const resetHeaderConfig = useUIStore((state) => state.resetHeaderConfig);
  const setSubView = useUIStore((state) => state.setSubView);
  const resetSubView = useUIStore((state) => state.resetSubView);

  useEffect(() => {
    setHeaderConfig({
      search: {
        placeholder: "Найти объявление...",
        onFocus: () => setSubView("search"),
      },
      rightButton: {
        icon: <ArrowUpIcon />,
        onClick: resetSubView,
      },
    });
    return () => {
      resetHeaderConfig();
    };
  }, [setHeaderConfig, resetHeaderConfig, setSubView, resetSubView]);
  return (
    <div>
      <h1>CatalogFilters</h1>
    </div>
  );
};