import { MainButtonController } from '@/shared/components'
import styles from './App.module.scss';
import { MainButtonMock } from '@/shared/components';

function App() {
  return (
    <div className={styles.app}>
      <MainButtonController />
      <h1>LarionBase</h1>
      <MainButtonMock />
    </div>
  )
}

export default App
