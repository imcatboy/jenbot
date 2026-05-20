import type { ImageProps } from "./types";
import { useState } from "react";
import clsx from "clsx";
import styles from "./Image.module.scss";
import WebApp from "@twa-dev/sdk";

export const Image = ({ src, alt, placeholder, size }: ImageProps) => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:4000';
  const initData = import.meta.env.PROD ? WebApp.initData : "XXXX";
  const [currentSrc, setCurrentSrc] = useState(`${baseUrl}${src}?init_data=${initData}`);

  const handleError = () => {
    if (currentSrc !== placeholder) {
      setCurrentSrc(placeholder);
    }
  };

  return (
    <img src={currentSrc} alt={alt} onError={handleError} className={clsx(styles.image, styles[size])} />
  );
};