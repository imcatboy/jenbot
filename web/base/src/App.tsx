import { ErrorAlert, MainButtonController } from "@/shared/components";
import styles from "./App.module.scss";
import {
  MainSearch,
  ReputationCard,
  UserCreate,
  UserSearch,
  DetailCreate,
} from "@/features";
import { useUIStore } from "@/stores";

function App() {
  const view = useUIStore((state) => state.view);
  return (
    <div className={styles.app}>
      {view === "home" && <MainSearch />}
      {view === "card" && <ReputationCard />}
      {view === "userSearch" && <UserSearch />}
      {view === "createUser" && <UserCreate />}
      {view === "createDetail" && <DetailCreate />}
      <MainButtonController />
      <ErrorAlert />
    </div>
  );
}

export default App;
