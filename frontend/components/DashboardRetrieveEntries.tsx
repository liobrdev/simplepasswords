import { useEffect } from 'react';
import useSWR from 'swr';

import { useAppDispatch, useAppSelector, useDebounce } from '@/hooks';

import { checkListEntry, IListEntry } from '@/types';
import { request } from '@/utils';


const fetcher = (path: string, title: string) => {
  const token = localStorage.getItem('simplepasswords_token');

  return request
    .get(`${path}${title ? '?search=' + encodeURIComponent(title) : ''}`)
    .set({ 'Authorization': `Token ${token}` })
    .then(res => {
      const entries: IListEntry[] = [];
      for (const entry of res.body) entries.push(checkListEntry(entry, res));
      return entries;
    });
}

export default function DashboardRetrieveEntries() {
  const {
    searchBarOn,
    searchTitle,
  } = useAppSelector((state) => state.dashboard);
  const dispatch = useAppDispatch();

  const debouncedSearchTitle = useDebounce(searchTitle, 250);

  const {
    data,
    error,
    isValidating,
  } = useSWR(['/entries/', searchBarOn ? debouncedSearchTitle : ''], fetcher);

  useEffect(() => {
    if (isValidating) {
      dispatch({ type: 'START_RETRIEVE_ENTRIES' });
    } else {
      dispatch({ type: 'STOP_RETRIEVE_ENTRIES' });
    }

    if (error) {
      dispatch({ type: 'DASHBOARD_SET_ENTRIES', data: [], error });
    } else if (data) {
      dispatch({ type: 'DASHBOARD_SET_ENTRIES', data });
    }
  }, [data, error, isValidating, dispatch]);

  return <></>;
}