"use client";

import React, { useState, useEffect } from "react";
import { Container } from "@/shared/container";
import { Input } from "@/shared/input";
import { Button } from "@/shared/button";
import styles from "./playlist.module.css";
import { Tracklist } from "@/widgets/track-list";
import { useParams } from "next/navigation";
import { useAuth } from "@/app/auth-context";

interface Track {
  id: string;
  title: string;
  artist: string;
  artistId: string;
  duration: number;
  path: string;
  starred: string;
}

interface Playlist {
  id: string;
  name: string;
  entry: Track[];
}

export default function Playlist() {
  const { playlistId } = useParams();
  const [playlistData, setPlaylistData] = useState<Playlist | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [playlistName, setPlaylistName] = useState<string>("");
  const [existingPlaylists, setExistingPlaylists] = useState<string[]>([]);
  const [nameError, setNameError] = useState<string | null>(null);
  const [trackToRemove, setTrackToRemove] = useState<number | null>(null);
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false);
  const [renameSuccess, setRenameSuccess] = useState(false);
  const { user, password } = useAuth();
  const [, setStarredTracks] = useState<Track[]>([]);

  useEffect(() => {
    const fetchPlaylistData = async () => {
      if (!playlistId) return;

      try {
        const response = await fetch(
          `http://localhost:8000/rest/getPlaylist?id=${playlistId}`
        );
        const data = await response.json();

        console.log("Fetched playlist data:", data);

        if (data["subsonic-response"]?.status === "ok") {
          const playlist: Playlist = {
            id: data["subsonic-response"].playlist.id,
            name: data["subsonic-response"].playlist.name,
            entry: data["subsonic-response"].playlist.entry.map(
              (track: Track) => ({
                id: track.id,
                title: track.title,
                artist: track.artist,
                artistId: track.artistId,
                starred: track.starred,
                duration: track.duration,
              })
            ),
          };
          setPlaylistData(playlist);
          setPlaylistName(playlist.name);
        } else {
          console.error("Failed to fetch playlist data:", data);
        }
      } catch (error) {
        console.error("Error fetching playlist data:", error);
      }
    };

    const fetchPlaylists = async () => {
      try {
        const userLogin = "test_user";
        const response = await fetch(
          `http://localhost:8000/rest/getPlaylists?username=${userLogin}`
        );
        const data = await response.json();

        console.log("Fetched playlists:", data);

        if (data["subsonic-response"].status === "ok") {
          const fetchedPlaylists: Playlist[] =
            data["subsonic-response"].playlists.playlist;
          setExistingPlaylists(
            fetchedPlaylists.map((playlist) => playlist.name)
          );
        } else {
          console.error("Failed to fetch existing playlists:", data);
        }
      } catch (error) {
        console.error("Error fetching existing playlists:", error);
      }
    };

    fetchPlaylistData();
    fetchPlaylists();
  }, [playlistId]);

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

      console.log("Favourite toggle response:", data);

      if (data["subsonic-response"].status === "ok") {
        setStarredTracks((prevTracks) =>
          prevTracks.filter((track) => track.id !== trackId)
        );
        window.location.reload();
      } else {
        alert("Ошибка при изменении статуса избранного");
      }
    } catch (error) {
      console.error("Error toggling favourite:", error);
      alert("Произошла ошибка при изменении статуса избранного");
    }
  };

  const openModal = () => setIsModalOpen(true);

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    setPlaylistName(newName);

    if (newName.length < 5) {
      setNameError("Длина названия должна быть не меньше 5 символов");
    } else if (newName.length > 64) {
      setNameError("Длина названия не может превышать 64 символа");
    } else if (existingPlaylists.includes(newName)) {
      setNameError("Плейлист с таким названием уже существует");
    } else {
      setNameError(null);
    }
  };

  const [, setRenameError] = useState<string | null>(null);

  const handleSaveChanges = async () => {
    if (nameError) return;

    try {
      const response = await fetch(
        `http://localhost:8000/rest/updatePlaylist?playlistId=${playlistId}&name=${encodeURIComponent(
          playlistName
        )}&username=${user}&u=${user}&p=${password}`,
        { method: "GET" }
      );
      const data = await response.json();
      const albumData = data["subsonic-response"]?.playlist.entry;

      console.log("Updated playlist data:", albumData);

      if (data["subsonic-response"].status === "ok") {
        setRenameSuccess(true);
      } else {
        setRenameError("Ошибка при изменении названия плейлиста");
      }
    } catch (error) {
      console.error("Ошибка при сохранении изменений:", error);
      setRenameError("Произошла ошибка при изменении названия плейлиста");
    }
  };

  const confirmRemoveTrack = async () => {
    if (trackToRemove === null) return;

    const trackToDelete = playlistData?.entry[trackToRemove];
    if (!trackToDelete) return;

    try {
      const response = await fetch(
        `http://localhost:8000/rest/updatePlaylist?playlistId=${playlistId}&songIndexToRemove=${trackToRemove}&username=${user}&u=${user}&p=${password}`,
        { method: "GET" }
      );
      const data = await response.json();

      console.log("Remove track response:", data);

      if (data["subsonic-response"].status === "ok") {
        setPlaylistData((prev) => {
          if (prev) {
            const updatedEntries = prev.entry.filter(
              (track, index) => index !== trackToRemove
            );
            return { ...prev, entry: updatedEntries };
          }
          return prev;
        });
      } else {
        alert("Ошибка при удалении трека");
      }
    } catch (error) {
      console.error("Ошибка при удалении трека:", error);
      alert("Произошла ошибка при удалении трека");
    }

    setIsRemoveModalOpen(false);
    setTrackToRemove(null);
  };

  const handleRemoveTrack = (index: number) => {
    setTrackToRemove(index);
    setIsRemoveModalOpen(true);
  };

  if (!playlistData) {
    return <div>Загрузка...</div>;
  }

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
        link_arrow="/playlists"
      >
        <h1 className={styles.playlist__title}>{playlistData.name}</h1>
        <div className={styles.playlist}>
          {playlistData.entry.map((track, index) => {
            return (
              <Tracklist
                key={track.id}
                name={track.title}
                name_link={`/track/${track.id}`}
                artist={track.artist}
                artist_link={`/artist/${track.artistId}`}
                favourite={track.starred}
                time={track.duration}
                showRemoveButton={true}
                onRemove={() => handleRemoveTrack(index)}
                onFavouriteToggle={() =>
                  handleFavouriteToggle(track.id, track.starred)
                }
              />
            );
          })}
        </div>
      </Container>

      <div className={styles.playlist_button}>
        <Button
          type="normal"
          color="green"
          disabled={false}
          onClick={openModal}
        >
          редактировать
        </Button>
      </div>

      {isRemoveModalOpen && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <button
              className={styles.closeButton}
              onClick={() => setIsRemoveModalOpen(false)}
            >
              <i className="fa-solid fa-xmark"></i>
            </button>

            <h2 className={styles.create_playlists__title}>
              Вы уверены, что хотите удалить этот трек из плейлиста?
            </h2>

            <div style={{ display: "flex", justifyContent: "center" }}>
              <Button type="normal" color="green" onClick={confirmRemoveTrack}>
                Да
              </Button>
              <Button
                type="normal"
                color="white"
                onClick={() => setIsRemoveModalOpen(false)}
              >
                Нет
              </Button>
            </div>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <button
              className={styles.closeButton}
              onClick={() => {
                setIsModalOpen(false);
                window.location.reload();
              }}
            >
              <i className="fa-solid fa-xmark"></i>
            </button>

            <h1 className={styles.create_playlists__title}>
              Изменение названия плейлиста
            </h1>

            <Input
              placeholder="Название плейлиста"
              value={playlistName}
              onChange={handleNameChange}
            />
            {nameError && <div className={styles.error}>{nameError}</div>}

            {renameSuccess && (
              <div className={styles.success}>Название успешно сохранено</div>
            )}

            <div style={{ display: "flex", justifyContent: "center" }}>
              <Button
                type="normal"
                color="green"
                disabled={Boolean(nameError) || !playlistName}
                onClick={handleSaveChanges}
              >
                сохранить название
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
