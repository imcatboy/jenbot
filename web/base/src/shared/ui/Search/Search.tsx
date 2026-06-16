import { SearchIcon } from "@/assets";
import type { SearchProps } from "./types";
import styles from "./Search.module.scss";

export const Search = ({ value, onChange, placeholder }: SearchProps) => {
  return (
    <div className={styles.search}>
      <SearchIcon />
      <input
        className={styles.input}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
};
