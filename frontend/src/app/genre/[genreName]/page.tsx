"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Container } from "@/shared/container";
import { Tracklist } from "@/widgets/track-list";
import { useAuth } from "@/app/auth-context";
import styles from "./genre.module.css";

interface Track {
  id: string;
  title: string;
  artist: string;
  artistId: string;
  duration: number;
  path: string;
  starred: string;
}

export default function TracksGenre() {
  const { genreName } = useParams();
  const [tracks, setTracks] = useState<Track[]>([]);
  const { user, password } = useAuth();
  const [, setStarredTracks] = useState<Track[]>([]);

  const decodedGenreName =
    typeof genreName === "string" ? decodeURIComponent(genreName) : "";

  useEffect(() => {
    if (!genreName) return;

    const fetchTracks = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/rest/getSongsByGenre?genre=${genreName}`
        );
        const data = await response.json();
        const songs = data["subsonic-response"]?.songsByGenre?.song;

        if (songs && songs.length > 0) {
          const tracksData = songs.map((track: Track) => ({
            ...track,
            starred: track.starred || "",
          }));

          setTracks(tracksData);
        } else {
          console.error("Треки не найдены в ответе сервера");
        }
      } catch (error) {
        console.error("Ошибка при загрузке треков:", error);
      }
    };

    fetchTracks();
  }, [genreName]);

  const handleFavouriteToggle = async (
    trackId: string,
    currentStatus: string
  ) => {
    if (!user || !password) return;

    const action = currentStatus ? "unstar" : "star";
    const url = `http://localhost:8000/rest/${action}?id=${trackId}&username=${user}&u=${user}&p=${password}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      if (data["subsonic-response"].status === "ok") {
        setStarredTracks((prevTracks) =>
          prevTracks.filter((track) => track.id !== trackId)
        );
        window.location.reload();
      } else {
        alert("Ошибка при изменении статуса избранного");
      }
    } catch (error) {
      console.error("Ошибка при изменении статуса избранного:", error);
      alert("Произошла ошибка при изменении статуса избранного");
    }
  };

  return (
    <Container
      style={{
        height: "65vh",
        width: "85vw",
        margin: "auto",
        marginTop: "50px",
      }}
      direction="column"
      arrow={true}
      link_arrow="/"
    >
      <h1 className={styles.playlist__title}>{decodedGenreName}</h1>
      <div className={styles.playlist}>
        {tracks.length > 0 ? (
          tracks.map((track) => (
            <Tracklist
              key={track.id}
              name={track.title}
              name_link={`/track/${track.id}`}
              artist={track.artist}
              artist_link={`/artist/${track.artistId}`}
              favourite={track.starred}
              time={track.duration}
              showRemoveButton={false}
              onFavouriteToggle={() =>
                handleFavouriteToggle(track.id, track.starred)
              }
            />
          ))
        ) : (
          <p>Треки не найдены.</p>
        )}
      </div>
    </Container>
  );
}
