import { FormEvent, useState } from 'react';

import { useAppDispatch, useAppSelector } from '@/hooks';
import { checkEntry, IEntry } from '@/types';
import { parseErrorResponse, request } from '@/utils';

import { Input } from './';


interface Props {
  slug: string;
}

const initialError: ReturnType<typeof parseErrorResponse> = {};

export default function EntryFormRetrieve({ slug }: Props) {
  const [form, setForm] = useState({ password: '' });
  const [error, setError] = useState({ ...initialError });

  const { isRetrieving } = useAppSelector((state) => state.entry);
  const dispatch = useAppDispatch();
  
  const handleInput = () => (e: FormEvent<HTMLInputElement>) => {
    const password = (e.target as HTMLInputElement).value;
    setForm({ password });
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch({ type: 'START_RETRIEVE_ENTRY' });
    setError({});

    try {
      const token = localStorage.getItem('simplepasswords_token');
      const entry = await request
        .post(`/entry_retrieve/${slug}/`)
        .set({ 'Authorization': `Token ${token}` })
        .send({ ...form })
        .then((res) => checkEntry(res.body, res));
      dispatch({ type: 'SUCCESS_RETRIEVE_ENTRY', entry });
    } catch (err: any) {
      dispatch({ type: 'STOP_RETRIEVE_ENTRY' });
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);
      setError(parseErrorResponse(err?.response?.body, Object.keys(form)));
    }
  };

  const canSubmit = !isRetrieving && !!form.password;

  return (
    <>
      <h2>Enter your master password to view this entry</h2>
      <form
        className='EntryFormRetrieve'
        id='formRetrieveEntry'
        onSubmit={canSubmit ? handleSubmit : undefined}
      >
        <Input
          className='EntryFormRetrieve-input'
          name='password'
          type='password'
          disabled={isRetrieving}
          onChange={handleInput()}
          required
          autoFocus
          showAsterisk
        />
        {error?.password?.map(
          e => <p key={e.id} className='EntryFormRetrieve-error'>{e.msg}</p>
        )}
        {error?.nonField?.map(
          e => <p key={e.id} className='EntryFormRetrieve-error'>{e.msg}</p>
        )}
        {error?.detail?.map(
          e => <p key={e.id} className='EntryFormRetrieve-error'>{e.msg}</p>
        )}
        <button
          className='EntryFormRetrieve-button'
          type='submit'
          disabled={!canSubmit}
        >
          {isRetrieving ? 'Retrieving...' : 'View'}
        </button>
      </form>
    </>
  );
}