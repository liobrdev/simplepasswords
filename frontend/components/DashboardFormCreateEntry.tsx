import { FormEvent, MouseEvent, useRef, useState } from 'react';

import { enableBodyScroll, disableBodyScroll } from 'body-scroll-lock';
import generator from 'generate-password';

import { useAppDispatch, useAppSelector } from '@/hooks';
import { checkListEntry, IModal } from '@/types';
import { parseErrorResponse, request } from '@/utils';

import { CloseIcon, Input, PlusIcon, SliderCheckbox, TextArea } from './';


const initialForm = { title: '', value: '', password: '' };
const initialError: ReturnType<typeof parseErrorResponse> = {};

export default function DashboardFormCreateEntry() {
  const {
    formOnCreateEntry,
    isCreating,
    isRetrieving,
  } = useAppSelector((state) => state.dashboard);
  const dispatch = useAppDispatch();

  const [form, setForm] = useState({ ...initialForm });
  const [generatorOn, setGeneratorOn] = useState(false);
  const [generatorLength, setGeneratorLength] = useState(16);
  const [errorCreate, setError] = useState({ ...initialError });

  const thisComponent = useRef<HTMLDivElement>(null);

  const handleShow = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (thisComponent.current) disableBodyScroll(thisComponent.current);
    dispatch({ type: 'DASHBOARD_FORM_SHOW' });
  };

  const handleClose = (e: MouseEvent<HTMLButtonElement | HTMLDivElement>) => {
    e.preventDefault();
    if (thisComponent.current) enableBodyScroll(thisComponent.current);
    setForm({ ...initialForm });
    setError({ ...initialError });
    dispatch({ type: 'DASHBOARD_FORM_CLOSE' });
  };

  const handleInput = () => (e: FormEvent<HTMLInputElement>) => {
    e.preventDefault();
    const name: string = (e.target as HTMLInputElement).name;
    const value: string = (e.target as HTMLInputElement).value;
    setForm((prevState) => ({ ...prevState, [name]: value }));
  };

  const handleToggleGenerator = () => (e: FormEvent<HTMLInputElement>) => {
    const checked = (e.target as HTMLInputElement).checked;
    if (checked) setGeneratorOn(true);
    else setGeneratorOn(false);
  };

  const handleGeneratorLength = () => (e: FormEvent<HTMLInputElement>) => {
    e.preventDefault();
    const value: number = +(e.target as HTMLInputElement).value;
    setGeneratorLength(value);
  };

  const handleGeneratePassword = () => (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (generatorLength < 8) {
      setGeneratorLength(8);
    } else {
      const value = generator.generate({
        length: generatorLength,
        numbers: true,
        symbols: true,
        strict: true,
      });
      setForm((prevState) => ({ ...prevState, value }));
    }
  };

  const handleTextArea = () => (e: FormEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
    const name: string = (e.target as HTMLTextAreaElement).name;
    const value: string = (e.target as HTMLTextAreaElement).value;
    setForm((prevState) => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch({ type: 'START_CREATE_ENTRY' });
    setError({});

    try {
      const token = localStorage.getItem('simplepasswords_token');
      const entry = await request
        .post('/entries/')
        .set({ 'Authorization': `Token ${token}` })
        .send({ ...form })
        .then((res) => checkListEntry(res.body, res));
      setForm({ ...initialForm });
      if (thisComponent.current) enableBodyScroll(thisComponent.current);
      dispatch({ type: 'SUCCESS_CREATE_ENTRY', entry });
      const dashboardModal: IModal = {
        message: 'New entry added successfully!',
        page: 'dashboard',
      };
      dispatch({ type: 'DASHBOARD_MODAL_SHOW', dashboardModal });
      window.scrollTo(0, 0);
    } catch (err: any) {
      dispatch({ type: 'STOP_CREATE_ENTRY' });
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);
      const res = err?.response;

      if (res?.unauthorized || res?.forbidden) {
        localStorage.removeItem('simplepasswords_token');
        if (thisComponent.current) enableBodyScroll(thisComponent.current);
        dispatch({ type: 'START_LOGOUT_USER' });
      }

      setError(parseErrorResponse(res?.body, Object.keys(form)));
    }
  };

  const canSubmit = (
    formOnCreateEntry &&
    !!form.title && !!form.value && !!form.password &&
    !isCreating && !isRetrieving
  );

  const rootClass = 'DashboardFormCreateEntry';

  const formCreateEntry = (
    <form
      className={rootClass + '-form'}
      onSubmit={canSubmit ? handleSubmit : undefined}
    >
      <div className='CloseIcon-container'>
        <CloseIcon
          onClick={handleClose}
          disabled={isCreating}
          type='button'  
        />
      </div>
      <div className={rootClass + '-form-titleContainer'}>
        <Input
          className={rootClass + '-form-input'}
          label='New entry title'
          type='text'
          name='title'
          value={form.title}
          minLength={1}
          maxLength={255}
          disabled={isCreating}
          onChange={handleInput()}
          autoFocus
          required
          showAsterisk
        />
        {errorCreate?.title?.map(e => (
          <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
        ))}
        <SliderCheckbox
          className={`${rootClass}-form-checkbox`}
          label='Generate password?'
          type='checkbox'
          name='generatorOn'
          checked={generatorOn}
          disabled={isCreating}
          onChange={handleToggleGenerator()}
        />
        <Input
          className={`${rootClass}-form-generatorLength`}
          label='Password length'
          type='number'
          name='generatorLength'
          min={8}
          max={256}
          value={generatorLength}
          onChange={handleGeneratorLength()}
          disabled={!generatorOn || isCreating}
        />
        <button
          className={`${rootClass}-form-button ${rootClass}-form-button--generator`}
          type='button'
          disabled={!generatorOn || isCreating}
          onClick={handleGeneratePassword()}
        >
          Generate
        </button>
      </div>
      <div className={rootClass + '-form-passwordContainer'}>
        <TextArea
          className={rootClass + '-form-textArea'}
          label='Value'
          name='value'
          value={form.value}
          minLength={1}
          disabled={isCreating}
          onChange={handleTextArea()}
          required
          showAsterisk
        />
        {errorCreate?.value?.map(e => (
          <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
        ))}
        <Input
          className={rootClass + '-form-input'}
          type='password'
          label='Enter master password'
          name='password'
          value={form.password}
          disabled={isCreating}
          minLength={1}
          onChange={handleInput()}
          required
          showAsterisk
        />
        {errorCreate?.password?.map(e =>
          <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
        )}
        <button
          className={`${rootClass}-form-button ${rootClass}-form-button--saveShort`}
          type='submit'
          disabled={!canSubmit}
        >
          {isCreating ? 'Creating entry...' : 'Create'}
        </button>
      </div>
      {errorCreate?.nonField?.map(e => (
        <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
      ))}
      {errorCreate?.detail?.map(e => (
        <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
      ))}
      <button
        className={`${rootClass}-form-button ${rootClass}-form-button--saveTall`}
        type='submit'
        disabled={!canSubmit}
      >
        {isCreating ? 'Creating entry...' : 'Create'}
      </button>
    </form>
  );

  return (
    <>
      <div
        className={`${rootClass}${formOnCreateEntry ? ' is-on' : ''}`}
        ref={thisComponent}
      >
        {formOnCreateEntry && (
          <>
            <div className={rootClass + '-overlay'} onClick={handleClose} />
            {formCreateEntry}
          </>
        )}
        {!formOnCreateEntry && <PlusIcon onClick={handleShow} type='button' />}
      </div>
    </>
  );
}