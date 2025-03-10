"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Button } from "@/shared/button";
import { Input } from "@/shared/input";
import { Container } from "@/shared/container";
import { useAuth } from "@/app/auth-context";
import Image from "next/image";
import styles from "./settings.module.css";

export default function Settings() {
  const { user, password, updateUser } = useAuth();
  const [newUsername, setNewUsername] = useState<string>(user || "");
  const [newPassword, setNewPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [, setErrorMessage] = useState<string>("");
  const [avatar, setAvatar] = useState<string | null>(null);
  const [isUsernameUnique, setIsUsernameUnique] = useState<boolean>(true);
  const [usernameError, setUsernameError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const checkUsernameUniqueness = useCallback(
    async (username: string) => {
      const response = await fetch(
        `http://localhost:8000/rest/getUsers?username=${user}&u=${user}&p=${password}`
      );
      const data = await response.json();

      if (data["subsonic-response"]?.status === "ok") {
        const existingUsernames = data["subsonic-response"].users.user.map(
          (user: { username: string }) => user.username
        );
        setIsUsernameUnique(!existingUsernames.includes(username));
      } else {
        setErrorMessage("Ошибка при проверке пользователей.");
      }
    },
    [user, password]
  );

  const updateUsername = async () => {
    if (!newUsername) {
      setErrorMessage("Пожалуйста, введите новый логин.");
      return;
    }

    if (!isUsernameUnique) {
      setErrorMessage("Этот логин уже занят.");
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
        updateUser(newUsername, password || "");
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
        updateUser(user || "", newPassword);
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

  const handleSaveChanges = async () => {
    setErrorMessage("");

    if (newUsername !== user) {
      await updateUsername();
    }

    if (newPassword && newPassword === confirmPassword) {
      await changePassword();
    }
  };

  useEffect(() => {
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

    fetchAvatar();
  }, [user, password]);

  const validateUsername = (value: string) => {
    if (!value) {
      setUsernameError("Пожалуйста, введите логин.");
    } else if (value.length < 5 || value.length > 64) {
      setUsernameError("Логин должен быть от 5 до 64 символов.");
    } else {
      setUsernameError("");
    }
  };

  const validatePassword = (value: string) => {
    if (!value) {
      setPasswordError("Пожалуйста, введите пароль.");
    } else if (value.length < 5 || value.length > 64) {
      setPasswordError("Пароль должен быть от 5 до 64 символов.");
    } else {
      setPasswordError("");
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
    if (newUsername) {
      checkUsernameUniqueness(newUsername);
    }
  }, [newUsername, checkUsernameUniqueness]);

  const isSaveButtonDisabled = Boolean(
    !newUsername ||
      (newUsername === user && !newPassword) ||
      newPassword !== confirmPassword ||
      usernameError ||
      passwordError
  );

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
        <Button type="normal" color="green" onClick={generateAvatar}>
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
          <h2 className={styles.registration__content__title}>
            Смена логина и пароля
          </h2>
          <Input
            type="text"
            placeholder="введите новый логин"
            value={newUsername}
            onChange={(e) => {
              setNewUsername(e.target.value);
              validateUsername(e.target.value);
            }}
          />
          {!isUsernameUnique && (
            <div className={styles.errorMessage}>Этот логин уже занят.</div>
          )}
          {usernameError && <div className={styles.error}>{usernameError}</div>}
          <Input
            type="password"
            placeholder="введите новый пароль"
            value={newPassword}
            onChange={(e) => {
              setNewPassword(e.target.value);
              validatePassword(e.target.value);
            }}
          />
          {passwordError && <div className={styles.error}>{passwordError}</div>}
          <Input
            type="password"
            placeholder="подтвердите новый пароль"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          {newPassword !== confirmPassword && (
            <div className={styles.errorMessage}>Пароли не совпадают.</div>
          )}
          <div className={styles.registration__content_button}>
            <Button
              type="normal"
              color="green"
              disabled={isSaveButtonDisabled}
              onClick={handleSaveChanges}
            >
              Сохранить изменения
            </Button>
          </div>
        </Container>
      </div>
    </div>
  );
}
