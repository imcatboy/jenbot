import { useUIStore } from "@/stores";
import { CatalogIcon, MessageIcon, ProfileIcon, AdIcon } from "@/assets";
import { Tab } from "@/shared/ui";
import styles from "./TabBar.module.scss";


export const TabBar = () => {
  const isTabbarVisible = useUIStore((state) => state.isTabbarVisible);
  const setView = useUIStore((state) => state.setView);
  const view = useUIStore((state) => state.view);

  if (!isTabbarVisible) return null;

  return (
    <nav className={styles.tabBar}>
      <Tab icon={<CatalogIcon />} label="Каталог" onClick={() => setView('catalog')} isActive={view === 'catalog'} />
      <Tab icon={<MessageIcon />} label="Чат" onClick={() => setView('chat')} isActive={view === 'chat'} />
      <Tab icon={<ProfileIcon />} label="Профиль" onClick={() => setView('profile')} isActive={view === 'profile'} />
      <Tab icon={<AdIcon />} label="Объявления" onClick={() => setView('advertisement')} isActive={view === 'advertisement'} />
    </nav>
  );
};