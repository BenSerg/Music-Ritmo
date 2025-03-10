"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Container } from "@/shared/container";
import { Playlist } from "@/entities/playlist";
import styles from "./artist.module.css";

interface Album {
  album: string;
  id: string;
  genre: string;
  year: string;
  coverArt: string;
}

interface Artist {
  id: string;
  name: string;
  album: Album[];
  coverArt: string;
  starred: string | null;
}

export default function Artist() {
  const { artistName } = useParams<{ artistName: string }>();
  const [artist, setArtist] = useState<Artist | null>(null);

  useEffect(() => {
    if (artistName) {
      fetch(`http://localhost:8000/rest/getArtist?id=${artistName}`)
        .then((response) => response.json())
        .then((data) => {
          setArtist(data["subsonic-response"].artist);
        })
        .catch((error) =>
          console.error("Ошибка при получении данных об исполнителе:", error)
        );
    }
  }, [artistName]);

  if (!artist) {
    return <div>Загрузка...</div>;
  }

  return (
    <>
      <Container
        style={{
          height: "75vh",
          width: "85vw",
          margin: "auto",
          marginTop: "50px",
        }}
        direction="column"
        arrow={true}
        link_arrow="/"
      >
        <h1 className={styles.playlist__title}>{artist.name}</h1>

        <div className={styles.playlist}>
          <div className={styles.album_playlists}>
            {artist.album.map((album, index) => (
              <Playlist
                key={index}
                name={album.album}
                link={`/album/${album.id}`}
                coverArt={album.coverArt}
                showDelete={false}
              />
            ))}
          </div>
        </div>
      </Container>
    </>
  );
}
