import type { SearchProps } from "./types";
import styles from "./Search.module.scss";
import { Button } from "../Button";
import { ArrowLeftIcon, SearchIcon } from "@/assets/icons";


export const Search = ({ placeholder, onChange, value, onCancel, onFocus }: SearchProps) => {
  return (
    <div className={styles.search}>
      {!onCancel && <SearchIcon />}
      {onCancel && <Button icon={<ArrowLeftIcon />} onClick={onCancel} />}
      <input type="text" placeholder={placeholder} value={value || ""} onFocus={onFocus} onChange={(e) => onChange?.(e.target.value)} />
    </div>
  );
};