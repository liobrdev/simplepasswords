import React, { Component, createRef, MouseEvent, RefObject } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import { disableBodyScroll, enableBodyScroll } from 'body-scroll-lock';

import { AppDispatch, IAction, IModal } from '@/types';


class EntryModal extends Component<Props> {
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
    if (this.props.entryModal.leftButton) {
      const { action } = this.props.entryModal.leftButton;
      this.props.buttonDispatch(action);
    } else {
      this.props.entryModalClose();
    }
  }

  handleRightButton(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    if (this.props.entryModal.rightButton) {
      const { action } = this.props.entryModal.rightButton;
      this.props.buttonDispatch(action);
    }
  }

  handleClose(e: MouseEvent<HTMLButtonElement | HTMLDivElement>) {
    e.preventDefault();
    this.props.entryModalClose();
  }

  componentDidMount() {
    if (this.modal.current) disableBodyScroll(this.modal.current);
  }

  componentWillUnmount() {
    if (this.modal.current) enableBodyScroll(this.modal.current);
  }

  render() {
    const { entryModal } = this.props;

    const leftButtonText = entryModal.leftButton?.text || 'Close';
    const rightButtonText = entryModal.rightButton?.text;

    return (
      <div className='EntryModal' ref={this.modal}>
        <div className='EntryModal-overlay' onClick={this.handleClose} />
        <div className='EntryModal-modal'>
          <p className='EntryModal-modal-message'>
            {entryModal.message}
          </p>
          <div className='EntryModal-modal-buttons'>
            <button
              className='EntryModal-modal-button'
              type='button'
              onClick={this.handleLeftButton}
            >
              {leftButtonText}
            </button>
            {entryModal.rightButton && (
              <button
                className='EntryModal-modal-button'
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
  entryModalClose: () => {
    dispatch({ type: 'ENTRY_MODAL_CLOSE' });
  },
});

const connector = connect(null, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

interface Props extends PropsFromRedux {
  entryModal: IModal;
}

export default connector(EntryModal);