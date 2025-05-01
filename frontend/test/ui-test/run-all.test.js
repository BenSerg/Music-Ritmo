import { readdir } from "fs/promises";
import path from "path";
import { execSync } from "child_process";

const testDir = path.resolve("test/ui-test");

const runTest = async (file) => {
  console.log(`\nЗапуск теста: ${file}`);
  try {
    await import(path.join(testDir, file));
    console.log(`Тест ${file} прошел успешно!`);

    execSync("npm run reset-db");
  } catch (err) {
    console.error(`Ошибка в тесте ${file}:`, err);
    process.exit(1);
  }
};

const run = async () => {
  const files = (await readdir(testDir))
    .filter((f) => f.endsWith(".test.js"))
    .sort();

  for (const file of files) {
    await runTest(file);
  }

  console.log("\nВсе тесты успешно завершены");
  process.exit(0);
};

run();
