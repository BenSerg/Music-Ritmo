import classNames from "classnames";
import React from "react";

import styles from "./input.module.css";

interface InputProps {
  type?: React.HTMLInputTypeAttribute;
  name?: string;
  placeholder?: string;
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  disabled?: boolean;
  className?: string;
  required?: boolean;
  error?: boolean;
  minLength?: number;
  maxLength?: number;
}

export const Input: React.FC<InputProps> = ({
  type = "text",
  name,
  placeholder,
  value,
  onChange = () => {},
  onBlur,
  onFocus,
  disabled = false,
  className,
  required,
  error,
  minLength = 5,
  maxLength = 64,
}) => {
  const inputClassName = classNames(styles.input, className, {
    input_error: error,
  });

  return (
    <input
      type={type}
      name={name}
      className={inputClassName}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      onBlur={onBlur}
      onFocus={onFocus}
      disabled={disabled}
      required={required}
      maxLength={maxLength}
      minLength={minLength}
    />
  );
};
