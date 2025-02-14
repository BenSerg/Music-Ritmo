"use client";

import { Container } from "@/shared/container";
import React, { useState, useEffect } from "react";
import { Tracklist } from "@/widgets/track-list";
import { useAuth } from "@/app/auth-context";
import styles from "./favourite-track.module.css";

interface Track {
  id: string;
  title: string;
  artist: string;
  artistId: string;
  album: string;
  duration: number;
  coverArt: string;
  starred: string;
  playCount: number;
}

export default function FavouriteTrack() {
  const [starredTracks, setStarredTracks] = useState<Track[]>([]);
  const { user, password } = useAuth();

  const fetchStarredTracks = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/rest/getStarred2?username=${user}&u=${user}&p=${password}`
      );

      if (!response.ok) {
        throw new Error(`Ошибка при запросе: ${response.status}`);
      }

      const data = await response.json();

      if (data["subsonic-response"]?.status === "ok") {
        const { song } = data["subsonic-response"]["starred2"];

        const starred = song?.filter(
          (track: Track) => track.starred === "true"
        );
        setStarredTracks(starred || []);
      } else {
        console.error("Ошибка получения данных");
      }
    } catch (error) {
      console.error("Ошибка при запросе данных:", error);
    }
  };

  useEffect(() => {
    fetchStarredTracks();
  }, []);

  const handleFavouriteToggle = async (
    trackId: string,
    currentStatus: string
  ) => {
    const action = currentStatus ? "unstar" : "star";
    const url = `http://localhost:8000/rest/${action}?id=${trackId}`;

    try {
      const response = await fetch(url);
      const data = await response.json();
      if (data["subsonic-response"].status === "ok") {
        setStarredTracks((prevTracks) =>
          prevTracks
            .map((track) =>
              track.id === trackId
                ? {
                    ...track,
                    starred: currentStatus ? "" : "true",
                  }
                : track
            )
            .filter((track) => track.starred === "true")
        );
      } else {
        alert("Ошибка при изменении статуса избранного");
      }
    } catch (error) {
      console.error("Ошибка при изменении статуса избранного:", error);
      alert("Произошла ошибка при изменении статуса избранного");
    }
  };

  return (
    <>
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
        <h1 className={styles.playlist__title}>Избранные треки</h1>
        <div className={styles.playlist}>
          {starredTracks.length > 0 ? (
            starredTracks.map((track) => (
              <Tracklist
                key={track.id}
                name={track.title}
                name_link={`/track/${track.id}`}
                artist={track.artist}
                artist_link={`/artist/${track.artistId}`}
                favourite={track.starred === "true"}
                time={track.duration}
                showRemoveButton={false}
                onFavouriteToggle={() =>
                  handleFavouriteToggle(track.id, track.starred)
                }
              />
            ))
          ) : (
            <p>Нет избранных треков</p>
          )}
        </div>
      </Container>
    </>
  );
}
