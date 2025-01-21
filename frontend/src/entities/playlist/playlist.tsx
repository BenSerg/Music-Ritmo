import { useState, useEffect } from "react";
import styles from "./playlist.module.css";

interface PlaylistProps {
  name: string;
  link: string;
}

export const Playlist = ({ name, link }: PlaylistProps) => {
  const colorOptions = ["#949E7B", "#B3BF7D", "#758934", "#A1BA65", "#405A01"];

  const [randomColor, setRandomColor] = useState<string>("");

  useEffect(() => {
    const getRandomColor = (colors: string[]): string => {
      const randomIndex = Math.floor(Math.random() * colors.length);
      return colors[randomIndex];
    };

    setRandomColor(getRandomColor(colorOptions));
  }, []);

  return (
    <a
      href={link}
      className={styles.playlist}
      style={{ backgroundColor: randomColor }}
    >
      <i className={`fa-regular fa-trash-can ${styles.deleteIcon}`}></i>
      <div className={styles.playlist__name}>{name}</div>
    </a>
  );
};
