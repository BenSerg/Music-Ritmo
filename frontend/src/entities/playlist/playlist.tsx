import React, { useState, useEffect } from "react";
import { Button } from "@/shared/button";
import Image from "next/image";
import styles from "./playlist.module.css";
import Link from "next/link";

interface PlaylistProps {
  name: string;
  link?: string;
  showDelete: boolean;
  playlist_id?: string;
  onDelete?: (id: string) => void;
  coverArt?: string;
}

export const Playlist = ({
  name,
  link = "/",
  showDelete,
  playlist_id,
  onDelete,
  coverArt,
}: PlaylistProps) => {
  const colorOptions = ["#949E7B", "#B3BF7D", "#758934", "#A1BA65", "#405A01"];
  const [randomColor, setRandomColor] = useState<string>("");
  const [showModal, setShowModal] = useState<boolean>(false);
  const [, setDeleteStatus] = useState<string>("");
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
    }
  }, [coverArt]);

  const handleDeleteClick = () => {
    setShowModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!playlist_id) {
      setDeleteStatus("Не удалось найти идентификатор плейлиста");
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/rest/deletePlaylist?id=${playlist_id}`
      );
      const data = await response.json();

      if (data["subsonic-response"]?.status === "ok") {
        setDeleteStatus("Плейлист успешно удален!");

        if (onDelete) {
          onDelete(playlist_id);
        }

        setTimeout(() => setShowModal(false), 2000);
      } else {
        setDeleteStatus("Ошибка при удалении плейлиста");
      }
    } catch (error) {
      console.error("Ошибка при запросе на сервер:", error);
      setDeleteStatus("Произошла ошибка при удалении плейлиста");
    }
  };

  const handleDeleteCancel = () => {
    setShowModal(false);
  };

  return (
    <div>
      <div
        className={styles.playlist}
        style={{ backgroundColor: randomColor }}
        data-testid="playlist"
      >
        {image && (
          <Image
            src={image}
            alt={`${name} cover`}
            width={150}
            height={150}
            role="img"
            className={styles.playlist__cover}
          />
        )}
        {showDelete && (
          <i
            role="button"
            className={`fa-regular fa-trash-can ${styles.deleteIcon}`}
            onClick={handleDeleteClick}
            aria-label="delete"
          ></i>
        )}
        <Link href={link} role="link" data-testid="playlist-link">
          <div className={styles.playlist__name}>{name}</div>
        </Link>
      </div>

      {showModal && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <p>Вы уверены, что хотите удалить плейлист {name}?</p>

            <Button
              type="normal"
              color="green"
              disabled={false}
              onClick={handleDeleteConfirm}
            >
              Да
            </Button>

            <Button
              type="normal"
              color="white"
              disabled={false}
              onClick={handleDeleteCancel}
            >
              Нет
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
