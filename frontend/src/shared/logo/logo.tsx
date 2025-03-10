import classNames from "classnames";
import React from "react";
import Image from "next/image";

import styles from "./logo.module.css";
import logo from "../../../public/images/logo.svg";

type logoType = "big" | "normal";

interface logoProps {
  type?: logoType;
}

export const Logo: React.FC<logoProps> = ({ type = "normal" }) => {
  const logoClassName = classNames(styles.logo, styles[type]);

  return (
    <div className={logoClassName} data-testid="logo">
      <Image
        src={logo}
        className={styles.img}
        alt="logo"
        width={300}
        height={300}
      />
      <h1>musicRitmo</h1>
    </div>
  );
};
