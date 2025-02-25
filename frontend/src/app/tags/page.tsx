"use client";

import React, { useState } from "react";
import { Container } from "@/shared/container";
import { Button } from "@/shared/button";
import styles from "./tags.module.css";

export default function Tags() {
  const [tags, setTags] = useState([
    { id: 1, tag: "Музыка", value: "20" },
    { id: 2, tag: "Спорт", value: "10" },
    { id: 3, tag: "Кино", value: "15" },
    { id: 4, tag: "Технологии", value: "30" },
  ]);

  const handleAddTag = () => {
    const newTag = {
      id: tags.length + 1,
      tag: "Новый тег",
      value: "0",
    };
    setTags([...tags, newTag]);
  };

  const handleTagChange = (id: number, field: string, value: string) => {
    setTags(
      tags.map((tag) => (tag.id === id ? { ...tag, [field]: value } : tag))
    );
  };

  const handleClearTags = () => {
    setTags([]);
  };

  const handleDeleteTag = (id: number) => {
    setTags(tags.filter((tag) => tag.id !== id));
  };

  return (
    <>
      <Container
        style={{
          height: "65vh",
          width: "60vw",
          margin: "auto",
          marginTop: "50px",
        }}
        direction="column"
        arrow={true}
        link_arrow="/track"
      >
        <h1>Теги</h1>
        <div className={styles.tags}>
          <table className={styles.tags_table}>
            <tbody>
              {tags.map((tag) => (
                <tr key={tag.id} className={styles.tagRow}>
                  <td>
                    <input
                      type="text"
                      value={tag.tag}
                      onChange={(e) =>
                        handleTagChange(tag.id, "tag", e.target.value)
                      }
                      className={styles.inputTag}
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={tag.value}
                      onChange={(e) =>
                        handleTagChange(tag.id, "value", e.target.value)
                      }
                      className={styles.inputValue}
                    />
                  </td>
                  <td
                    className={styles.deleteIconWrapper}
                    onClick={() => handleDeleteTag(tag.id)}
                  >
                    <i className={`fa-solid fa-xmark ${styles.deleteIcon}`}></i>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className={styles.tags_button}>
          <Button
            type="normal"
            color="green"
            disabled={false}
            onClick={handleAddTag}
          >
            добавить тег
          </Button>
          <Button
            type="normal"
            color="white"
            disabled={false}
            onClick={handleClearTags}
          >
            очистить все
          </Button>
          <Button type="normal" color="green" disabled={false}>
            сохранить
          </Button>
        </div>
      </Container>
    </>
  );
}
