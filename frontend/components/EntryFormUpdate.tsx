import React, { Component, FormEvent, MouseEvent } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import generator from 'generate-password';
import { debounce } from 'lodash';
import { CopyToClipboard } from 'react-copy-to-clipboard';

import {
  AppDispatch,
  AppState,
  checkEntry,
  IButton,
  IEntry,
  IEntryForm,
  IModal,
} from '@/types';
import { parseErrorResponse, request } from '@/utils';

import { Input, SliderCheckbox, TextArea } from './';


class EntryFormUpdate extends Component<Props, State> {
  private events: string[];
  private warnTimeout?: ReturnType<typeof setTimeout>;
  private hideEntryTimeout?: ReturnType<typeof setTimeout>;

  constructor(props: Props) {
    super(props);
    this.events = ['load', 'mousedown', 'click', 'scroll', 'keydown'];
    this.warnTimeout = undefined;
    this.hideEntryTimeout = undefined;
    this.resetTimeouts = debounce(this.resetTimeouts.bind(this), 250, {
      leading: true,
      trailing: false,
    });

    this.state = {
      form: {
        title: props.entry.title,
        value: props.entry.value,
        password: '',
      },
      valueCopied: false,
      generatorOn: false,
      generatorLength: 16,
      error: {},
    };

    this.handleFormDeleteShow = this.handleFormDeleteShow.bind(this);
    this.handleGeneratePassword = this.handleGeneratePassword.bind(this);
    this.handleGeneratorLength = this.handleGeneratorLength.bind(this);
    this.handleInputTitle = this.handleInputTitle.bind(this);
    this.handleInputValue = this.handleInputValue.bind(this);
    this.handleInputPassword = this.handleInputPassword.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleToggleGenerator = this.handleToggleGenerator.bind(this);
    this.handleUndoChanges = this.handleUndoChanges.bind(this);
    this.handleCopyValue = this.handleCopyValue.bind(this);
  }

  handleInputTitle(e: FormEvent<HTMLInputElement>) {
    e.preventDefault();
    const title: string = (e.target as HTMLInputElement).value;
    this.setState({ form: { ...this.state.form, title } });
  }

  handleInputValue(e: FormEvent<HTMLTextAreaElement>) {
    e.preventDefault();
    const value: string = (e.target as HTMLTextAreaElement).value;
    this.setState({ form: { ...this.state.form, value }, valueCopied: false });
  }

  handleInputPassword(e: FormEvent<HTMLInputElement>) {
    e.preventDefault();
    const password: string = (e.target as HTMLInputElement).value;
    this.setState({ form: { ...this.state.form, password } });
  }

  handleToggleGenerator(e: FormEvent<HTMLInputElement>) {
    const generatorOn = (e.target as HTMLInputElement).checked;
    this.setState({ generatorOn });
  }

  handleGeneratorLength(e: FormEvent<HTMLInputElement>) {
    e.preventDefault();
    const generatorLength: number = +(e.target as HTMLInputElement).value;
    this.setState({ generatorLength });
  }

  handleGeneratePassword(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    const { form, generatorLength } = this.state;

    if (generatorLength < 8) {
      this.setState({ generatorLength: 8 });
    } else {
      const value = generator.generate({
        length: generatorLength,
        numbers: true,
        symbols: true,
        strict: true,
      });
      this.setState({ form: { ...form, value }, valueCopied: false });
    }
  }

  handleUndoChanges(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    this.setState({
      form: {
        title: this.props.entry.title,
        value: this.props.entry.value,
        password: '',
      },
      valueCopied: false,
    });
    this.setState({ error: {} });
    window.scrollTo(0, 0);
    (document.activeElement as HTMLElement).blur();
  }

  handleFormDeleteShow(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    this.props.entryFormDeleteShow();
  }

  handleCopyValue(text: string, result: boolean) {
    this.setState({ valueCopied: true });
  }

  async handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const { form } = this.state;
    this.props.startUpdateEntry();
    this.setState({ error: {} });

