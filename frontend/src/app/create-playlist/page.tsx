"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Container } from "@/shared/container";
import { Input } from "@/shared/input";
import { Button } from "@/shared/button";
import { useAuth } from "@/app/auth-context";
import styles from "./create_playlist.module.css";

interface Playlist {
  id: string;
  name: string;
  owner: string;
  public: boolean;
  created: string;
  changed: string;
  songCount: number;
  duration: number;
}

export default function CreatePlaylist() {
  const router = useRouter();
  const { user, password } = useAuth();
  const [playlistName, setPlaylistName] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [existingPlaylists, setExistingPlaylists] = useState<string[]>([]);
  const [nameError, setNameError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const userLogin = "test_user";
        const response = await fetch(
          `http://localhost:8000/rest/getPlaylists?username=${userLogin}`
        );
        const data = await response.json();

        if (data["subsonic-response"].status === "ok") {
          const fetchedPlaylists: Playlist[] =
            data["subsonic-response"].playlists.playlist;
          setExistingPlaylists(
            fetchedPlaylists.map((playlist) => playlist.name)
          );
          setError(null);
        } else {
          setError("Не удалось загрузить плейлисты");
        }
      } catch {
        setError("Произошла ошибка при получении плейлистов");
      }
    };

    fetchPlaylists();
  }, []);

  const handleCreatePlaylist = async () => {
    if (!playlistName) {
      setError("Название плейлиста не может быть пустым");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const userLogin = "test_user";
      const response = await fetch(
        `http://localhost:8000/rest/createPlaylist?name=${encodeURIComponent(
          playlistName
        )}&u=${encodeURIComponent(
          userLogin
        )}?username=${user}&u=${user}&p=${password}`,
        {
          method: "GET",
        }
      );

      const data = await response.json();

      if (data["subsonic-response"].status === "ok") {
        router.push("/playlists");
      } else {
        setError("Не удалось создать плейлист");
      }
    } catch {
      setError("Произошла ошибка при создании плейлиста");
    } finally {
      setLoading(false);
    }
  };

  const isNameTooShort = playlistName.length < 5;
  const isNameAlreadyExists = existingPlaylists.includes(playlistName);

  useEffect(() => {
    if (isNameAlreadyExists) {
      setNameError("Плейлист с таким названием уже существует");
    } else {
      setNameError(null);
    }
  }, [playlistName, isNameAlreadyExists]);

  return (
    <>
      <Container
        style={{
          height: "35vh",
          width: "50vw",
          margin: "auto",
          marginTop: "50px",
        }}
        direction="column"
        arrow={true}
        link_arrow="/playlists"
      >
        <h1 className={styles.create_playlists__title}>Создание плейлиста</h1>
        <Input
          placeholder="Название плейлиста"
          value={playlistName}
          onChange={(e) => setPlaylistName(e.target.value)}
        />

        {isNameTooShort && (
          <div className={styles.error}>
            Длина названия плейлиста не может быть короче 5 символов
          </div>
        )}

        {nameError && <div className={styles.error}>{nameError}</div>}

        {error && <div className={styles.error}>{error}</div>}

        <Button
          type="normal"
          color="green"
          disabled={loading || isNameTooShort || isNameAlreadyExists}
          onClick={handleCreatePlaylist}
        >
          {loading ? "Создание..." : "Создать плейлист"}
        </Button>
      </Container>
    </>
  );
}
