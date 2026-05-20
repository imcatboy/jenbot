import { MainButtonController, BackButtonController, TabBar, Header, MainButtonMock } from '@/shared/components'
import { useUIStore } from '@/stores';
import { Catalog, CatalogSearch, CatalogFilters } from '@/features';
import styles from './App.module.scss';

function App() {
  const view = useUIStore((state) => state.view);
  const subView = useUIStore((state) => state.subView);

  return (
    <div className={styles.app}>
      <MainButtonController />
      <BackButtonController />
      <Header>
        {view === 'catalog' && subView === undefined && <Catalog />}
        {view === 'catalog' && subView === 'search' && <CatalogSearch />}
        {view === 'catalog' && subView === 'filters' && <CatalogFilters />}
      </Header>
      <TabBar />
      <MainButtonMock />
    </div>
  )
}

export default App
