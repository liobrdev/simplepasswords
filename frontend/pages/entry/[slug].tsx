import React, { Component, MouseEvent } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import Head from 'next/head';
import { withRouter, NextRouter } from 'next/router';

import {
  EntryFormRetrieve,
  EntryFormUpdate,
  EntryFormDelete,
  LeftArrowIcon,
  LoadingView,
  Modal,
} from '@/components';
import { AppDispatch, AppState } from '@/types';


class Entry extends Component<Props> {
  private authTimeout?: ReturnType<typeof setTimeout>;

  constructor(props: Props) {
    super(props);
    this.authTimeout = undefined;
    this.handleBack = this.handleBack.bind(this);
    this.handleEsc = this.handleEsc.bind(this);
  }

  handleBack(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    this.props.router.push('/dashboard');
  };

  handleEsc(e: KeyboardEvent) {
    if (e.code === 'Escape') {
      if (this.props.entryModal) {
        this.props.entryModalClose();
      } else {
        this.props.entryFormDeleteClose();
      }
    }
  }

  componentDidMount() {
    this.authTimeout = setTimeout(() => {
      if (!this.props.user) this.props.router.replace('/login');
    }, 4000);
    window.addEventListener('keydown', this.handleEsc, false);
  }

  componentDidUpdate(prevProps: Props) {
    // Once logged in, clear timeout
    if (this.props.user && !prevProps.user) {
      if (this.authTimeout) clearTimeout(this.authTimeout);
    }

    // If not logged in, redirect to login page
    if (!this.props.user && prevProps.user) {
      this.props.router.replace('/login');
    }
  }

  componentWillUnmount() {
    if (this.authTimeout) clearTimeout(this.authTimeout);
    this.props.entryReset();
    window.removeEventListener('keydown', this.handleEsc, false);
  }

  render() {
    const { entry, entryModal, formOnDeleteEntry } = this.props;
    const { slug } = this.props.router.query;
    let entrySlug: string | undefined;

    if (typeof slug === 'string') entrySlug = slug;

    return !this.props.user ? <LoadingView /> : (
      <>
        <Head>
          <title>SimplePasswords</title>
          <meta name='robots' content='noindex, nofollow' />
        </Head>
        <main className='Page Page--entry'>
          {!!entryModal && <Modal modal={entryModal}/>}
          {!!entry && formOnDeleteEntry && <EntryFormDelete entry={entry} />}
          <div className='LeftArrowIcon-container'>
            <LeftArrowIcon
              onClick={this.handleBack}
              src='/left-arrow-wh.png'
              type='button'
              title='Back to dashboard'
            />
          </div>
          {!entry && !!entrySlug && <EntryFormRetrieve slug={entrySlug} />}
          {!!entry && <EntryFormUpdate entry={entry} />}
          <div className='Footer Footer--entry' />
        </main>
      </>
    );
  }
}

const mapStateToProps = (state: AppState) => ({
  user: state.user.user,
  entry: state.entry.entry,
  entryModal: state.entry.entryModal,
  formOnDeleteEntry: state.entry.formOnDeleteEntry,
});

const mapDispatchToProps = (dispatch: AppDispatch) => ({
  entryModalClose: () => {
    dispatch({ type: 'ENTRY_MODAL_CLOSE' });
  },
  entryFormDeleteClose: () => {
    dispatch({ type: 'ENTRY_FORM_DELETE_CLOSE' });
  },
  entryReset: () => {
    dispatch({ type: 'ENTRY_RESET' });
  },
});

const connector = connect(mapStateToProps, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

interface Props extends PropsFromRedux {
  router: NextRouter;
}

export default withRouter(connector(Entry));