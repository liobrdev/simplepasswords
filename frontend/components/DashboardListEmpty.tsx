import React, { Component } from 'react';
import { connect, ConnectedProps } from 'react-redux';

import { AppState } from '@/types';


class DashboardListEmpty extends Component<Props, State> {
  private loadingTimeout?: ReturnType<typeof setTimeout>;

  constructor(props: Props) {
    super(props);
    this.state = { messageOn: false };
    this.loadingTimeout = undefined;
  }

  componentDidMount() {
    this.loadingTimeout = setTimeout(() => {
      this.setState({ messageOn: true });
    }, 500);
  }

  componentWillUnmount() {
    if (this.loadingTimeout) clearTimeout(this.loadingTimeout);
  }

  render() {
    const { searchBarOn } = this.props;
    const { messageOn } = this.state;

    return messageOn ? (
      <p className='DashboardListEntries-message'>
        {searchBarOn ? 'No matching entries found.' : (
          <>
            You don&apos;t have any entries at the moment.
            Tap <span>+</span> to create one!
          </>
        )}
      </p>
    ) : null;
  }
}

const mapStateToProps = (state: AppState) => ({
  searchBarOn: state.dashboard.searchBarOn,
});

const connector = connect(mapStateToProps);

type Props = ConnectedProps<typeof connector>;

interface State {
  messageOn: boolean;
}

export default connector(DashboardListEmpty);