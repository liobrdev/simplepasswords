import { IEntryState } from '@/types';


export const initialEntryState: IEntryState = {
  entry: undefined,
  entryModal: undefined,
  isRetrieving: false,
  isUpdating: false,
  isDeleting: false,
  formOnDeleteEntry: false,
};

export const entryReducer = (
  state: IEntryState = initialEntryState,
  action: any,
): IEntryState => {
  switch (action.type) {
    case 'START_RETRIEVE_ENTRY':
      return { ...state, isRetrieving: true };

    case 'STOP_RETRIEVE_ENTRY':
      return { ...state, isRetrieving: false };

    case 'SUCCESS_RETRIEVE_ENTRY':
      return { ...state, entry: action.entry, isRetrieving: false };

    case 'START_UPDATE_ENTRY':
      return { ...state, isUpdating: true };

    case 'STOP_UPDATE_ENTRY':
      return { ...state, isUpdating: false };

    case 'SUCCESS_UPDATE_ENTRY':
      return { ...state, entry: action.entry, isUpdating: false };

    case 'START_DELETE_ENTRY':
      return { ...state, isDeleting: true };

    case 'STOP_DELETE_ENTRY':
      return { ...state, isDeleting: false };

    case 'SUCCESS_DELETE_ENTRY':
      return { ...state, entry: undefined, isDeleting: false };

    case 'ENTRY_MODAL_SHOW':
      return { ...state, entryModal: { ...action.entryModal } };

    case 'ENTRY_MODAL_CLOSE':
      return { ...state, entryModal: undefined };

    case 'ENTRY_FORM_DELETE_SHOW':
      return {
        ...state,
        formOnDeleteEntry: true,
      };

    case 'ENTRY_FORM_DELETE_CLOSE':
      return {
        ...state,
        formOnDeleteEntry: false,
      };

    case 'ENTRY_RESET':
      return { ...initialEntryState };

    default:
      return state;
  }
};