import React, { Component, FocusEvent, TextareaHTMLAttributes } from 'react';


interface Props extends TextareaHTMLAttributes<HTMLTextAreaElement>{
  label?: string | JSX.Element;
  showAsterisk?: boolean;
}

export default class TextArea extends Component<Props> {
  handleFocus(e: FocusEvent<HTMLTextAreaElement>) {
    e.preventDefault();
    e.target.select();
  }

  render() {
    const { className, id, showAsterisk, ...rest } = this.props;
    const { disabled, label, name, required } = rest;

    return (
      <div className={`TextArea${!!className ? ' ' + className : ''}`} id={id}>
        {!!label && (
          <label
            htmlFor={name}
            style={disabled ? { opacity: '0.66667' } : undefined}
          >
            {label}
          </label>
        )}
        <textarea
          { ...rest }
          id={name}
          onFocus={this.handleFocus}
        />
        {required && showAsterisk && (
          <span className='TextArea-asterisk'>*</span>
        )}
      </div>
    );
  }
};