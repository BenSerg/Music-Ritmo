import React, { useState, useEffect } from "react";
import Image from "next/image";
import styles from "./artist.module.css";

interface PlaylistProps {
  name: string;
  link: string;
  coverArt?: string;
}

export const Artist = ({ name, link, coverArt }: PlaylistProps) => {
  const colorOptions = ["#949E7B", "#B3BF7D", "#758934", "#A1BA65", "#405A01"];
  const [randomColor, setRandomColor] = useState<string>("");
  const [image, setImage] = useState<string | null>(null);

  useEffect(() => {
    const getRandomColor = (colors: string[]): string => {
      const randomIndex = Math.floor(Math.random() * colors.length);
      return colors[randomIndex];
    };

    setRandomColor(getRandomColor(colorOptions));

    if (coverArt) {
      fetch(`http://localhost:8000/rest/getCoverArt?id=${coverArt}`)
        .then((response) => response.blob())
        .then((imageBlob) => {
          const imageUrl = URL.createObjectURL(imageBlob);
          setImage(imageUrl);
        })
        .catch((error) =>
          console.error("Ошибка при загрузке изображения:", error)
        );

      console.log(coverArt);
    }
  }, [coverArt]);
  return (
    <a
      href={link}
      className={styles.playlist}
      style={{ backgroundColor: randomColor }}
    >
      {image && (
        <Image
          src={image}
          alt={`${name} cover`}
          role="img"
          width={150}
          height={150}
          className={styles.playlist__cover}
        />
      )}
      <div className={styles.playlist__name}>{name}</div>
    </a>
  );
};
