import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runWideSearchTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("http://localhost:3000/login");
  await page.type('input[placeholder="введите логин"]', "admin");
  await page.type('input[placeholder="введите пароль"]', "admin");

  const loginButton = await page.waitForSelector("button", { visible: true });
  if (loginButton) {
    await loginButton.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });
  } else {
    throw new Error("Кнопка входа не найдена");
  }

  const mediaLibraryButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((b) => b.textContent.includes("медиатека"));
  });

  if (mediaLibraryButton) {
    await mediaLibraryButton.click();
  } else {
    throw new Error("Кнопка 'медиатека' не найдена");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });

  const scanLibraryButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((b) =>
      b.textContent.includes("Запустить сканирование")
    );
  });

  if (scanLibraryButton) {
    await scanLibraryButton.click();
  } else {
    throw new Error("Кнопка 'Запустить сканирование' не найдена");
  }

  await delay(1000);

  const scanResultText = await page.evaluate(() => {
    const el = document.querySelector('div[class*="media_message"]');
    return el ? el.textContent.trim() : null;
  });

  if (scanResultText !== "Сканирование завершено успешно!") {
    throw new Error(
      `Неверное сообщение после сканирования: "${scanResultText}"`
    );
  }

  console.log("11 тест выполнен успешно, сканирование медиатеки");

  await browser.close();
};

runWideSearchTest().catch(console.error);
