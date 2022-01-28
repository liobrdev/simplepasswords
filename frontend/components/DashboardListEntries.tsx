import React, { Component, MouseEvent } from 'react';
import { connect, ConnectedProps } from 'react-redux';
import { mutate } from 'swr';

import { debounce } from 'lodash';

import { AppDispatch, AppState } from '@/types';

import {
  DashboardListEmpty,
  DashboardRetrieveEntries,
  EntryThumb,
  LoadingView,
} from './';


class DashboardListEntries extends Component<Props> {
  constructor(props: Props) {
    super(props);
    this.handleClick = debounce(this.handleClick.bind(this), 500, {
      leading: true,
      trailing: false,
    });
  }

  handleClick(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    this.props.refreshEntries();
    mutate('/entries/');
  }

  render() {
    const { entries, errorRetrieve, isRetrieving } = this.props;
    const hasEntries = !!entries?.length && Array.isArray(entries);

    return (
      <div className={`DashboardListEntries${!hasEntries ? ' is-empty' : ''}`}>
        <DashboardRetrieveEntries />
        {isRetrieving ? <LoadingView className='LoadingView--dashboard' /> : (
          <>
            {!errorRetrieve && hasEntries && (
              <ul className='DashboardListEntries-list'>
                {entries.map((listEntry) => (
                  <li
                    className='DashboardListEntries-list-item'
                    key={listEntry.slug}
                  >
                    <EntryThumb { ...listEntry } />
                  </li>
                ))}
              </ul>
            )}
            {!errorRetrieve && !hasEntries && <DashboardListEmpty />}
            {!!errorRetrieve && (
              <div className='DashboardListEntries-error'>
                <p className='DashboardListEntries-error-message'>
                  Sorry, no entries found.
                </p>
                <button
                  className='DashboardListEntries-error-button'
                  type='button'
                  onClick={this.handleClick}
                >
                  Refresh
                </button>
              </div>
            )}
            <div className='Footer Footer--dashboard' />
          </>
        )}
      </div>
    );    
  }
}

const mapStateToProps = (state: AppState) => ({
  entries: state.dashboard.entries,
  errorRetrieve: state.dashboard.errorRetrieve,
  isRetrieving: state.dashboard.isRetrieving,
});

const mapDispatchToProps = (dispatch: AppDispatch) => ({
  refreshEntries: () => {
    dispatch({ type: 'DASHBOARD_SET_ENTRIES', data: [] });
  },
});

const connector = connect(mapStateToProps, mapDispatchToProps);

type Props = ConnectedProps<typeof connector>;

export default connector(DashboardListEntries);