import { Component } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import Head from 'next/head';
import { withRouter, NextRouter } from 'next/router';

import {
  DashboardFormCreateEntry,
  DashboardListEntries,
  DashboardNavigation,
  LoadingView,
  Modal,
} from '@/components';
import { AppDispatch, AppState } from '@/types';


class Dashboard extends Component<Props> {
  private authTimeout?: ReturnType<typeof setTimeout>;

  constructor(props: Props) {
    super(props);
    this.authTimeout = undefined;
    this.handleEsc = this.handleEsc.bind(this);
  }

  handleEsc(e: KeyboardEvent) {
    if (e.code === 'Escape') {
      if (this.props.dashboardModal) {
        this.props.dashboardModalClose();
      } else {
        this.props.dashboardFormClose();
        this.props.dashboardMenuClose();
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
    this.props.dashboardReset();
    window.removeEventListener('keydown', this.handleEsc, false);
  }

  render() {
    const { dashboardModal, error, formOn, menuOn, user } = this.props;

    return !user ? <LoadingView /> : (
      <>
        <Head>
          <title>Dashboard - SimplePasswords</title>
          <meta name='robots' content='noindex, nofollow' />
        </Head>
        <main
          className={`Page Page--dashboard${
            menuOn ? ' is-menuOn' : ''
          }${
            formOn ? ' is-formOn' : ''
          }`}
        >
          {!!dashboardModal && <Modal modal={dashboardModal} />}
          {!error && formOn && <DashboardFormCreateEntry />}
          <DashboardNavigation />
          <h3 className='DashboardHeading'>Dashboard</h3>
          <DashboardListEntries />
          {!error && !formOn && <DashboardFormCreateEntry />}
        </main>
      </>
    );
  }
}

const mapStateToProps = (state: AppState) => ({
  user: state.user.user,
  formOn: state.dashboard.formOnCreateEntry,
  menuOn: state.dashboard.menuOn,
  error: state.dashboard.errorRetrieve,
  dashboardModal: state.dashboard.dashboardModal,
});

const mapDispatchToProps = (dispatch: AppDispatch) => ({
  dashboardFormClose: () => {
    dispatch({ type: 'DASHBOARD_FORM_CLOSE' });
  },
  dashboardMenuClose: () => {
    dispatch({ type: 'DASHBOARD_MENU_CLOSE' });
  },
  dashboardModalClose: () => {
    dispatch({ type: 'DASHBOARD_MODAL_CLOSE' });
  },
  dashboardReset: () => {
    dispatch({ type: 'DASHBOARD_RESET' });
  },
});

const connector = connect(mapStateToProps, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

interface Props extends PropsFromRedux {
  router: NextRouter;
}

export default withRouter(connector(Dashboard));