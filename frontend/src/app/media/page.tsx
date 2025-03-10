"use client";

import { Container } from "@/shared/container";
import { Button } from "@/shared/button";
import React, { useState } from "react";
import styles from "./media.module.css";

export default function Media() {
  const [scanStatus, setScanStatus] = useState("");
  const [scanning, setScanning] = useState(false);

  const startScan = async () => {
    try {
      const response = await fetch("http://localhost:8000/rest/startScan", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (response.ok && data["subsonic-response"].status === "ok") {
        setScanStatus("Сканирование запущено");
        setScanning(true);
        checkScanStatus();
      } else {
        setScanStatus("Ошибка при запуске сканирования");
      }
    } catch (error) {
      console.error("Error during scan initiation:", error);
      setScanStatus("Ошибка при запуске сканирования");
    }
  };

  const checkScanStatus = async () => {
    try {
      const statusResponse = await fetch(
        "http://localhost:8000/rest/getScanStatus",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const statusData = await statusResponse.json();

      if (
        statusResponse.ok &&
        statusData["subsonic-response"].status === "ok"
      ) {
        const scanStatusData = statusData["subsonic-response"].scanStatus;

        if (scanStatusData.scanning) {
          setScanStatus(
            `Сканирование в процессе: найдено ${scanStatusData.count} элементов`
          );
          setTimeout(checkScanStatus, 50);
        } else {
          setScanStatus("Сканирование завершено успешно!");
          setScanning(false);
        }
      } else {
        setScanStatus("Ошибка при получении статуса сканирования");
      }
    } catch (error) {
      console.error("Error while checking scan status:", error);
      setScanStatus("Ошибка при получении статуса сканирования");
    }
  };

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
        link_arrow="/"
      >
        <h1>Медиатека</h1>

        <div style={{ display: "flex", justifyContent: "center" }}>
          <Button
            type="normal"
            color="green"
            onClick={startScan}
            disabled={scanning}
          >
            {scanning ? "Сканирование..." : "Запустить сканирование"}
          </Button>
        </div>

        {scanStatus && <div className={styles.message}>{scanStatus}</div>}
      </Container>
    </>
  );
}
