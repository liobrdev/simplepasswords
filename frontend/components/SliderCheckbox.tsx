import React, { Component, FocusEvent, InputHTMLAttributes } from 'react';


interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string | JSX.Element;
  showAsterisk?: boolean;
  showObelisk?: boolean;
}

export default class SliderCheckbox extends Component<Props> {
  handleFocus(e: FocusEvent<HTMLInputElement>) {
    e.preventDefault();
    e.target.select();
  }

  render() {
    const { className, id, showAsterisk, showObelisk, ...rest } = this.props;
    const { label, name, required, disabled } = rest;

    return (
      <div
        id={id}
        className={`Input Input--sliderCheckbox${
          !!className ? ' ' + className : ''
        }`}
      >
        {!!label && (
          <label
            htmlFor={name}
            style={disabled ? { opacity: '0.66667' } : undefined}
          >
            {label}
          </label>
        )}
        <div className='SliderCheckbox SliderCheckbox--round'>
          <input
            { ...rest }
            type='checkbox'
            id={name}
            onFocus={this.handleFocus}
          />
          <span className='SliderCheckbox-slider SliderCheckbox-slider--round' />
        </div>
        {required && showAsterisk && (
          <span className='Input-asterisk'>*</span>
        )}
        {showObelisk && (
          <span className='Input-obelisk'>&dagger;</span>
        )}
      </div>
    );
  }
};