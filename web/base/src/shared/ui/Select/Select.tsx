import type { SelectProps } from "./types";
import styles from "./Select.module.scss";
import { ArrowDownIcon } from "@/assets";
import { Fragment, useEffect, useRef, useState } from "react";
import clsx from "clsx";

export const Select = ({
  options,
  placeholder,
  title,
  value,
  onChange,
  disabled,
}: SelectProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);
  const selectedOption = options.find((option) => option.value === value);

  const handleOpen = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleChange = (value: string) => {
    onChange(value);
    setIsOpen(false);
  };

  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (
        event.target instanceof HTMLElement &&
        !selectRef.current?.contains(event.target as HTMLElement)
      ) {
        setIsOpen(false);
      }
    };

    const timer = setTimeout(() => {
      document.addEventListener("mousedown", handleClickOutside);
    }, 0);

    return () => {
      clearTimeout(timer);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen, setIsOpen]);

  return (
    <div className={styles.select} ref={selectRef}>
      <div className={styles.selectHeader} onClick={handleOpen}>
        <h3 className={styles.title}>{title}</h3>
        <hr className={styles.divider} />
        <div className={styles.selectedOptionContainer}>
          {selectedOption ? (
            <div className={styles.selectedOptionValue}>
              <div className={styles.optionIcon}>{selectedOption.icon}</div>
              <div className={styles.optionLabel}>{selectedOption.label}</div>
            </div>
          ) : (
            <div className={styles.selectedOptionPlaceholder}>
              {placeholder}
            </div>
          )}
          {!disabled && (
            <div className={clsx(styles.arrow, isOpen && styles.open)}>
              <ArrowDownIcon />
            </div>
          )}
        </div>
      </div>
      {isOpen && (
        <div className={styles.options}>
          {options.map((option, index) => (
            <Fragment key={`select-${option.value}-${index}`}>
              {index !== 0 && <hr className={styles.divider} />}
              <div
                className={styles.option}
                key={`select-${option.value}-${index}`}
                onClick={() => handleChange(option.value)}
              >
                <div className={styles.optionIcon}>{option.icon}</div>
                <div className={styles.optionLabel}>{option.label}</div>
              </div>
            </Fragment>
          ))}
        </div>
      )}
    </div>
  );
};
