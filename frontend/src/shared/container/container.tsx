import classNames from "classnames";
import React from "react";
import { ArrowBack } from "@/shared/arrow-back";

import styles from "./container.module.css";

type directionType = "row" | "column";

interface ContainerProps {
  children?: React.ReactNode;
  style?: React.CSSProperties;
  direction?: directionType;
  arrow?: boolean;
  link_arrow?: string;
}

export const Container: React.FC<ContainerProps> = ({
  children,
  style,
  direction = "column",
  arrow = false,
  link_arrow = "",
}) => {
  const containerClassName = classNames(styles.container, styles[direction]);

  return (
    <div className={containerClassName} style={style} data-testid="container">
      {arrow && <ArrowBack className={styles.arrow} link={link_arrow} />}
      {children}
    </div>
  );
};
