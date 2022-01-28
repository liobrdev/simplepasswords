import { IAccountState } from '@/types';


export const initialAccountState: IAccountState = {
  formOnDeleteUser: false,
  formOnVerifyPhone: false,
  accountModal: undefined,
};

export const accountReducer = (
  state: IAccountState = initialAccountState, 
  action: any,
): IAccountState => {
  switch (action.type) {
    case 'ACCOUNT_FORM_DELETE_SHOW':
      return {
        ...state,
        formOnVerifyPhone: false,
        formOnDeleteUser: true,
      };

    case 'ACCOUNT_FORM_DELETE_CLOSE':
      return {
        ...state,
        formOnDeleteUser: false,
      };

    case 'ACCOUNT_FORM_VERIFY_SHOW':
      return {
        ...state,
        formOnDeleteUser: false,
        formOnVerifyPhone: true,
      };

    case 'ACCOUNT_FORM_VERIFY_CLOSE':
      return {
        ...state,
        formOnVerifyPhone: false,
      };

    case 'ACCOUNT_MODAL_SHOW':
      return { ...state, accountModal: { ...action.accountModal } };

    case 'ACCOUNT_MODAL_CLOSE':
      return { ...state, accountModal: undefined };

    case 'ACCOUNT_RESET':
      return initialAccountState;

    default:
      return state;
  }
};