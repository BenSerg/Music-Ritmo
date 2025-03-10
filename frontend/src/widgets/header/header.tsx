import { Logo } from "@/shared/logo";
import Link from "next/link";
import React from "react";
import { User } from "@/entities/user";

import styles from "./header.module.css";

export const Header = () => {
  return (
    <div className={styles.header} data-testid="header">
      <div className={styles.header__logo}>
        <Logo type="normal" />
      </div>
      <div className={styles.header__buttons}>
        <Link href="/playlists">
          <i
            className={`fa-solid fa-music ${styles.header__buttons__icons}`}
            role="img"
            aria-label="music"
          />
        </Link>
        <Link href="/favourite-track">
          <i
            className={`fa-solid fa-star ${styles.header__buttons__icons}`}
            role="img"
            aria-label="star"
          />
        </Link>
        <User />
      </div>
    </div>
  );
};
