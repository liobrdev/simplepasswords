// Misc
export interface IAction {
  type: string;
  [key: string]: any;
}

export interface IBreadcrumbListItem {
  '@type': string;
  position: number;
  name: string;
  item: string;
}

export interface IButton {
  action: IAction;
  text: string;
}

export interface IEntry extends IListEntry {
  value: string;
}

export interface IEntryForm {
  title: string;
  value: string;
  password: string;
}

export interface IErrorMsg {
  id: string;
  msg: string;
}

export interface IErrorInfo {
  [key: string]: IErrorMsg[];
}

export interface IListEntry {
  slug: string;
  title: string;
  created_at: string;
}

export interface IModal {
  page: 'account' | 'dashboard' | 'entry';
  message: string;
  leftButton?: IButton;
  rightButton?: IButton;
}

export interface IRoute {
  path: string;
  name?: string;
}

export interface IUser {
  user_slug: string;
  name: string;
  email: string;
  email_is_verified: boolean;
  phone_number_is_verified: boolean;
  tfa_is_enabled: boolean;
  truncated_phone_number: string;
}

export interface IUserForm {
  name: string;
  email: string;
  phone_number?: string;
  tfa_is_enabled?: boolean;
  password?: string;
  password_2?: string;
  current_password: string;
}

// Reducer states
export interface IAccountState {
  formOnDeleteUser: boolean;
  formOnVerifyPhone: boolean;
  accountModal?: IModal;
}

export interface IDashboardState {
  entries: IListEntry[];
  errorRetrieve?: Error;
  isRetrieving: boolean;
  isCreating: boolean;
  formOnCreateEntry: boolean;
  menuOn: boolean;
  searchBarOn: boolean;
  searchTitle: string;
  dashboardModal?: IModal;
}

export interface IEntryState {
  entry?: IEntry;
  entryModal?: IModal;
  isRetrieving: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  formOnDeleteEntry: boolean;
}

export interface IUserState {
  clientIp?: string;
  isLoggingIn: boolean;
  isLoggingOut: boolean;
  isRegistering: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  user?: IUser;
}