import type { AdCardProps } from "./types";
import { Image } from "../Image";
import placeholder from "@/assets/media/placeholder.png";
import styles from "./AdCard.module.scss";
import { CartIcon, FilledStarIcon, TradeIcon } from "@/assets";
import { Button } from "../Button";

export const AdCard = ({ advertisementOption, onClick }: AdCardProps) => {
  return (
    <article className={styles.adCard}>
      <Image key={advertisementOption.image_url} src={advertisementOption.image_url} alt={advertisementOption.name} placeholder={placeholder} size="big" />
      <h2 className={styles.title}>{advertisementOption.name}</h2>
      <p className={styles.category}>{advertisementOption.category_path}</p>
      <div className={styles.prices}>
        {advertisementOption.has_trades && <TradeIcon />}
        {advertisementOption.prices.length > 0 && <><CartIcon /><span className={styles.price}>{advertisementOption.prices[0]}</span></>}
        {advertisementOption.prices.length > 1 && <span className={styles.morePrices}>+{advertisementOption.prices.length - 1}</span>}
      </div>
      <div className={styles.seller}>
        {advertisementOption.user.rating > 0 && <div className={styles.rating}>
          <FilledStarIcon />
          <span className={styles.ratingValue}>{advertisementOption.user.rating.toFixed(1)}</span>
        </div>}
        <span className={styles.sellerName}>{advertisementOption.user.name || `@${advertisementOption.user.username}`}</span>
      </div>
      <div className={styles.options}>
        {advertisementOption.options.map((option) => (
          <span key={option} className={styles.option}>{option}</span>
        ))}
      </div>
      <Button label="Открыть" onClick={onClick} fullWidth type="standard" />
    </article>
  );
};