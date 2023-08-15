import { MouseEventHandler } from 'react';

interface Props {
  onClick: MouseEventHandler<HTMLButtonElement>;
  children: React.ReactNode;
}

const Button = ({ onClick, children }: Props) => {
  return (
    <button
      className="flex flex-shrink-0 cursor-pointer select-none items-center gap-3 rounded-md border border-white/20 p-3 text-white transition-colors duration-200 hover:bg-gray-500/10"
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export default Button;
