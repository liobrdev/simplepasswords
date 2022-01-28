import { useEffect } from 'react';
import useSWR from 'swr';

import { useAppDispatch } from '@/hooks';

import { checkListEntry, IListEntry } from '@/types';
import { request } from '@/utils';


const fetcher = (url: string) => {
  const token = localStorage.getItem('simplepasswords_token');

  return request
    .get(url)
    .set({ 'Authorization': `Token ${token}` })
    .then(res => {
      const entries: IListEntry[] = [];
      for (const entry of res.body) entries.push(checkListEntry(entry, res));
      return entries;
    });
}

export default function DashboardRetrieveEntries() {
  const { data, error, isValidating } = useSWR('/entries/', fetcher);
  const dispatch = useAppDispatch();

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