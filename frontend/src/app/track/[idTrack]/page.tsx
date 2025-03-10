"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Container } from "@/shared/container";
import { useAuth } from "@/app/auth-context";
import Link from "next/link";
import styles from "./track.module.css";

interface TrackData {
  title: string;
  artist: string;
  artistId: string;
  genre: string;
  coverArt?: string;
  starred: string;
}

interface PlaylistType {
  id: string;
  name: string;
  owner: string;
  public: boolean;
  created: string;
  changed: string;
  songCount: number;
  duration: number;
}

const Modal = ({
  onClose,
  trackId,
}: {
  onClose: () => void;
  trackId: number;
}) => {
  const [playlists, setPlaylists] = useState<PlaylistType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const { user, password } = useAuth();

  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const userLogin = "test_user";
        const response = await fetch(
          `http://localhost:8000/rest/getPlaylists?username=${userLogin}`
        );
        const data = await response.json();

        if (data["subsonic-response"].status === "ok") {
          const fetchedPlaylists = data["subsonic-response"].playlists.playlist;
          if (fetchedPlaylists.length === 0) {
            setError("У вас нет плейлистов");
          } else {
            setPlaylists(fetchedPlaylists);
            setError(null);
          }
        } else {
          setError("Не удалось загрузить плейлисты");
        }
      } catch {
        setError("Произошла ошибка при получении плейлистов");
      } finally {
        setLoading(false);
      }
    };

    fetchPlaylists();
  }, []);

  const addTrackToPlaylist = async (
    playlistId: string,
    playlistName: string
  ) => {
    try {
      const response = await fetch(
        `http://localhost:8000/rest/updatePlaylist?playlistId=${playlistId}&songIdToAdd=${trackId}&username=${user}&u=${user}&p=${password}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );
      const data = await response.json();
      console.log(data);

      if (data["subsonic-response"].status === "ok") {
        setSuccessMessage(`Трек успешно добавлен в плейлист "${playlistName}"`);
      } else {
        setError("Не удалось добавить трек в плейлист");
      }
    } catch (error) {
      console.error("Ошибка при добавлении трека в плейлист:", error);
      setError("Произошла ошибка при добавлении трека в плейлист");
    }
  };

  const colorOptions = ["#949E7B", "#B3BF7D", "#758934", "#A1BA65", "#405A01"];

  const getRandomColor = (colors: string[]): string => {
    const randomIndex = Math.floor(Math.random() * colors.length);
    return colors[randomIndex];
  };

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <div className={styles.modalHeader}>
          <h2>
            Выберите плейлист
            {successMessage && (
              <p className={styles.successMessage}>{successMessage}</p>
            )}
          </h2>

          <button onClick={onClose} className={styles.closeButton}>
            <i className="fa-solid fa-xmark"></i>
          </button>
        </div>
        <div className={styles.playlists}>
          {loading && <div>Загрузка плейлистов...</div>}
          {error && <div className={styles.message}>{error}</div>}
          {!loading &&
            !error &&
            playlists.length > 0 &&
            playlists.map((playlist) => (
              <div
                key={playlist.id}
                className={styles.playlistItem}
                style={{ backgroundColor: getRandomColor(colorOptions) }}
                onClick={() => addTrackToPlaylist(playlist.id, playlist.name)}
              >
                <div className={styles.playlistItem__name}>{playlist.name}</div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default function PlayedTrack() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [trackId, setTrackId] = useState<number>(0);
  const [coverArtUrl, setCoverArtUrl] = useState<string | null>(null);
  const { user, password } = useAuth();

  const toggleModal = () => {
    setIsModalOpen((prev) => !prev);
  };

  const [isPlaying, setIsPlaying] = useState(false);
  const [isFavourite, setIsFavourite] = useState(false);
  const [isRepeat, setIsRepeat] = useState(false);
  const [isShuffle, setIsShuffle] = useState(false);
  const [isRotateRight, setIsRotateRight] = useState(false);
  const [isRightLong, setIsRightLong] = useState(true);

  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string>("");
  const [trackData, setTrackData] = useState<TrackData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const pathname = usePathname();
  const router = useRouter();
  const totalTracks = 6;

  useEffect(() => {
    const idFromUrl = pathname?.split("/")[2];
    if (idFromUrl) {
      setTrackId(parseInt(idFromUrl));
    }
  }, [pathname]);

  useEffect(() => {
    const fetchTrack = async (id: number) => {
      try {
        const response = await fetch(
          `http://localhost:8000/rest/stream?id=${id}`
        );
        if (!response.ok) {
          throw new Error("Ошибка при получении трека");
        }
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);
      } catch (error) {
        console.error("Ошибка при загрузке трека:", error);
      }
    };

    const fetchTrackData = async (id: number) => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8000/rest/getSong?id=${id}`
        );
        if (!response.ok) {
          throw new Error("Ошибка при получении данных о треке");
        }
        const data = await response.json();

        const track = data?.["subsonic-response"]?.song;

        if (track) {
          setTrackData({
            title: track.title || "Неизвестное название",
            artist: track.artist || "Неизвестный автор",
            artistId: track.artistId || "Неизвестный id автора",
            genre: track.genre || "Неизвестный жанр",
            coverArt: track.coverArt || null,
            starred: track.starred || "",
          });

          setIsFavourite(!!track.starred);

          if (track.coverArt) {
            const coverArtResponse = await fetch(
              `http://localhost:8000/rest/getCoverArt?id=${track.coverArt}`
            );
            if (coverArtResponse.ok) {
              const imageBlob = await coverArtResponse.blob();
              const imageUrl = URL.createObjectURL(imageBlob);
              setCoverArtUrl(imageUrl);
            }
          }
        } else {
          setTrackData({
            title: "Неизвестное название",
            artist: "Неизвестный автор",
            artistId: "Неизвестный id автора",
            genre: "Неизвестный жанр",
            starred: "",
          });
          setIsFavourite(false);
        }
      } catch (error) {
        console.error("Error fetching track data:", error);
        setTrackData({
          title: "Неизвестное название",
          artist: "Неизвестный автор",
          artistId: "Неизвестный id автора",
          genre: "Неизвестный жанр",
          starred: "",
        });
        setIsFavourite(false);
      } finally {
        setIsLoading(false);
      }
    };

    if (trackId) {
      fetchTrack(trackId);
      fetchTrackData(trackId);
    }
  }, [trackId]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(
      2,
      "0"
    )}`;
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration);
    }
  };

  const handleFavouriteToggle = async () => {
    const action = isFavourite ? "unstar" : "star";
    const url = `http://localhost:8000/rest/${action}?id=${trackId}&username=${user}&u=${user}&p=${password}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      if (data["subsonic-response"].status === "ok") {
        setIsFavourite(!isFavourite);
        setTrackData((prev) =>
          prev
            ? { ...prev, starred: !isFavourite ? new Date().toISOString() : "" }
            : null
        );
      } else {
        alert("Ошибка при изменении статуса избранного");
      }
    } catch (error) {
      console.error("Ошибка при изменении статуса избранного:", error);
      alert("Произошла ошибка при изменении статуса избранного");
    }
  };

  const handleForward = () => {
    switch (true) {
      case isRepeat:
        if (trackId < totalTracks) {
          setTrackId(trackId + 1);
          router.push(`/track/${trackId + 1}`);
        } else {
          setTrackId(1);
          router.push(`/track/1`);
        }
        break;

      case isShuffle:
        const randomTrackId = Math.floor(Math.random() * totalTracks) + 1;
        setTrackId(randomTrackId);
        router.push(`/track/${randomTrackId}`);
        break;

      case isRotateRight:
        setTrackId(trackId);
        break;

      case isRightLong:
        if (trackId < totalTracks) {
          setTrackId(trackId + 1);
          router.push(`/track/${trackId + 1}`);
        }
        break;
    }
  };

  const handleBackward = () => {
    switch (true) {
      case isRepeat:
        if (trackId > 1) {
          setTrackId(trackId - 1);
          router.push(`/track/${trackId - 1}`);
        } else {
          setTrackId(totalTracks);
          router.push(`/track/${totalTracks}`);
        }
        break;

      case isShuffle:
        const randomTrackId = Math.floor(Math.random() * totalTracks) + 1;
        setTrackId(randomTrackId);
        router.push(`/track/${randomTrackId}`);
        break;

      case isRotateRight:
        setTrackId(trackId);
        break;

      case isRightLong:
        if (trackId > 1) {
          setTrackId(trackId - 1);
          router.push(`/track/${trackId - 1}`);
        }
        break;
    }
  };

  const handleChangeMode = () => {
    let newRepeat = isRepeat;
    let newShuffle = isShuffle;
    let newRotateRight = isRotateRight;
    let newRightLong = isRightLong;

    if (isRepeat) {
      newRepeat = false;
      newShuffle = true;
    } else if (isShuffle) {
      newShuffle = false;
      newRotateRight = true;
    } else if (isRotateRight) {
      newRotateRight = false;
      newRightLong = true;
    } else if (isRightLong) {
      newRightLong = false;
      newRepeat = true;
    }

    setIsRepeat(newRepeat);
    setIsShuffle(newShuffle);
    setIsRotateRight(newRotateRight);
    setIsRightLong(newRightLong);

    localStorage.setItem(
      "playbackModes",
      JSON.stringify({
        isRepeat: newRepeat,
        isShuffle: newShuffle,
        isRotateRight: newRotateRight,
        isRightLong: newRightLong,
      })
    );
  };

  useEffect(() => {
    const savedModes = localStorage.getItem("playbackModes");
    if (savedModes) {
      const parsedModes = JSON.parse(savedModes);
      setIsRepeat(parsedModes.isRepeat);
      setIsShuffle(parsedModes.isShuffle);
      setIsRotateRight(parsedModes.isRotateRight);
      setIsRightLong(parsedModes.isRightLong);
    }
  }, []);

  if (isLoading) {
    return <div>Загрузка...</div>;
  }

  return (
    <div>
      <Container
        style={{
          height: "70vh",
          width: "30vw",
          margin: "auto",
          marginTop: "70px",
        }}
        arrow={true}
        link_arrow={"/"}
        direction="column"
      >
        <div
          className={styles.track__avatar}
          style={{
            backgroundImage: coverArtUrl ? `url(${coverArtUrl})` : "none",
            backgroundColor: coverArtUrl ? "transparent" : "gray",
            backgroundSize: "cover",
          }}
        ></div>

        <div className={styles.track__info}>
          <h2 className={styles.track__name}>
            {trackData ? trackData.title : "Загрузка названия трека..."}
          </h2>
          <Link
            href={`/artist/${trackData?.artistId}`}
            className={styles.track__artist}
          >
            <p className={styles.track__artist}>
              {trackData ? trackData.artist : "Загрузка автора..."}
            </p>
          </Link>

          <Link href="/track-info">
            <i className={`fa-solid fa-info ${styles.track__infoIcon}`}></i>
          </Link>
        </div>

        <div className={styles.track__progress}>
          <span className={styles.track__currentTime}>
            {formatTime(currentTime)}
          </span>
          <input
            type="range"
            min="0"
            max={duration || 0}
            value={currentTime}
            onChange={(e) => {
              if (audioRef.current) {
                audioRef.current.currentTime = Number(e.target.value);
                setCurrentTime(Number(e.target.value));
              }
            }}
            className={styles.track__range}
          />
          <span className={styles.track__duration}>{formatTime(duration)}</span>
        </div>

        <div className={styles.track__controls}>
          <div onClick={handleChangeMode}>
            {isRepeat ? (
              <i
                className={`fa-solid fa-repeat ${styles.track__controlIcon}`}
              ></i>
            ) : isShuffle ? (
              <i
                className={`fa-solid fa-shuffle ${styles.track__controlIcon}`}
              ></i>
            ) : isRotateRight ? (
              <i
                className={`fa-solid fa-arrow-rotate-right ${styles.track__controlIcon}`}
              ></i>
            ) : isRightLong ? (
              <i
                className={`fa-solid fa-arrow-right-long ${styles.track__controlIcon}`}
              ></i>
            ) : null}
          </div>

          <i
            className={`fa-solid fa-backward ${styles.track__controlIcon}`}
            onClick={handleBackward}
          />

          <div className={styles.track__playPause} onClick={handlePlayPause}>
            {isPlaying ? (
              <i
                className={`fa-regular fa-circle-pause ${styles.track__controlIcon}`}
              ></i>
            ) : (
              <i
                className={`fa-regular fa-circle-play ${styles.track__controlIcon}`}
              ></i>
            )}
          </div>

          <i
            className={`fa-solid fa-forward ${styles.track__controlIcon}`}
            onClick={handleForward}
          />

          <div onClick={handleFavouriteToggle}>
            {isFavourite ? (
              <i
                className={`fa-solid fa-star ${styles.track__controlIcon}`}
              ></i>
            ) : (
              <i
                className={`fa-regular fa-star ${styles.track__controlIcon}`}
              ></i>
            )}
          </div>
        </div>

        <div className={styles.track__controls}>
          <i
            className={`fa-solid fa-share ${styles.track__controlIcon}`}
            onClick={toggleModal}
          ></i>
          <i className={`fa-solid fa-list-ul ${styles.track__controlIcon}`}></i>
        </div>
      </Container>

      {audioUrl && (
        <audio
          ref={audioRef}
          src={audioUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={() => {
            if (audioRef.current) {
              setDuration(audioRef.current.duration);
            }
          }}
          onEnded={() => {
            if (isRepeat) {
              handleForward();
            } else {
              setIsPlaying(false);
            }
          }}
        />
      )}

      {isModalOpen && <Modal onClose={toggleModal} trackId={trackId} />}
    </div>
  );
}
