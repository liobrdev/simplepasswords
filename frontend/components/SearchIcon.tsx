import { ButtonHTMLAttributes } from 'react';


interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  color?: string;
  src?: string;
}

export default function SearchIcon(props: Props) {
  const { className, color, src } = props;

  return (
    <button
      { ...props }
      className={`SearchIcon${className ? ' ' + className : ''}`}
    >
      <div className='SearchIcon-image-container'>
        <img
          className='SearchIcon-image'
          src={src ? src : `/search${color ? '-' + color : '-red'}.png`}
          width='60%'
          alt='Search'
        />
      </div>
    </button>
  );
}