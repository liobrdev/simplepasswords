import { FormEvent, useState } from 'react';

import { mutate } from 'swr';

import { useAppDispatch, useAppSelector } from '@/hooks';
import { checkToken, checkUser, IUser } from '@/types';
import { parseErrorResponse, request } from '@/utils';

import { Input } from './';


const initialError: ReturnType<typeof parseErrorResponse> = {};

export default function LoginForm() {
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [tfaForm, setTfaForm] = useState({
    email: '',
    security_code: '',
    tfa_token: '',
  });

  const [loginError, setLoginError] = useState({ ...initialError });
  const [tfaError, setTfaError] = useState({ ...initialError });

  const dispatch = useAppDispatch();

  const handleInputLogin = () => (e: FormEvent<HTMLInputElement>) => {
    const name = (e.target as HTMLInputElement).name;
    const value = (e.target as HTMLInputElement).value;
    setLoginForm((prevState) => ({ ...prevState, [name]: value }));
  };

  const handleInputTfa = () => (e: FormEvent<HTMLInputElement>) => {
    const name = (e.target as HTMLInputElement).name;
    const value = (e.target as HTMLInputElement).value;
    setTfaForm((prevState) => ({ ...prevState, [name]: value }));
  };

  const handleSubmitLogin = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch({ type: 'START_LOGIN_USER' });
    setLoginError({});

    try {
      const res = await request.post('/auth/login/').send({ ...loginForm });

      if (res.status === 201) {
        const tfa_token: string = checkToken(res.body?.tfa_token, res);
        setTfaForm({ email: loginForm.email, security_code: '', tfa_token });
        setLoginForm({ email: '', password: '' });
      } else if (res.status === 200) {
        const token: string = checkToken(res.body?.token, res);
        const data: IUser = checkUser(res.body?.user, res);
        localStorage.setItem('simplepasswords_token', token);
        dispatch({ type: 'SUCCESS_LOGIN_USER', data });
        setLoginForm({ email: '', password: '' });
        setTfaForm({ email: '', security_code: '', tfa_token: '' });
        mutate('/users/');
      }
    } catch (err: any) {
      localStorage.removeItem('simplepasswords_token');
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);
      setLoginError(
        parseErrorResponse(err?.response?.body, Object.keys(loginForm)));
    } finally {
      dispatch({ type: 'STOP_LOGIN_USER' });
    }
  };

  const handleSubmitTfa = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch({ type: 'START_LOGIN_USER' });
    setTfaError({});

    try {
      const { token, data } = await request
        .post('/auth/two_factor_auth/')
        .send({ ...tfaForm })
        .then((res) => {
          const token: string = checkToken(res.body?.token, res);
          const data: IUser = checkUser(res.body?.user, res);
          return { token, data };
        });
      localStorage.setItem('simplepasswords_token', token);
      dispatch({ type: 'SUCCESS_LOGIN_USER', data });
      setLoginForm({ email: '', password: '' });
      setTfaForm({ email: '', security_code: '', tfa_token: '' });
      mutate('/users/');
    } catch (err: any) {
      localStorage.removeItem('simplepasswords_token');
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);
      setTfaError(
        parseErrorResponse(err?.response?.body, Object.keys(tfaForm)));
    } finally {
      dispatch({ type: 'STOP_LOGIN_USER' });
    }
  };

  const {
    isLoggingIn,
    isLoggingOut,
    isRegistering,
  } = useAppSelector((state) => state.user);

  const canSubmitLogin = !!(
    !isLoggingIn &&
    !isLoggingOut &&
    !isRegistering &&
    loginForm.email && loginForm.password
  );

  const canSubmitTfa = !!(
    !isLoggingIn &&
    !isLoggingOut &&
    !isRegistering &&
    tfaForm.email && tfaForm.security_code && tfaForm.tfa_token
  );

  const formLogin = (
    <>
      <h2>Log in</h2>
      <form
        className='LoginForm'
        id='formLogin'
        onSubmit={canSubmitLogin ? handleSubmitLogin : undefined}
      >
        <Input
          className='LoginForm-input'
          label='Email'
          name='email'
          value={loginForm.email}
          type='text'
          disabled={isLoggingIn}
          minLength={1}
          maxLength={50}
          onChange={handleInputLogin()}
          required
          autoFocus
        />
        {loginError?.email?.map(
          e => <p key={e.id} className='LoginForm-error'>{e.msg}</p>
        )}
        <Input
          className='LoginForm-input'
          label='Password'
          name='password'
          type='password'
          disabled={isLoggingIn}
          onChange={handleInputLogin()}
          required
        />
        {loginError?.password?.map(
          e => <p key={e.id} className='LoginForm-error'>{e.msg}</p>
        )}
        {loginError?.nonField?.map(
          e => <p key={e.id} className='LoginForm-error'>{e.msg}</p>
        )}
        {loginError?.detail?.map(
          e => <p key={e.id} className='LoginForm-error'>{e.msg}</p>
        )}
        <button
          className='LoginForm-button'
          type='submit'
          disabled={!canSubmitLogin}
        >
          {isLoggingIn ? 'Logging in...' : 'Log in'}
        </button>
      </form>
    </>
  );

  const formTfa = (
    <>
      <h2>Enter the security code sent to your phone</h2>
      <form
        className='LoginForm'
        id='formTfa'
        onSubmit={canSubmitTfa ? handleSubmitTfa : undefined}
      >
        <Input
          className='LoginForm-input'
          name='security_code'
          value={tfaForm.security_code}
          type='password'
          disabled={isLoggingIn}
          maxLength={50}
          onChange={handleInputTfa()}
          required
          autoFocus
        />
        {tfaError?.security_code?.map(
          e => <p key={e.id} className='LoginForm-error'>{e.msg}</p>
        )}
        {tfaError?.nonField?.map(
          e => <p key={e.id} className='LoginForm-error'>{e.msg}</p>
        )}
        {tfaError?.detail?.map(
          e => <p key={e.id} className='LoginForm-error'>{e.msg}</p>
        )}
        <button
          className='LoginForm-button'
          type='submit'
          disabled={!canSubmitTfa}
        >
          {isLoggingIn ? 'Submitting...' : 'Submit'}
        </button>
      </form>
    </>
  );

  return tfaForm.tfa_token ? formTfa : formLogin;
}