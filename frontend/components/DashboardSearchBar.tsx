import { FormEvent, MouseEvent } from 'react';

import { useAppDispatch, useAppSelector } from '@/hooks';

import { CloseIcon, Input, SearchIcon } from './';


export default function DashboardSearchBar() {
  const {
    searchBarOn,
    searchTitle,
  } = useAppSelector((state) => state.dashboard);
  const dispatch = useAppDispatch();

  const handleShow = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    dispatch({ type: 'DASHBOARD_SEARCHBAR_SHOW' });
  };

  const handleClose = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    dispatch({ type: 'DASHBOARD_SEARCHBAR_CLOSE' });
  };

  const handleInput = () => (e: FormEvent<HTMLInputElement>) => {
    const searchTitle = (e.target as HTMLInputElement).value;
    dispatch({ type: 'DASHBOARD_SEARCHBAR_INPUT', searchTitle });
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  const searchBar = (
    <form
      className='DashboardSearchBar-form'
      id='formSearchBar'
      onSubmit={handleSubmit}
    >
      <Input
        className='DashboardSearchBar-form-input'
        name='title'
        type='text'
        value={searchTitle}
        placeholder='Search'
        onChange={handleInput()}
        disabled={!searchBarOn}
        required
        autoFocus
      />
      <div className='CloseIcon-container'>
        <CloseIcon type='button' onClick={handleClose} />
      </div>
    </form>
  );

  const buttonShow = (
    <div className='SearchIcon-container'>
      <SearchIcon type='button' onClick={handleShow} color='purple' />
    </div>
  );

  return (
    <div className={`DashboardSearchBar${searchBarOn ? ' is-on' : ''}`}>
      {searchBarOn ? searchBar : buttonShow}
    </div>
  );
}