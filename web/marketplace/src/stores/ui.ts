import { create } from 'zustand';
import type { HeaderConfig } from '@/shared/components';


type View = 'catalog' | 'profile' | 'chat' | 'advertisement';
type SubView = 'search' | 'filters';


interface MainButtonConfig {
  label: string;
  isEnabled: boolean;
  isVisible: boolean;
  isLoading: boolean;
  onClick: () => void;
}

interface UIStore {
  view: View;
  subView?: SubView;
  setSubView: (subView: SubView) => void;
  subViewHistory: SubView[];
  popSubView: () => void;
  resetSubView: () => void;
  setView: (view: View) => void;
  isTabbarVisible: boolean;
  setIsTabbarVisible: (isVisible: boolean) => void;
  mainButtonConfig: MainButtonConfig;
  setMainButtonConfig: (config: Partial<MainButtonConfig>) => void;
  headerConfig: HeaderConfig;
  setHeaderConfig: (config: HeaderConfig) => void;
  resetHeaderConfig: () => void;
}


export const useUIStore = create<UIStore>((set) => ({
  view: 'catalog',
  setView: (view: View) => set({ view: view, subView: undefined, subViewHistory: [] }),
  subView: undefined,
  subViewHistory: [],
  resetSubView: () => set({ subView: undefined, subViewHistory: [] }),
  setSubView: (subView: SubView) => set((state) => ({
    subViewHistory: [...state.subViewHistory, subView],
    subView: subView,
  })),
  popSubView: () => set((state) => {
    const newHistory = state.subViewHistory.slice(0, -1);
    const previousSubView = newHistory[newHistory.length - 1]; 
    return {
      subViewHistory: newHistory,
      subView: previousSubView,
    };
  }),
  isTabbarVisible: true,
  setIsTabbarVisible: (isVisible: boolean) => set({ isTabbarVisible: isVisible }),
  mainButtonConfig: {
    label: 'MainButton',
    isEnabled: true,
    isVisible: false,
    isLoading: false,
    onClick: () => {},
  },
  setMainButtonConfig: (config: Partial<MainButtonConfig>) => set((state) => ({ mainButtonConfig: { ...state.mainButtonConfig, ...config } })),
  headerConfig: {},
  setHeaderConfig: (config: HeaderConfig) => set({ headerConfig: config }),
  resetHeaderConfig: () => set({ headerConfig: {} }),
}))