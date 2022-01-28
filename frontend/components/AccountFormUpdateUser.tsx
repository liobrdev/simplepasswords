import { FormEvent, MouseEvent } from 'react';

import { useState } from 'react';
import { mutate } from 'swr';

import { useAppDispatch, useAppSelector } from '@/hooks';
import { checkUser, IModal, IUser, IUserForm } from '@/types';
import { parseErrorResponse, request } from '@/utils';

import { Input, SliderCheckbox } from './';

import 'react-phone-number-input/style.css';
import PhoneInput from 'react-phone-number-input';


interface Props {
  user: IUser;
}

export default function AccountFormUpdateUser({ user }: Props) {
  const {
    isLoggingIn,
    isLoggingOut,
    isRegistering,
    isUpdating,
  } = useAppSelector((state) => state.user);
  const { formOnDeleteUser } = useAppSelector((state) => state.account);
  const dispatch = useAppDispatch();
  
  const initialForm: IUserForm = {
    name: user.name,
    email: user.email,
    phone_number: undefined,
    tfa_is_enabled: user.tfa_is_enabled,
    password: '',
    password_2: '',
    current_password: '',
  };

  const initialError: ReturnType<typeof parseErrorResponse> = {};
  
  const [form, setForm] = useState({ ...initialForm });
  const [phoneInputOn, showPhoneInput] = useState(false);
  const [willRemovePhoneNumber, setWillRemovePhoneNumber] = useState(false);
  const [error, setError] = useState({ ...initialError });
  
  const handleInput = () => (e: FormEvent<HTMLInputElement>) => {
    e.preventDefault();
    const name: string = (e.target as HTMLInputElement).name;
    const value: string = (e.target as HTMLInputElement).value;
    setForm((prevState) => ({ ...prevState, [name]: value }));
  };

  const handleTwoFactorAuth = () => (e: FormEvent<HTMLInputElement>) => {
    const checked = (e.target as HTMLInputElement).checked;
    if (checked) setForm({ ...form, tfa_is_enabled: true });
    else setForm({ ...form, tfa_is_enabled: false });
  };
  
  const handlePhoneNumber = () => (value?: string) => {
    setForm((prevState) => ({ ...prevState, phone_number: value }));
  };

  const handleRemovePhoneNumber = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setForm((prevState) => ({ ...prevState, phone_number: '' }));
    setWillRemovePhoneNumber(true);
  };

  const handleUndoRemovePhoneNumber = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setForm((prevState) => ({ ...prevState, phone_number: undefined }));
    setWillRemovePhoneNumber(false);
  };

  const handleShowPhoneInput = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    showPhoneInput(true);
  };

  const handleClosePhoneInput = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setForm((prevState) => ({ ...prevState, phone_number: undefined }));
    showPhoneInput(false);
  };

  const handleReset = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setForm({ ...initialForm });
    showPhoneInput(false);
    setWillRemovePhoneNumber(false);
    setError({});
    window.scrollTo(0, 0);
    (document.activeElement as HTMLElement).blur();
  };

  const handleVerifyEmail = async (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    dispatch({ type: 'START_UPDATE_USER' });
    setError({});

    try {
      const token = localStorage.getItem('simplepasswords_token');
      await request
        .get('/auth/verify_email/')
        .set({ 'Authorization': `Token ${token}` })
        .then((res) => {
          if (res.noContent) {
            const accountModal: IModal = {
              message: 'Please check your email to complete verification.',
              page: 'account',
            };
            dispatch({ type: 'ACCOUNT_MODAL_SHOW' , accountModal });
          }
        });
    } catch (err: any) {
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);

      if (err?.response?.unauthorized || err?.response?.forbidden) {
        localStorage.removeItem('simplepasswords_token');
        dispatch({ type: 'START_LOGOUT_USER' });
      }

      setError(parseErrorResponse(err?.response?.body, Object.keys(form)));
    } finally {
      dispatch({ type: 'STOP_UPDATE_USER' });
    }
  };

  const handleVerifyPhone = async (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    dispatch({ type: 'START_UPDATE_USER' });
    setError({});

    try {
      const token = localStorage.getItem('simplepasswords_token');
      await request
        .get('/auth/verify_phone/')
        .set({ 'Authorization': `Token ${token}` })
        .then((res) => {
          if (res.noContent) dispatch({ type: 'ACCOUNT_FORM_VERIFY_SHOW' });
        });
    } catch (err: any) {
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);

      if (err?.response?.unauthorized || err?.response?.forbidden) {
        localStorage.removeItem('simplepasswords_token');
        dispatch({ type: 'START_LOGOUT_USER' });
      }

      setError(parseErrorResponse(err?.response?.body, Object.keys(form)));
    } finally {
      dispatch({ type: 'STOP_UPDATE_USER' });
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch({ type: 'START_UPDATE_USER' });
    setError({});

    try {
      const token = localStorage.getItem('simplepasswords_token');
      const data = await request
        .patch(`/users/${user.user_slug}/`)
        .set({ 'Authorization': `Token ${token}` })
        .send({ ...form })
        .then((res) => checkUser(res.body, res));
      dispatch({ type: 'SUCCESS_UPDATE_USER', data });
      mutate('/users/');
      const { name, email, tfa_is_enabled } = data;
      setForm({ ...initialForm, name, email, tfa_is_enabled });
      showPhoneInput(false);
      setWillRemovePhoneNumber(false);
      window.scrollTo(0, 0);
      const accountModal: IModal = {
        message: 'Update successful!',
        page: 'account',
      };
      dispatch({ type: 'ACCOUNT_MODAL_SHOW' , accountModal });
    } catch (err: any) {
      dispatch({ type: 'STOP_UPDATE_USER' });
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);

      if (err?.response?.unauthorized || err?.response?.forbidden) {
        localStorage.removeItem('simplepasswords_token');
        dispatch({ type: 'START_LOGOUT_USER' });
      }

      setError(parseErrorResponse(err?.response?.body, Object.keys(form)));
    } finally {
      (document.activeElement as HTMLElement).blur();
    }
  };

  const canSubmit = !!(
    !formOnDeleteUser &&
    !isLoggingIn &&
    !isLoggingOut &&
    !isRegistering &&
    !isUpdating &&
    form.name &&
    form.email &&
    form.current_password
  );

  const hasPhoneNumber = !!user.truncated_phone_number;
  const emailIsVerified = !!user.email_is_verified;
  const phoneIsVerified = !!user.phone_number_is_verified;

  const emailVerification = (
    <>
      <span
        className={
          'AccountFormUpdateUser-verified ' +
          'AccountFormUpdateUser-verified--email'
        }
      >
        {(emailIsVerified && form.email === user.email) && '(verified)'}
        {(!emailIsVerified || form.email !== user.email) && '(not verified)'}
      </span>
      {!emailIsVerified && form.email === user.email && (
        <>
          <br/>
          <button
            className={
              'AccountFormUpdateUser-verify ' +
              'AccountFormUpdateUser-verify--email'
            }
            type='button'
            disabled={isUpdating}
            onClick={handleVerifyEmail}
          >
            {isUpdating ? 'Sending...' : 'Verify email address'}
          </button>
        </>
      )}
    </>
  );

  const phoneVerification = (
    <span
      className={
        'AccountFormUpdateUser-verified ' +
        'AccountFormUpdateUser-verified--phone'
      }
    >
      {!phoneInputOn && hasPhoneNumber && phoneIsVerified && '(verified)'}
      {!phoneInputOn && hasPhoneNumber && !phoneIsVerified && '(not verified)'}
    </span>
  );

  return (
    <form
      className='AccountFormUpdateUser'
      id='formUpdateUser'
      onSubmit={canSubmit ? handleSubmit : undefined}
    >
      <Input
        className='AccountFormUpdateUser-input'
        label='Name'
        type='text'
        name='name'
        value={form.name}
        disabled={isUpdating || formOnDeleteUser}
        minLength={1}
        maxLength={50}
        onChange={handleInput()}
        required
        showAsterisk
      />
      {error?.name?.map(
        e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      <br/>
      <Input
        className='AccountFormUpdateUser-input'
        label={<>Email address{emailVerification}</>}
        type='email'
        name='email'
        value={form.email}
        disabled={isUpdating || formOnDeleteUser}
        minLength={1}
        maxLength={50}
        onChange={handleInput()}
        required
        showAsterisk
        showObelisk
      />
      {error?.email?.map(
        e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      <br/>
      <div className='AccountFormUpdateUser-phoneNumber'>
        {!willRemovePhoneNumber && (
          <>
            <span className='AccountFormUpdateUser-phoneNumber-label'>
              Phone number
              <span className='AccountFormUpdateUser-phoneNumber-label-obelisk'>
                &dagger;
              </span>
              {phoneVerification}
            </span>
            {!phoneInputOn && (
              <>
                {hasPhoneNumber ? (
                  <span className='AccountFormUpdateUser-phoneNumber-truncated'>
                    {user.truncated_phone_number}
                  </span>
                ) : <br/>}
                <button
                  className='AccountFormUpdateUser-phoneNumber-button'
                  type='button'
                  disabled={isUpdating || formOnDeleteUser}
                  onClick={handleShowPhoneInput}
                >
                  {hasPhoneNumber ? 'Edit' : 'Add phone number'}
                </button>
                {hasPhoneNumber && (
                  <button
                    className={
                      'AccountFormUpdateUser-phoneNumber-button ' +
                      'AccountFormUpdateUser-phoneNumber-button--remove'
                    }
                    type='button'
                    disabled={isUpdating || formOnDeleteUser}
                    onClick={handleRemovePhoneNumber}
                  >
                    Remove
                  </button>
                )}
                {hasPhoneNumber && !phoneIsVerified && (
                  <button
                    className={
                      'AccountFormUpdateUser-phoneNumber-button ' +
                      'AccountFormUpdateUser-phoneNumber-button--verify'
                    }
                    type='button'
                    disabled={isUpdating}
                    onClick={handleVerifyPhone}
                  >
                    {isUpdating ? 'Sending...' : (
                      <>Verify phone number<span>&nbsp;&Dagger;</span></>
                    )}
                  </button>
                )}
              </>
            )}
            {phoneInputOn && (
              <>

                <button
                  className={
                    'AccountFormUpdateUser-phoneNumber-button ' +
                    'AccountFormUpdateUser-phoneNumber-button--close'
                  }
                  type='button'
                  disabled={isUpdating || formOnDeleteUser}
                  onClick={handleClosePhoneInput}
                >
                  Undo
                </button>
                <PhoneInput
                  placeholder='Enter phone number'
                  defaultCountry='US'
                  value={form.phone_number}
                  onChange={handlePhoneNumber()}
                />
                {error?.phone_number?.map(
                  e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
                )}
              </>
            )}
          </>
        )}
        {willRemovePhoneNumber && (
          <>
            <span className='AccountFormUpdateUser-phoneNumber-label '>
              Phone number will be removed upon saving changes.
            </span>
            &nbsp;&nbsp;
            <button
              className='AccountFormUpdateUser-phoneNumber-button'
              type='button'
              disabled={isUpdating || formOnDeleteUser}
              onClick={handleUndoRemovePhoneNumber}
            >
              Undo
            </button>
          </>
        )}
      </div>
      <br/>
      <SliderCheckbox
        className='AccountFormUpdateUser-form-checkbox'
        label={(
          <>
            Enable two-factor authentication?
            <span>&dagger;</span><span>&Dagger;</span>
          </>
        )}
        type='checkbox'
        name='tfa_is_enabled'
        checked={form.tfa_is_enabled}
        disabled={
          isUpdating
          || !emailIsVerified || !phoneIsVerified
          || willRemovePhoneNumber
        }
        onChange={handleTwoFactorAuth()}
        title={`Click to ${form.tfa_is_enabled ? 'disable' : 'enable'}`}
      />
      {error.tfa_is_enabled?.map(e =>
        <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      <br/>
      <Input
        className='AccountFormUpdateUser-input'
        label='Set new master password'
        type='password'
        name='password'
        value={form.password}
        disabled={isUpdating || formOnDeleteUser}
        onChange={handleInput()}
      />
      {error?.password?.map(
        e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      <br/>
      <Input
        className='AccountFormUpdateUser-input'
        type='password'
        label='Enter new master password again'
        name='password_2'
        value={form.password_2}
        disabled={
          isUpdating ||
          (!form.password && !form.password_2) ||
          formOnDeleteUser
        }
        onChange={handleInput()}
        required={!!form.password}
        showAsterisk={!!form.password}
      />
      {error?.password_2?.map(
        e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      <br/>
      <Input
        className='AccountFormUpdateUser-input'
        type='password'
        label='Current master password'
        name='current_password'
        value={form.current_password}
        disabled={isUpdating || formOnDeleteUser}
        onChange={handleInput()}
        required
        showAsterisk
      />
      {error?.current_password?.map(
        e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      <br/>
      {error?.nonField?.map(
        e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      {error?.detail?.map(
        e => <p key={e.id} className='AccountFormUpdateUser-error'>{e.msg}</p>
      )}
      <br/>
      <p className='AccountFormUpdateUser-text AccountFormUpdateUser-text--asterisk'>
        <span>*</span>&nbsp;Required
      </p>
      <p className='AccountFormUpdateUser-text AccountFormUpdateUser-text--obelisk'>
        <span>&dagger;&nbsp;</span>
        Email address and phone number must be verified in order to enable
        &nbsp;<b>two-factor authentication</b>.
        This is optional, but strongly-recommended for the security
        of your account. If either email address or phone number is changed,
        it will need to be verified again.
      </p>
      <p className='AccountFormUpdateUser-text AccountFormUpdateUser-text--diesis'>
        <span>&Dagger;&nbsp;</span>
        Message and data rates may apply.
      </p>
      <br/>
      <button
        className={
          'AccountFormUpdateUser-button AccountFormUpdateUser-button--undo'
        }
        type='button'
        disabled={isUpdating || formOnDeleteUser}
        onClick={handleReset}
      >
        Undo changes
      </button>
      <button
        className='AccountFormUpdateUser-button'
        type='submit'
        disabled={isUpdating || formOnDeleteUser}
      >
        {isUpdating ? 'Saving changes...' : 'Save changes'}
      </button>
    </form>
  );
}