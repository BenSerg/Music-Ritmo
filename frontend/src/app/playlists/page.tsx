"use client";

import { useRouter } from "next/navigation";
import { Container } from "@/shared/container";
import { Playlist } from "@/entities/playlist";
import { Button } from "@/shared/button";
import styles from "./playlists.module.css";

export default function Playlists() {
  const router = useRouter();

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
        <h1 className={styles.playlists__title}>Ваши плейлисты</h1>
        <div className={styles.playlists}>
          <Playlist name="Ммтао1" link="/здфндшые1" />
          <Playlist name="Ммтао2" link="/здфндшые2" />
          <Playlist name="Ммтао3" link="/здфндшые3" />
          <Playlist name="Ммтао4" link="/здфндшые4" />
          <Playlist name="Ммтао5" link="/здфндшые5" />
          <Playlist name="Ммтао1" link="/здфндшые1" />
          <Playlist name="Ммтао2" link="/здфндшые2" />
          <Playlist name="Ммтао3" link="/здфндшые3" />
          <Playlist name="Ммтао4" link="/здфндшые4" />
          <Playlist name="Ммтао5" link="/здфндшые5" />
          <Playlist name="Ммтао1" link="/здфндшые1" />
          <Playlist name="Ммтао2" link="/здфндшые2" />
          <Playlist name="Ммтао1" link="/здфндшые1" />
          <Playlist name="Ммтао2" link="/здфндшые2" />
          <Playlist name="Ммтао3" link="/здфндшые3" />
          <Playlist name="Ммтао4" link="/здфндшые4" />
          <Playlist name="Ммтао5" link="/здфндшые5" />
          <Playlist name="Ммтао1" link="/здфндшые1" />
          <Playlist name="Ммтао2" link="/здфндшые2" />
        </div>
      </Container>

      <div className={styles.playlists_button}>
        <Button
          type="normal"
          color="green"
          disabled={false}
          onClick={() => {
            router.push("/create-playlist");
          }}
        >
          создать плейлист
        </Button>
      </div>
    </>
  );
}
