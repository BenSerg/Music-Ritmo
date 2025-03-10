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
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [usernameError, setUsernameError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const validateFields = () => {
    if (!username || !password) {
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
    if (usernameError || passwordError || !username || !password) {
      setErrorMessage("Пожалуйста, исправьте все ошибки.");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
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

      if (
        response.status === 200 &&
        data["subsonic-response"]?.status === "ok" &&
        data["subsonic-response"]?.user
      ) {
        login(username, password);
        router.push("/");
      } else {
        setErrorMessage("Неверные данные для входа. Попробуйте снова.");
      }
    } catch (error) {
      setErrorMessage("Ошибка сети. Пожалуйста, попробуйте позже.");
      console.error("Network error:", error);
    } finally {
      setLoading(false);
    }
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
              validateUsername(e.target.value);
              validateFields();
            }}
          />
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
          {errorMessage && <div className={styles.error}>{errorMessage}</div>}

          <div className={styles.login__content_button}>
            <Button
              type="normal"
              color="green"
              disabled={Boolean(
                loading ||
                  usernameError ||
                  passwordError ||
                  !username ||
                  !password
              )}
              onClick={handleSubmit}
            >
              {loading ? "Загружается..." : "Войти"}
            </Button>
          </div>
        </Container>
        <Button
          type="transparent"
          color="green-text"
          onClick={() => {
            router.push("/registration");
          }}
        >
          регистрация
        </Button>
      </div>
    </div>
  );
}
