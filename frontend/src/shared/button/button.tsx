import classNames from "classnames";
import React, { useState } from "react";

import styles from "./button.module.css";

type ButtonType = "normal" | "transparent";
type ButtonColor = "green" | "white" | "green-text";

interface ButtonProps {
  children?: React.ReactNode;
  className?: string;
  type?: ButtonType;
  color?: ButtonColor;
  onClick?: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  type = "normal",
  color = "green",
  onClick,
  disabled,
}) => {
  const [isDisabled, setIsDisabled] = useState<boolean>(false);

  const handleClick = (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent>
  ) => {
    if (onClick) {
      onClick(event);
    }

    setIsDisabled(true);

    setTimeout(() => {
      setIsDisabled(false);
    }, 500);
  };

  const buttonClassName = classNames(className, styles[type], styles[color]);

  return (
    <button
      className={buttonClassName}
      disabled={disabled || isDisabled}
      onClick={handleClick}
    >
      {children}
    </button>
  );
};
