import { Component, FormEvent, MouseEvent, createRef, RefObject } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import { mutate } from 'swr';
import { enableBodyScroll, disableBodyScroll } from 'body-scroll-lock';

import { AppDispatch, AppState, IModal } from '@/types';
import { parseErrorResponse, request } from '@/utils';

import { Input, CloseIcon } from './';


class AccountFormVerifyPhone extends Component<Props, State> {
  private component: RefObject<HTMLDivElement>;

  constructor(props: Props) {
    super(props);
    this.component = createRef();
    this.state = {
      form: { token: '' },
      error: {},
    };
    this.handleClose = this.handleClose.bind(this);
    this.handleInput = this.handleInput.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleClose(e: MouseEvent<HTMLButtonElement | HTMLDivElement>) {
    e.preventDefault();
    this.props.accountFormVerifyClose();
  }

  handleInput(e: FormEvent<HTMLInputElement>) {
    e.preventDefault();
    const token = (e.target as HTMLInputElement).value;
    this.setState({ form: { token } });
  };

  async handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    this.props.startUpdateUser();
    this.setState({ error: {} });
    const { form } = this.state;

    try {
      const token = localStorage.getItem('simplepasswords_token');
      await request
        .post('/auth/verify_phone/')
        .set({ 'Authorization': `Token ${token}` })
        .send({ ...form })
        .then((res) => {
          if (res.noContent) {
            const accountModal: IModal = {
              message: 'Phone number verified successfully!',
              page: 'account',
            };
            this.props.accountModalShow(accountModal);
            this.props.accountFormVerifyClose();
          }
        });
    } catch (err: any) {
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);

      if (err?.response?.forbidden) {
        const accountModal: IModal = {
          message: err?.response?.body?.detail || 'Oops, verification failed!',
          page: 'account',
        };
        this.props.accountModalShow(accountModal);        
      }

    } finally {
      this.props.stopUpdateUser();
      mutate('/users/');
    }
  };

  componentDidMount() {
    if (this.component.current) disableBodyScroll(this.component.current);
  }

  componentWillUnmount() {
    if (this.component.current) enableBodyScroll(this.component.current);
  }

  render() {
    const { isUpdating, user } = this.props;
    const { form, error } = this.state;

    const canSubmit = !isUpdating && !!form.token;

    const formVerifyPhone = (
      <form
        className='AccountFormVerifyPhone-form'
        id='formVerifyPhone'
        onSubmit={canSubmit ? this.handleSubmit : undefined}
      >
        <div className='CloseIcon-container'>
          <CloseIcon
            type='button'
            onClick={this.handleClose}
            disabled={isUpdating}
          />
        </div>
        <div className='AccountFormVerifyPhone-form-text'>
          Enter the security code sent to {user?.truncated_phone_number}
        </div>
        <Input
          className='AccountFormVerifyPhone-form-input'
          type='password'
          name='token'
          value={form.token}
          disabled={isUpdating}
          onChange={this.handleInput}
          maxLength={50}
          required
        />
        {error?.token?.map(
          e => <p key={e.id} className='AccountFormVerifyPhone-form-error'>{e.msg}</p>
        )}
        {error?.nonField?.map(
          e => <p key={e.id} className='AccountFormVerifyPhone-form-error'>{e.msg}</p>
        )}
        {error?.detail?.map(
          e => <p key={e.id} className='AccountFormVerifyPhone-form-error'>{e.msg}</p>
        )}
        <button
          className='AccountFormVerifyPhone-form-button'
          type='submit'
          disabled={!canSubmit}
        >
          {isUpdating ? 'Verifying...' : 'Submit'}
        </button>
      </form>
    );

    return (
      <div className='AccountFormVerifyPhone' ref={this.component}>
        <div
          className='AccountFormVerifyPhone-overlay'
          onClick={this.handleClose}
        />
        {formVerifyPhone}
      </div>
    );
  }
}

const mapStateToProps = (state: AppState) => ({
  isUpdating: state.user.isUpdating,
  user: state.user.user,
});

const mapDispatchToProps = (dispatch: AppDispatch) => ({
  accountFormVerifyClose: () => {
    dispatch({ type: 'ACCOUNT_FORM_VERIFY_CLOSE' });
  },
  accountModalShow: (accountModal: IModal) => {
    dispatch({ type: 'ACCOUNT_MODAL_SHOW', accountModal });
  },
  startUpdateUser: () => {
    dispatch({ type: 'START_UPDATE_USER' });
  },
  stopUpdateUser: () => {
    dispatch({ type: 'STOP_UPDATE_USER' });
  },
});

const connector = connect(mapStateToProps, mapDispatchToProps);

type Props = ConnectedProps<typeof connector>;

interface IForm {
  token: string;
}

interface State {
  form: IForm;
  error: ReturnType<typeof parseErrorResponse>;
}

export default connector(AccountFormVerifyPhone);