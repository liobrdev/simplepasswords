import { combineReducers } from 'redux';

import { accountReducer, initialAccountState } from './account';
import { entryReducer, initialEntryState } from './entry';
import { dashboardReducer, initialDashboardState } from './dashboard';
import { userReducer, initialUserState } from './user';


const reducers = {
  account: accountReducer,
  entry: entryReducer,
  dashboard: dashboardReducer,
  user: userReducer,
};

export const initialAppState = {
  account: initialAccountState,
  entry: initialEntryState,
  dashboard: initialDashboardState,
  user: initialUserState,
};

export default combineReducers(reducers);