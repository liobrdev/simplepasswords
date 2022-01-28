import { IDashboardState } from '@/types';


export const initialDashboardState: IDashboardState = {
  entries: [],
  errorRetrieve: undefined,
  isRetrieving: false,
  isCreating: false,
  formOnCreateEntry: false,
  menuOn: false,
  searchBarOn: false,
  dashboardModal: undefined,
};

export const dashboardReducer = (
  state: IDashboardState = initialDashboardState, 
  action: any,
): IDashboardState => {
  switch (action.type) {
    case 'START_RETRIEVE_ENTRIES':
      return {
        ...state,
        isRetrieving: true,
      };

    case 'STOP_RETRIEVE_ENTRIES':
      return {
        ...state,
        isRetrieving: false,
      };

    case 'START_CREATE_ENTRY':
      return {
        ...state,
        isCreating: true,
      };

    case 'STOP_CREATE_ENTRY':
      return {
        ...state,
        isCreating: false,
      };

    case 'SUCCESS_CREATE_ENTRY':
      return {
        ...state,
        entries: [action.entry, ...state.entries],
        formOnCreateEntry: false,
        isCreating: false,
      };

    case 'DASHBOARD_FORM_SHOW':
      return {
        ...state,
        formOnCreateEntry: true,
        menuOn: false,
        searchBarOn: false,
      };

    case 'DASHBOARD_FORM_CLOSE':
      return {
        ...state,
        formOnCreateEntry: false,
      };

    case 'DASHBOARD_MENU_SHOW':
      return {
        ...state,
        formOnCreateEntry: false,
        menuOn: true,
        searchBarOn: false,
      };

    case 'DASHBOARD_MENU_CLOSE':
      return {
        ...state,
        menuOn: false,
      };

    case 'DASHBOARD_SEARCHBAR_SHOW':
      return {
        ...state,
        formOnCreateEntry: false,
        menuOn: false,
        searchBarOn: true,
      };

    case 'DASHBOARD_SEARCHBAR_CLOSE':
      return {
        ...state,
        searchBarOn: false,
      };

    case 'DASHBOARD_SET_ENTRIES':
      return {
        ...state,
        entries: action.data,
        errorRetrieve: action.error,
      };

    case 'DASHBOARD_MODAL_SHOW':
      return { ...state, dashboardModal: { ...action.dashboardModal } };

    case 'DASHBOARD_MODAL_CLOSE':
      return { ...state, dashboardModal: undefined };

    case 'DASHBOARD_RESET':
      return initialDashboardState;

    default:
      return state;
  }
};