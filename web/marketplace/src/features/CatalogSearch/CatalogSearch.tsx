import { useEffect, useState, useCallback, useMemo } from "react";
import { useUIStore } from "@/stores";
import { FiltersIcon, WarningIcon } from "@/assets";
import { useAdvertisementSuggestions, useDebounce } from "@/hooks";
import { useCatalogStore } from "@/stores";
import type { AdvertisementSuggestionResponse, GetAdvertisementSuggestionsRequest } from "@/api/schemas";
import styles from "./CatalogSearch.module.scss";
import { Option, Sceleton } from "@/shared/ui";

export const CatalogSearch = () => {
  const setHeaderConfig = useUIStore((state) => state.setHeaderConfig);
  const setSubView = useUIStore((state) => state.setSubView);
  const resetSubView = useUIStore((state) => state.resetSubView);
  const resetHeaderConfig = useUIStore((state) => state.resetHeaderConfig);
  const draftFilters = useCatalogStore((state) => state.draftFilters);
  const applyDraftFilters = useCatalogStore((state) => state.applyDraftFilters);
  const selectedSuggestions = useCatalogStore((state) => state.selectedSuggestions);
  const addSelectedSuggestion = useCatalogStore((state) => state.addSelectedSuggestion);
  const removeSelectedSuggestion = useCatalogStore((state) => state.removeSelectedSuggestion);
  const setMainButtonConfig = useUIStore((state) => state.setMainButtonConfig);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);
  const suggestionRequest: GetAdvertisementSuggestionsRequest = {
    search: debouncedSearch,
    limit: 10,
    offset: 0,
    category_ids: draftFilters.category_ids,
    product_ids: draftFilters.product_ids,
    seller_ids: draftFilters.seller_ids,
    product_option_ids: draftFilters.product_option_ids,
  };
  const { data, isLoading, isError } = useAdvertisementSuggestions(suggestionRequest);

  const filteredSuggestions = useMemo(() => {
    if (!data) return [];

    const selectedIds = selectedSuggestions.map((suggestion) => `${suggestion.id}-${suggestion.kind}`);

    return data.filter((suggestion) => !selectedIds.includes(`${suggestion.id}-${suggestion.kind}`));
  }, [data, selectedSuggestions]);

  const handleApplyFilters = useCallback(() => {
    applyDraftFilters();
    resetSubView();
  }, [applyDraftFilters, resetSubView]);

  const handleAddSelectedSuggestion = useCallback((suggestion: AdvertisementSuggestionResponse) => {
    setSearch("");
    addSelectedSuggestion(suggestion);
  }, [addSelectedSuggestion, setSearch]);

  useEffect(() => {
    setMainButtonConfig({
      label: "Применить",
      onClick: handleApplyFilters,
      isVisible: true,
    });
    return () => {
      setMainButtonConfig({
        isVisible: false,
      });
    };
  }, [selectedSuggestions, handleApplyFilters, setMainButtonConfig]);

  useEffect(() => {
    setHeaderConfig({
      search: {
        placeholder: "Найти объявление...",
        onChange: (value) => setSearch(value),
        onCancel: resetSubView,
        value: search,
      },
      rightButton: {
        icon: <FiltersIcon />,
        onClick: () => setSubView("filters"),
      },
    });
    return () => {
      resetHeaderConfig();
    };
  }, [setHeaderConfig, resetHeaderConfig, search, resetSubView, setSubView]);
  return (
    <div className={styles.catalogSearch}>
      {(selectedSuggestions.length > 0 || filteredSuggestions.length > 0) && (
        <div className={styles.suggestions}>
          {selectedSuggestions.map((suggestion) => (
            <Option
              key={`${suggestion.id}-${suggestion.kind}`}
              label={suggestion.title}
              type="checkbox"
              checked={true}
              onClick={() => removeSelectedSuggestion(suggestion)}
            />
          ))}
          {filteredSuggestions.map((suggestion) => (
            <Option
              key={`${suggestion.id}-${suggestion.kind}`}
              label={suggestion.title}
              type="checkbox"
              onClick={() => handleAddSelectedSuggestion(suggestion)}
            />
          ))}
        </div>
      )}
      {isLoading && (
        <div className={styles.suggestions}>
          {Array.from({ length: 10 }).map((_, index) => (
            <Sceleton key={index} width={`${index % 2 === 0 ? "63px" : "100px"}`} height="43px" />
          ))}
        </div>
      )}
      {isError && (
        <div className={styles.error}>
          <WarningIcon />
          <p>Произошла ошибка при загрузке подсказок</p>
        </div>
      )}
      {debouncedSearch.length < 3 && !isLoading && !isError && filteredSuggestions.length === 0 && selectedSuggestions.length === 0 && (
        <div className={styles.error}>
          <p>Начните поиск среди категорий, товаров, опций или продавцов</p>
        </div>
      )}
      {debouncedSearch.length < 3 && selectedSuggestions.length > 0 && !isLoading && !isError && (
        <div className={styles.error}>
        <p>Продолжайте поиск среди категорий, товаров, опций или продавцов</p>
      </div>
      )}
      {debouncedSearch.length >= 3 && data && data.length === 0 && !isLoading && !isError && (
        <div className={styles.error}>
          <p>Ничего не найдено</p>
        </div>
      )}
    </div>
  );
};