    try {
      const token = localStorage.getItem('simplepasswords_token');
      const entry = await request
        .put(`/entry_update/${this.props.entry.slug}/`)
        .set({ 'Authorization': `Token ${token}` })
        .send({ ...form })
        .then((res) => checkEntry(res.body, res));
      this.props.successUpdateEntry(entry);    
      const { title, value } = entry;
      this.setState({
        form: { title, value, password: '' },
        valueCopied: false,
      });
      window.scrollTo(0, 0);
      const entryModal: IModal = {
        message: 'Update successful!',
        page: 'entry',
      };
      this.props.entryModalShow(entryModal);
    } catch (err: any) {
      this.props.stopUpdateEntry();
      console.error(err);

      const res = err?.response;
      if (res?.unauthorized || res?.forbidden || res?.notFound) {
        localStorage.removeItem('simplepasswords_token');
        this.props.startLogoutUser();
      }

      const error = parseErrorResponse(res?.body, Object.keys(form));
      this.setState({ error });
    } finally {
      (document.activeElement as HTMLElement).blur();
    }
  }

  setWarnTimeout() {
    // Show warning after 30 seconds of inactivity
    this.warnTimeout = setTimeout(() => {
      const page = 'entry';

      const message = (
        "This entry will be hidden automatically after " +
        "30 more seconds of inactivity. " +
        "Click 'Cancel' to keep working."
      );

      const leftButton: IButton = {
        text: 'Hide now',
        action: { type: 'ENTRY_RESET' },
      };

      const rightButton: IButton = {
        text: 'Cancel',
        action: { type: 'ENTRY_MODAL_CLOSE' },
      };

      const entryModal: IModal = { page, message, leftButton, rightButton };
      this.props.entryModalShow(entryModal);
      this.setHideEntryTimeout();
    }, 30 * 1000);
  }

  setHideEntryTimeout() {
    // Hide entry after another 30s of inactivity
    this.hideEntryTimeout = setTimeout(() => {
      this.props.entryReset();
    }, 30 * 1000);
  }

  clearTimeouts() {
    if (this.warnTimeout) clearTimeout(this.warnTimeout);
    if (this.hideEntryTimeout) clearTimeout(this.hideEntryTimeout);
  }

  resetTimeouts() {
    // Clear any active timeouts,
    // then restart the 30-second warning countdown
    this.clearTimeouts();
    this.setWarnTimeout();
  }

  componentDidMount() {
    this.events.forEach((event) => {
      document.addEventListener(event, this.resetTimeouts);
    });
    this.setWarnTimeout();
  }

  componentWillUnmount() {
    this.events.forEach((event) => {
      document.removeEventListener(event, this.resetTimeouts);
    });
    this.clearTimeouts();
  }
  
  render() {
    const { formOnDeleteEntry, isDeleting, isUpdating } = this.props;
    const {
      form, valueCopied, generatorLength, generatorOn, error,
    } = this.state;

    const canSubmit = (
      !!form.title && !!form.value && !!form.password &&
      !isDeleting && !isUpdating
    );

    const rootClass = 'EntryFormUpdate';

    const spanCopyValue = (
      <CopyToClipboard text={form.value} onCopy={this.handleCopyValue}>
        <span className={rootClass + '-copyValue'}>
          {valueCopied ? 'Copied to clipboard!' : 'Copy'}
        </span>
      </CopyToClipboard>
    );

    return (
      <div className={rootClass}>
        <form
          className={rootClass + '-form'}
          onSubmit={canSubmit ? this.handleSubmit : undefined}
        >
          <div className={rootClass + '-form-titleContainer'}>
            <Input
              className={rootClass + '-form-input'}
              label='Entry title'
              type='text'
              name='title'
              value={form.title}
              minLength={1}
              maxLength={255}
              disabled={isUpdating || isDeleting}
              onChange={this.handleInputTitle}
              required
              showAsterisk
            />
            {error.title?.map(e =>
              <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
            )}
            <SliderCheckbox
              className={`${rootClass}-form-checkbox`}
              label='Generate password?'
              type='checkbox'
              name='generatorOn'
              checked={generatorOn}
              disabled={isUpdating || isDeleting}
              onChange={this.handleToggleGenerator}
            />
            <Input
              className={`${rootClass}-form-generatorLength`}
              label='Password length'
              type='number'
              name='generatorLength'
              min={8}
              max={256}
              value={generatorLength}
              onChange={this.handleGeneratorLength}
              disabled={!generatorOn || isUpdating || isDeleting}
            />
            <button
              className={`${rootClass}-form-button ${rootClass}-form-button--generator`}
              type='button'
              disabled={!generatorOn || isUpdating || isDeleting}
              onClick={this.handleGeneratePassword}
            >
              Generate
            </button>
          </div>
          <div className={rootClass + '-form-passwordContainer'}>
            <TextArea
              className={rootClass + '-form-textArea'}
              label={<>Value {spanCopyValue}</>}
              name='value'
              value={form.value}
              minLength={1}
              disabled={isUpdating || isDeleting}
              onChange={this.handleInputValue}
              required
              showAsterisk
            />
            {error.value?.map(e =>
              <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
            )}
            <Input
              className={rootClass + '-form-input'}
              type='password'
              label='Enter master password'
              name='password'
              value={form.password}
              disabled={isUpdating || isDeleting}
              minLength={1}
              onChange={this.handleInputPassword}
              autoFocus
              showAsterisk
              required
            />
            {error.password?.map(e =>
              <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
            )}
            <button
              className={`${rootClass}-form-button ${rootClass}-form-button--undoShort`}
              type='button'
              disabled={isUpdating || isDeleting}
              onClick={this.handleUndoChanges}
            >
              Undo changes
            </button>
            <button
              className={`${rootClass}-form-button ${rootClass}-form-button--saveShort`}
              type='submit'
              disabled={!canSubmit}
            >
              {isUpdating ? 'Saving changes...' : 'Save changes'}
            </button>
            <div className='EntryButtonDelete EntryButtonDelete--short'>
              <button
                className='EntryButtonDelete-button'
                type='button'
                disabled={formOnDeleteEntry || isDeleting || isUpdating}
                onClick={this.handleFormDeleteShow}
              >
                Delete this entry
              </button>
            </div>
          </div>
          {error.nonField?.map(e => 
            <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
          )}
          {error.detail?.map(e => 
            <p key={e.id} className={rootClass + '-form-error'}>{e.msg}</p>
          )}
          <br/>
          <button
            className={`${rootClass}-form-button ${rootClass}-form-button--undoTall`}
            type='button'
            disabled={isUpdating || isDeleting}
            onClick={this.handleUndoChanges}
          >
            Undo changes
          </button>
          <button
            className={`${rootClass}-form-button ${rootClass}-form-button--saveTall`}
            type='submit'
            disabled={!canSubmit}
          >
            {isUpdating ? 'Saving changes...' : 'Save changes'}
          </button>
          <div className='EntryButtonDelete EntryButtonDelete--tall'>
            <button
              className='EntryButtonDelete-button'
              type='button'
              disabled={formOnDeleteEntry || isDeleting || isUpdating}
              onClick={this.handleFormDeleteShow}
            >
              Delete this entry
            </button>
          </div>
        </form>
      </div>
    );
  }
}

