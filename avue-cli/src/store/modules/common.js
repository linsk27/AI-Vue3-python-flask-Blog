import {
  setStore,
  getStore,
  removeStore
} from 'utils/store'
import website from '@/config/website'
const common = {
  state: {
    language: getStore({
      name: 'language'
    }) || 'zh-cn',
    isCollapse: false,
    isFullScren: false,
    isMenu: true,
    isSearch: false,
    isRefresh: true,
    isLock: getStore({
      name: 'isLock'
    }),
    colorName: getStore({
      name: 'colorName'
    }),
    themeName: getStore({
      name: 'themeName'
    }) || 'default',
    lockPasswd: getStore({
      name: 'lockPasswd'
    }) || '',
    website: website,
    setting: website.setting,
    axiosCancelArr: [],
  },
  mutations: {
    PUSH_CANCEL(state, cancel) {
      state.axiosCancelArr.push(cancel.cancelToken);
    },
    CLEAR_CANCEL(state) {
      state.axiosCancelArr.forEach(e => {
        e && e()
      });
      state.axiosCancelArr = []
    },
    SET_LANGUAGE: (state, language) => {
      state.language = language
      setStore({
        name: 'language',
        content: state.language
      })
    },
    SET_COLLAPSE: (state) => {
      state.isCollapse = !state.isCollapse;
    },
    SET_IS_MENU: (state, menu) => {
      state.isMenu = menu;
    },
    SET_IS_REFRESH: (state, refresh) => {
      state.isRefresh = refresh;
    },
    SET_IS_SEARCH: (state, search) => {
      state.isSearch = search;
    },
    SET_FULLSCREN: (state) => {
      state.isFullScren = !state.isFullScren;
    },
    SET_LOCK: (state) => {
      state.isLock = true;
      setStore({
        name: 'isLock',
        content: state.isLock,
        type: 'session'
      })
    },
    SET_COLOR_NAME: (state, colorName) => {
      state.colorName = colorName;
      setStore({
        name: 'colorName',
        content: state.colorName,
      })
    },
    SET_THEME_NAME: (state, themeName) => {
      state.themeName = themeName;
      setStore({
        name: 'themeName',
        content: state.themeName,
      })
    },
    SET_LOCK_PASSWD: (state, lockPasswd) => {
      state.lockPasswd = lockPasswd;
      setStore({
        name: 'lockPasswd',
        content: state.lockPasswd,
        type: 'session'
      })
    },
    CLEAR_LOCK: (state) => {
      state.isLock = false;
      state.lockPasswd = '';
      removeStore({
        name: 'lockPasswd',
        type: 'session'
      });
      removeStore({
        name: 'isLock',
        type: 'session'
      });
    },
  },
  actions: {
    pushCancel({
      commit
    }, cancel) {
      commit('PUSH_CANCEL', cancel)
    },
    clearCancel({
      commit
    }) {
      commit('CLEAR_CANCEL');
    }
  }
}
export default common