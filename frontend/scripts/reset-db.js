import path from "path";
import sqlite3 from "sqlite3";
import { open } from "sqlite";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dbPath = path.resolve(__dirname, "../../database.db");

const resetDatabase = async () => {
  const db = await open({
    filename: dbPath,
    driver: sqlite3.Database,
  });

  try {
    await db.run("DELETE FROM CustomTags;");
    await db.run("DELETE FROM Favourite_Tracks;");
    await db.run("DELETE FROM Playlists;");
    await db.run("DELETE FROM Users WHERE id != 1;");
  } catch (error) {
    console.error(error);
    process.exit(1);
  } finally {
    await db.close();
  }
};

resetDatabase();