const mapStateToProps = (state: AppState) => ({
  formOnDeleteEntry: state.entry.formOnDeleteEntry,
  isUpdating: state.entry.isUpdating,
  isDeleting: state.entry.isDeleting,
});

const mapDispatchToProps = (dispatch: AppDispatch) => ({
  startUpdateEntry: () => {
    dispatch({ type: 'START_UPDATE_ENTRY' });
  },
  stopUpdateEntry: () => {
    dispatch({ type: 'STOP_UPDATE_ENTRY' });
  },
  successUpdateEntry: (entry: IEntry) => {
    dispatch({ type: 'SUCCESS_UPDATE_ENTRY', entry });
  },
  entryFormDeleteShow: () => {
    dispatch({ type: 'ENTRY_FORM_DELETE_SHOW' });
  },
  startLogoutUser: () => {
    dispatch({ type: 'START_LOGOUT_USER' });
  },
  entryModalShow: (entryModal: IModal) => {
    dispatch({ type: 'ENTRY_MODAL_SHOW', entryModal });
  },
  entryReset: () => {
    dispatch({ type: 'ENTRY_RESET' });
  },
});

const connector = connect(mapStateToProps, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

interface Props extends PropsFromRedux {
  entry: IEntry;
}

interface State {
  form: IEntryForm;
  valueCopied: boolean;
  generatorOn: boolean;
  generatorLength: number;
  error: ReturnType<typeof parseErrorResponse>;
}

export default connector(EntryFormUpdate);