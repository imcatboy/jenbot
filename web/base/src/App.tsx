import { MainButtonController } from "@/shared/components";
import styles from "./App.module.scss";
import { MainButtonMock } from "@/shared/components";
import { MainSearch, ReputationCard } from "@/features";
import { useUIStore } from "@/stores";

function App() {
  const view = useUIStore((state) => state.view);
  return (
    <div className={styles.app}>
      {view === "home" && <MainSearch />}
      {view === "card" && <ReputationCard />}
      <MainButtonController />
      <MainButtonMock />
    </div>
  );
}

export default App;
