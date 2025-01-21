"use client";

import { useRouter } from "next/navigation";
import { Container } from "@/shared/container";
import { Input } from "@/shared/input";
import { Button } from "@/shared/button";
import styles from "./create_playlist.module.css";

export default function CreatePlaylist() {
  const router = useRouter();

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

        <Input placeholder="Название плейлиста" />
        <Button
          type="normal"
          color="green"
          disabled={false}
          onClick={() => {
            router.push("/playlists");
          }}
        >
          создать плейлист
        </Button>
      </Container>
    </>
  );
}
