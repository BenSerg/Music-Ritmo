"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/widgets/header";
import { SearchPanel } from "@/features/search-panel";
import { Button } from "@/shared/button";
import { Playlist } from "@/entities/playlist";
import styles from "./page.module.css";

interface Genre {
  songCount: number;
  albumCount: number;
  value: string;
}

interface GenresResponse {
  "subsonic-response": {
    status: string;
    version: string;
    type: string;
    serverVersion: string;
    openSubsonic: boolean;
    genres: {
      "genre": Genre[];
    };
  };
}

const GenreList = () => {
  const [responseData, setResponseData] = useState<GenresResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await fetch("http://localhost:8000/rest/getGenres");

        if (!response.ok) {
          throw new Error("Не удалось получить данные с сервера");
        }

        const data: GenresResponse = await response.json();
        setResponseData(data);
      } catch (error) {
        setError(error instanceof Error ? error.message : "Неизвестная ошибка");
      } finally {
        setLoading(false);
      }
    };

    fetchGenres();
  }, []);

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (error) {
    return <div>Ошибка: {error}</div>;
  }

  const genres = responseData?.["subsonic-response"]?.genres?.["genre"];

  return (
    <>
      <Header />
      <SearchPanel />
      <div className={styles.home_playlists}>
        {genres && genres.length > 0 ? (
          genres.map((genre, index) => (
            <Playlist
              key={index}
              name={genre.value}
              link={`/genre/${genre.value}`}
              showDelete={false}
            />
          ))
        ) : (
          <p>Нет доступных жанров</p>
        )}
      </div>

      <div className={styles.home_button}>
        <Button
          type="normal"
          color="green"
          disabled={false}
          onClick={() => {
            router.push("/media");
          }}
        >
          медиатека
        </Button>
      </div>
    </>
  );
};

export default GenreList;
