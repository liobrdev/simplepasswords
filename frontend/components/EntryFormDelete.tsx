import { Component, FormEvent, MouseEvent, createRef, RefObject } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import { enableBodyScroll, disableBodyScroll } from 'body-scroll-lock';
import { withRouter, NextRouter } from 'next/router';

import { AppDispatch, AppState, IEntry } from '@/types';
import { parseErrorResponse, request } from '@/utils';

import { Input, CloseIcon } from './';


class EntryFormDelete extends Component<Props, State> {
  private component: RefObject<HTMLDivElement>;

  constructor(props: Props) {
    super(props);
    this.component = createRef();
    this.state = {
      form: { password: '' },
      error: {},
    };
    this.handleClose = this.handleClose.bind(this);
    this.handleInput = this.handleInput.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleClose(e: MouseEvent<HTMLButtonElement | HTMLDivElement>) {
    e.preventDefault();
    this.props.entryFormDeleteClose();
  }

  handleInput(e: FormEvent<HTMLInputElement>) {
    e.preventDefault();
    const name = (e.target as HTMLInputElement).name;
    
    if (name !== 'password__deleteEntry') return;

    const password = (e.target as HTMLInputElement).value;
    this.setState({ form: { password } });
  };

  async handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    this.props.startDeleteEntry();
    this.setState({ error: {} });
    const { form } = this.state;

    try {
      const token = localStorage.getItem('simplepasswords_token');
      await request
        .post(`/entry_destroy/${this.props.entry.slug}/`)
        .set({ 'Authorization': `Token ${token}` })
        .send({ ...form });
      this.setState({ form: { password: '' } });
      this.props.successDeleteEntry();
      this.props.router.push('/dashboard');
    } catch (err: any) {
      this.props.stopDeleteEntry();
      // Possibly report to api in the future, for now just console.error
      // reportErrorToAPI(err);
      console.error(err);
      err = err?.response;

      if (err?.unauthorized || err?.forbidden || err?.notFound) {
        localStorage.removeItem('simplepasswords_token');
        this.props.startLogoutUser();
      }
      const error = parseErrorResponse(err?.body, Object.keys(form));
      this.setState({ error });
    } finally {
      (document.activeElement as HTMLElement).blur();
    }
  };

  componentDidMount() {
    if (this.component.current) disableBodyScroll(this.component.current);
  }

  componentWillUnmount() {
    if (this.component.current) enableBodyScroll(this.component.current);
  }

  render() {
    const { isDeleting, isUpdating } = this.props;
    const { form, error } = this.state;

    const canSubmit = !isUpdating && !isDeleting && !!form.password;

    const formDeleteEntry = (
      <form
        className='EntryFormDelete-form'
        id='formDeleteEntry'
        onSubmit={canSubmit ? this.handleSubmit : undefined}
      >
        <div className='CloseIcon-container'>
          <CloseIcon
            type='button'
            onClick={this.handleClose}
            disabled={isDeleting}
          />
        </div>
        <div className='EntryFormDelete-form-text'>
          To delete this entry, please re-enter your master
          password. <b>This action cannot be undone.</b> Before proceeding,
          please make sure that this password is no longer being used
          by any other service, and/or that you have saved a copy
          of it in a different location.
        </div>
        <Input
          className='EntryFormDelete-form-input'
          label='Master password'
          type='password'
          name='password__deleteEntry'
          value={form.password}
          disabled={isDeleting || isUpdating}
          onChange={this.handleInput}
          autoFocus
          required
        />
        {error?.password?.map(
          e => <p key={e.id} className='EntryFormDelete-form-error'>{e.msg}</p>
        )}
        {error?.nonField?.map(
          e => <p key={e.id} className='EntryFormDelete-form-error'>{e.msg}</p>
        )}
        {error?.detail?.map(
          e => <p key={e.id} className='EntryFormDelete-form-error'>{e.msg}</p>
        )}
        <button
          className='EntryFormDelete-form-button'
          type='submit'
          disabled={!canSubmit}
        >
          {isDeleting ? 'Deleting entry...' : 'Confirm delete'}
        </button>
      </form>
    );

    return (
      <div className='EntryFormDelete' ref={this.component}>
        <div
          className='EntryFormDelete-overlay'
          onClick={this.handleClose}
        />
        {formDeleteEntry}
      </div>
    );
  }
}

const mapStateToProps = (state: AppState) => ({
  isDeleting: state.user.isDeleting,
  isUpdating: state.user.isUpdating,
});

const mapDispatchToProps = (dispatch: AppDispatch) => ({
  entryFormDeleteClose: () => {
    dispatch({ type: 'ENTRY_FORM_DELETE_CLOSE' });
  },
  startDeleteEntry: () => {
    dispatch({ type: 'START_DELETE_ENTRY' });
  },
  stopDeleteEntry: () => {
    dispatch({ type: 'STOP_DELETE_ENTRY' });
  },
  successDeleteEntry: () => {
    dispatch({ type: 'SUCCESS_DELETE_ENTRY' });
  },
  startLogoutUser: () => {
    dispatch({ type: 'START_LOGOUT_USER' });
  },
});

const connector = connect(mapStateToProps, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

interface Props extends PropsFromRedux {
  entry: IEntry;
  router: NextRouter;
}

interface IForm {
  password: string;
}

interface State {
  form: IForm;
  error: ReturnType<typeof parseErrorResponse>;
}

export default withRouter(connector(EntryFormDelete));