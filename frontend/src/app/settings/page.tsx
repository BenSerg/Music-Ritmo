"use client";

import { useState, useEffect } from "react";
import { Button } from "@/shared/button";
import { Input } from "@/shared/input";
import { Container } from "@/shared/container";
import { useAuth } from "@/app/auth-context";
import Image from "next/image";
import styles from "./settings.module.css";

export default function Settings() {
  const { user, password, login } = useAuth();
  const [newUsername, setNewUsername] = useState<string>(user || "");
  const [newPassword, setNewPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [, setErrorMessage] = useState<string>("");
  const [isUsernameUnique] = useState<boolean>(true);
  const [avatar, setAvatar] = useState<string | null>(null);

  const updateUsername = async () => {
    if (!newUsername) {
      setErrorMessage("Пожалуйста, введите новый логин.");
      return;
    }

    if (!isUsernameUnique) {
      setErrorMessage("Этот логин уже занят.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage("Пароли не совпадают.");
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/rest/updateUser?username=${user}&u=${user}&p=${password}&newUsername=${newUsername}`,
        {
          method: "GET",
        }
      );

      const data = await response.json();
      if (data["subsonic-response"]?.status === "ok") {
        setErrorMessage("");
        setNewPassword("");
        setConfirmPassword("");

        login(newUsername, newPassword);
      } else {
        setErrorMessage("Ошибка при изменении логина.");
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(`Ошибка сети: ${err.message}`);
      } else {
        setErrorMessage("Неизвестная ошибка.");
      }
    }
  };

  const changePassword = async () => {
    if (newPassword !== confirmPassword) {
      setErrorMessage("Пароли не совпадают.");
      return;
    }

    if (!newPassword || !confirmPassword) {
      setErrorMessage("Пожалуйста, введите новый пароль.");
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/rest/changePassword?username=${user}&u=${user}&p=${password}&password=${newPassword}`,
        {
          method: "GET",
        }
      );

      const data = await response.json();
      if (data["subsonic-response"]?.status === "ok") {
        setErrorMessage("");
        setNewPassword("");
        setConfirmPassword("");
      } else {
        setErrorMessage("Ошибка при изменении пароля.");
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(`Ошибка сети: ${err.message}`);
      } else {
        setErrorMessage("Неизвестная ошибка.");
      }
    }
  };

  const fetchAvatar = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/rest/getAvatar?username=${user}&u=${user}&p=${password}`
      );

      if (response.ok) {
        const contentType = response.headers.get("Content-Type");

        if (contentType && contentType.includes("image")) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          setAvatar(url);
        } else {
          const data = await response.json();
          setAvatar(data.avatarUrl);
        }
      } else {
        console.error("Не удалось загрузить аватар");
      }
    } catch (error) {
      console.error("Ошибка при получении аватара:", error);
    }
  };

  const generateAvatar = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/specific/generateAvatar?u=${user}&p=${password}`,
        {
          method: "GET",
        }
      );

      if (response.ok) {
        const contentType = response.headers.get("Content-Type");

        if (contentType && contentType.includes("image")) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          setAvatar(url);
        } else {
          const data = await response.json();
          setAvatar(data.avatarUrl);
        }
      } else {
        console.error("Не удалось сгенерировать новый аватар");
      }
    } catch (error) {
      console.error("Ошибка при генерации аватара:", error);
    }
  };

  useEffect(() => {
    fetchAvatar();
  }, [user, password]);

  return (
    <div className={styles.settings}>
      <div className={styles.settings__avatar}>
        <h1 className={styles.settings__avatar__name}>{user}</h1>

        {avatar ? (
          <Image
            src={avatar}
            alt="User Avatar"
            width={300}
            height={300}
            className={styles.settings__avatar__image}
          />
        ) : (
          <Image
            src="/images/logo.svg"
            alt="User Avatar"
            width={300}
            height={300}
            className={styles.settings__avatar__image}
          />
        )}

        <Button
          type="normal"
          color="white"
          disabled={false}
          onClick={generateAvatar}
        >
          Сменить аватар
        </Button>
      </div>
      <div className={styles.settings__content}>
        <Container
          style={{ height: "45vh", width: "30vw" }}
          direction="column"
          arrow={true}
          link_arrow="/"
        >
          <h2 className={styles.registration__content__title}>Смена логина</h2>
          <Input
            type="text"
            placeholder="введите новый логин"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
          />
          {!isUsernameUnique && (
            <div className={styles.errorMessage}>Этот логин уже занят.</div>
          )}
          <Input
            type="password"
            placeholder="введите новый пароль"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <Input
            type="password"
            placeholder="подтвердите новый пароль"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          {newPassword !== confirmPassword && (
            <div className={styles.errorMessage}>Пароли не совпадают.</div>
          )}
          {(!newUsername || !newPassword || !confirmPassword) && (
            <div className={styles.errorMessage}>
              Пожалуйста, заполните все поля.
            </div>
          )}
          <div className={styles.registration__content_button}>
            <Button
              type="normal"
              color="green"
              disabled={false}
              onClick={updateUsername}
            >
              Сохранить изменения логина
            </Button>
            <Button
              type="normal"
              color="green"
              disabled={false}
              onClick={changePassword}
            >
              Сохранить изменения пароля
            </Button>
          </div>
        </Container>
      </div>
    </div>
  );
}
