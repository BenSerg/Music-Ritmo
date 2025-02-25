import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/app/auth-context";
import styles from "./user.module.css";

export const User = () => {
  const { user, password, logout } = useAuth();
  const [isMenuOpen, setMenuOpen] = useState(false);
  const [avatar, setAvatar] = useState<string | null>(null);

  const toggleMenu = () => {
    setMenuOpen((prevState) => !prevState);
  };

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
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
            console.log("Полученный ответ с бека:", data);
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

  return (
    <div className={styles.user}>
      <div className={styles.user__avatar} onClick={toggleMenu}>
        {avatar ? (
          <Image
            src={avatar}
            alt="User Avatar"
            width={40}
            height={40}
            className={styles.user__avatar__image}
          />
        ) : (
          <Image
            src="/images/logo.svg"
            alt="User Avatar"
            width={40}
            height={40}
            className={styles.user__avatar__image}
          />
        )}
        <span className={styles.user__avatar__name}>{user}</span>
      </div>

      {isMenuOpen && (
        <div className={styles.user__menu}>
          <ul className={styles.user__menu_list}>
            <li>
              <Link href="/settings" className={styles.user__menu_item}>
                Настройки
              </Link>
            </li>
            <li>
              <button className={styles.user__menu_item} onClick={handleLogout}>
                Выйти
              </button>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};
