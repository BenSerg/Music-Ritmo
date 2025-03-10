"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Button } from "@/shared/button";
import { Input } from "@/shared/input";
import { Container } from "@/shared/container";
import { useRouter } from "next/navigation";
import { Logo } from "@/shared/logo";
import { useAuth } from "@/app/auth-context";
import styles from "./registration.module.css";

export default function Registration() {
  const router = useRouter();
  const { login } = useAuth();
  const [user, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [, setErrorMessage] = useState("");
  const [, setSuccessMessage] = useState("");
  const [usernameError, setUsernameError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [isUsernameUnique, setIsUsernameUnique] = useState<boolean>(true);

  const checkUsernameUniqueness = useCallback(
    async (username: string) => {
      const response = await fetch(
        `http://localhost:8000/rest/getUsers?username=admin&u=admin&p=admin`
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

  const validateFields = () => {
    if (!user || !password) {
      setErrorMessage("Пожалуйста, заполните все поля.");
    } else {
      setErrorMessage("");
    }
  };

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

  useEffect(() => {
    validateFields();
  }, [validateFields]);

  const handleSubmit = async () => {
    setLoading(true);
    setErrorMessage("");
    setSuccessMessage("");

    const response = await fetch(
      `http://localhost:8000/rest/createUser?username=${user}&password=${password}&email=defemail@gmail.com}`,
      {
        method: "GET",
      }
    );

    const data = await response.json();

    if (data["subsonic-response"]?.status === "ok") {
      setSuccessMessage("Вы успешно зарегистрированы!");

      login(user, password);

      setTimeout(() => {
        router.push("/");
      }, 2000);
    } else {
      setErrorMessage("Ошибка при регистрации. Попробуйте снова.");
    }
  };

  useEffect(() => {
    if (user) {
      checkUsernameUniqueness(user);
    }
  }, [user, checkUsernameUniqueness]);

  return (
    <div className={styles.registration}>
      <div className={styles.registration__logo}>
        <Logo type="big" />
      </div>
      <div className={styles.registration__content}>
        <Container
          style={{ height: "35vh", width: "28vw" }}
          direction="column"
          arrow={true}
          link_arrow="/login"
        >
          <h2 className={styles.registration__content__title}>Регистрация</h2>

          <Input
            type="text"
            placeholder="введите логин"
            value={user}
            onChange={(e) => {
              setUsername(e.target.value);
              validateUsername(e.target.value);
              validateFields();
            }}
          />
          {!isUsernameUnique && (
            <div className={styles.errorMessage}>Этот логин уже занят.</div>
          )}
          {usernameError && <div className={styles.error}>{usernameError}</div>}

          <Input
            type="password"
            placeholder="введите пароль"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              validatePassword(e.target.value);
              validateFields();
            }}
          />
          {passwordError && <div className={styles.error}>{passwordError}</div>}

          <div className={styles.registration__content_button}>
            <Button
              type="normal"
              color="green"
              disabled={Boolean(
                loading || usernameError || passwordError || !user || !password
              )}
              onClick={handleSubmit}
            >
              {loading ? "Загружается..." : "Зарегистрироваться"}
            </Button>
          </div>
        </Container>
      </div>
    </div>
  );
}
