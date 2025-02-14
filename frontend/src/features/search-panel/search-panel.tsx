import React, { useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./search-panel.module.css";
import { Button } from "@/shared/button";
import { Artist } from "@/entities/artist";

interface Song {
  id: string;
  title: string;
  artist: string;
  album: string;
  genre: string;
  additionalData?: Record<string, unknown>;
}

interface Album {
  id: string;
  title: string;
  artist: string;
}

interface Artist {
  id: string;
  name: string;
}

interface SearchResult {
  id: string;
  title: string;
  artist: string;
  album: string;
  name: string;
  type: "song" | "album" | "artist";
}

export const SearchPanel = () => {
  const router = useRouter();
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searchClicked, setSearchClicked] = useState<boolean>(false);

  const handleSearch = async () => {
    setSearchClicked(true);
    if (query.length > 0) {
      try {
        const response = await fetch(
          `http://localhost:8000/rest/search3?query=${query}`
        );
        const data = await response.json();

        if (
          data["subsonic-response"] &&
          data["subsonic-response"].status === "ok"
        ) {
          const searchResult = [
            ...data["subsonic-response"].searchResult3.song.map(
              (song: Song) => ({
                ...song,
                type: "song",
              })
            ),
            ...data["subsonic-response"].searchResult3.album.map(
              (album: Album) => ({
                ...album,
                type: "album",
              })
            ),
            ...data["subsonic-response"].searchResult3.artist.map(
              (artist: Artist) => ({
                ...artist,
                type: "artist",
              })
            ),
          ];
          setResults(searchResult);
        } else {
          setResults([]);
        }
      } catch (error) {
        console.error("Ошибка при запросе:", error);
        setResults([]);
      }
    } else {
      setResults([]);
    }
  };

  const handleSelectResult = (result: SearchResult) => {
    if (result.type === "song") {
      router.push(`/track/${result.id}`);
    } else if (result.type === "album") {
      router.push(`/album/${result.id}`);
    } else if (result.type === "artist") {
      router.push(`/artist/${result.id}`);
    }

    setQuery(result.title);
    setResults([]);
    setSearchClicked(false);
  };

  const handleShowAllResults = () => {
    router.push(`/search?query=${encodeURIComponent(query)}`);
  };

  return (
    <div className={styles.search}>
      <input
        className={styles.search__input}
        placeholder="Поиск"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <i
        className={`fa-solid fa-magnifying-glass ${styles.search__icon}`}
        onClick={handleSearch}
      />

      {results.length > 0 ? (
        <div className={styles.search__results}>
          {results.slice(0, 10).map((result) => (
            <div
              key={`${result.id}-${result.type}`}
              className={styles.search__result}
              onClick={() => handleSelectResult(result)}
            >
              {result.type === "song" && (
                <>
                  <div className={styles.search__resultSong}>
                    {result.title}
                  </div>
                  <div className={styles.search__resultSongArtist}>
                    {result.artist}
                  </div>
                </>
              )}
              {result.type === "album" && (
                <div className={styles.search__resultAlbum}>
                  Альбом {result.album}
                </div>
              )}
              {result.type === "artist" && (
                <div className={styles.search__resultArtist}>
                  <div className={styles.search__resultArtistName}>
                    Исполнитель {result.name}
                  </div>
                </div>
              )}
            </div>
          ))}
          {results.length > 10 && (
            <div>
              <Button
                type="normal"
                color="green"
                disabled={false}
                onClick={handleShowAllResults}
              >
                Показать все результаты
              </Button>
            </div>
          )}
        </div>
      ) : searchClicked && results.length === 0 ? (
        <div className={styles.search__no_results}>Ничего не найдено</div>
      ) : null}
    </div>
  );
};
