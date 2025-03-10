import React from "react";
import Link from "next/link";
import styles from "./arrow-back.module.css";

interface arrowBackProps {
  className?: string;
  link?: string;
}

export const ArrowBack: React.FC<arrowBackProps> = ({
  className,
  link = "/",
}) => {
  return (
    <Link href={link} className={className} data-testid="arrow-back">
      <i
        className={`fa-solid fa-arrow-left ${styles.arrow}`}
        role="img"
        aria-label="Back"
      />
    </Link>
  );
};
