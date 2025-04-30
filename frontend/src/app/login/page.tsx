"use client";

import { useRouter } from "next/navigation";
import React, { useState, useEffect } from "react";
import { Button } from "@/shared/button";
import { Input } from "@/shared/input";
import { Container } from "@/shared/container";
import { Logo } from "@/shared/logo";
import styles from "./login.module.css";
import { useAuth } from "@/app/auth-context";

export default function Login() {
  const router = useRouter();
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [serverError, setServerError] = useState("");
  const [usernameError, setUsernameError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const translations: { [key: string]: string } = {
    "Wrong username or password": "Неверно введенный логин или пароль",
    "User not found": "Пользователь не найден",
    "Invalid password": "Неверный пароль",
  };

  const translateError = (message: string) => {
    return translations[message] || "Ошибка входа";
  };

  const validateFields = () => {
    if (!username || !password) {
      setErrorMessage("Пожалуйста, заполните все поля.");
    } else {
      setErrorMessage("");
    }
  };

  useEffect(() => {
    validateFields();
  }, [username, password]);

  const handleSubmit = async () => {
    if (usernameError || passwordError || !username || !password) {
      setErrorMessage("Пожалуйста, исправьте все ошибки.");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    setServerError("");

    const response = await fetch(
      `http://localhost:8000/rest/getUser?username=${username}&u=${username}&p=${password}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      const errorText = translateError(data.detail || "Ошибка входа");
      setServerError(errorText);
      return;
    }

    if (data["subsonic-response"]?.status !== "ok") {
      const errorText = translateError(
        data["subsonic-response"]?.error?.message || "Ошибка входа"
      );
      setServerError(errorText);
      return;
    }

    if (!data["subsonic-response"]?.user) {
      setServerError("Неверные данные для входа. Попробуйте снова.");
      return;
    }

    login(username, password);
    router.push("/");
  };

  return (
    <div className={styles.login}>
      <div className={styles.login__logo}>
        <Logo type="big" />
      </div>
      <div className={styles.login__content}>
        <Container style={{ height: "35vh", width: "28vw" }} direction="column">
          <h2 className={styles.login__content__title}>Вход</h2>
          <Input
            type="text"
            placeholder="введите логин"
            value={username}
            onChange={(e) => {
              setUsername(e.target.value);
              setUsernameError(
                e.target.value.length < 5 || e.target.value.length > 64
                  ? "Логин должен быть от 5 до 64 символов."
                  : ""
              );
            }}
          />
          {usernameError && <div className={styles.error}>{usernameError}</div>}

          <Input
            type="password"
            placeholder="введите пароль"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setPasswordError(
                e.target.value.length < 5 || e.target.value.length > 64
                  ? "Пароль должен быть от 5 до 64 символов."
                  : ""
              );
            }}
          />
          {passwordError && <div className={styles.error}>{passwordError}</div>}

          {errorMessage && <div className={styles.error}>{errorMessage}</div>}

          {serverError && <div className={styles.error}>{serverError}</div>}

          <div className={styles.login__content_button}>
            <Button
              type="normal"
              color="green"
              disabled={
                !username ||
                !password ||
                Boolean(errorMessage) ||
                Boolean(passwordError)
              }
              onClick={handleSubmit}
            >
              Войти
            </Button>
          </div>
        </Container>
        <Button
          type="transparent"
          color="green-text"
          testid="go-to-registration"
          onClick={() => router.push("/registration")}
        >
          регистрация
        </Button>
      </div>
    </div>
  );
}
