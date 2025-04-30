import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  try {
    await page.goto("http://localhost:3000/login");
    await page.type('input[placeholder="введите логин"]', "admin");
    await page.type('input[placeholder="введите пароль"]', "admin");

    const loginButton = await findButtonByText(page, "Войти");
    await loginButton.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    await page.waitForSelector("i.fa-solid.fa-music");
    await page.click("i.fa-solid.fa-music");
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    const playlistName1 = "Плейлист1";
    await createPlaylist(page, playlistName1);
    await checkPlaylistExists(page, playlistName1);

    const createButton = await findButtonByText(page, "создать плейлист");
    await createButton.click();
    await page.waitForSelector('input[placeholder="Название плейлиста"]', {
      timeout: 5000,
    });
    await page.type('input[placeholder="Название плейлиста"]', playlistName1);

    const confirmButton = await findButtonByText(page, "Создать плейлист");
    await confirmButton.click();

    await page.waitForSelector('div[class*="error"]', { timeout: 5000 });
    const errorText = await page.evaluate(() => {
      const el = document.querySelector('div[class*="error"]');
      return el ? el.textContent.trim() : null;
    });

    if (errorText !== "Плейлист с таким названием уже существует") {
      throw new Error(`Неверное сообщение об ошибке: "${errorText}"`);
    }

    await page.click('input[placeholder="Название плейлиста"]', {
      clickCount: 3,
    });
    await page.keyboard.press("Backspace");

    const playlistName2 = "Плейлист2";
    await page.type('input[placeholder="Название плейлиста"]', playlistName2);
    await confirmButton.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    await checkBothPlaylistsExist(page, playlistName1, playlistName2);

    console.log("13 тест выполнен успешно, создание нового плейлиста");
  } catch (error) {
    console.error("Ошибка в тесте:", error);
  } finally {
    await delay(2000);
    await browser.close();
  }
};

async function createPlaylist(page, playlistName) {
  const createButton = await findButtonByText(page, "создать плейлист");
  await createButton.click();
  await page.waitForSelector('input[placeholder="Название плейлиста"]', {
    timeout: 5000,
  });
  await page.type('input[placeholder="Название плейлиста"]', playlistName);
  const confirmButton = await findButtonByText(page, "Создать плейлист");
  await confirmButton.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });
}

async function checkPlaylistExists(page, playlistName) {
  await page.waitForSelector('div[class*="playlist__name"]', { timeout: 5000 });
  const elements = await page.$$('div[class*="playlist__name"]');
  for (const el of elements) {
    const text = await page.evaluate((el) => el.textContent.trim(), el);
    if (text === playlistName) return;
  }
  throw new Error(`Плейлист "${playlistName}" не найден`);
}

async function checkBothPlaylistsExist(page, name1, name2) {
  await page.waitForSelector('div[class*="playlist__name"]', { timeout: 5000 });
  const elements = await page.$$('div[class*="playlist__name"]');
  let found1 = false;
  let found2 = false;
  for (const el of elements) {
    const text = await page.evaluate((el) => el.textContent.trim(), el);
    if (text === name1) found1 = true;
    if (text === name2) found2 = true;
  }
  if (!found1 || !found2) {
    throw new Error(
      `Не найдены плейлисты: ${!found1 ? name1 : ""} ${!found2 ? name2 : ""}`
    );
  }
}

async function findButtonByText(page, text) {
  const buttons = await page.$$("button");
  for (const btn of buttons) {
    const btnText = await page.evaluate(
      (el) => el.textContent.trim().toLowerCase(),
      btn
    );
    if (btnText.includes(text.toLowerCase())) return btn;
  }
  throw new Error(`Кнопка с текстом "${text}" не найдена`);
}

runTest().catch(console.error);
