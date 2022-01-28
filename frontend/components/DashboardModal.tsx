import React, { Component, createRef, MouseEvent, RefObject } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import { disableBodyScroll, enableBodyScroll } from 'body-scroll-lock';

import { AppDispatch, IAction, IModal } from '@/types';


class DashboardModal extends Component<Props> {
  private modal: RefObject<HTMLDivElement>;

  constructor(props: Props) {
    super(props);
    this.modal = createRef();
    this.handleLeftButton = this.handleLeftButton.bind(this);
    this.handleRightButton = this.handleRightButton.bind(this);
    this.handleClose = this.handleClose.bind(this);
  }

  handleLeftButton(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    if (this.props.dashboardModal.leftButton) {
      const { action } = this.props.dashboardModal.leftButton;
      this.props.buttonDispatch(action);
    } else {
      this.props.dashboardModalClose();
    }
  }

  handleRightButton(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    if (this.props.dashboardModal.rightButton) {
      const { action } = this.props.dashboardModal.rightButton;
      this.props.buttonDispatch(action);
    }
  }

  handleClose(e: MouseEvent<HTMLButtonElement | HTMLDivElement>) {
    e.preventDefault();
    this.props.dashboardModalClose();
  }

  componentDidMount() {
    if (this.modal.current) disableBodyScroll(this.modal.current);
  }

  componentWillUnmount() {
    if (this.modal.current) enableBodyScroll(this.modal.current);
  }

  render() {
    const { dashboardModal } = this.props;

    const leftButtonText = dashboardModal.leftButton?.text || 'Close';
    const rightButtonText = dashboardModal.rightButton?.text;

    return (
      <div className='DashboardModal' ref={this.modal}>
        <div className='DashboardModal-overlay' onClick={this.handleClose} />
        <div className='DashboardModal-modal'>
          <p className='DashboardModal-modal-message'>
            {dashboardModal.message}
          </p>
          <div className='DashboardModal-modal-buttons'>
            <button
              className='DashboardModal-modal-button'
              type='button'
              onClick={this.handleLeftButton}
            >
              {leftButtonText}
            </button>
            {dashboardModal.rightButton && (
              <button
                className='DashboardModal-modal-button'
                type='button'
                autoFocus
                onClick={this.handleRightButton}
              >
                {rightButtonText}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }
}

const mapDispatchToProps = (dispatch: AppDispatch) => ({
  buttonDispatch: (action: IAction) => {
    dispatch(action);
  },
  dashboardModalClose: () => {
    dispatch({ type: 'DASHBOARD_MODAL_CLOSE' });
  },
});

const connector = connect(null, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

interface Props extends PropsFromRedux {
  dashboardModal: IModal;
}

export default connector(DashboardModal);