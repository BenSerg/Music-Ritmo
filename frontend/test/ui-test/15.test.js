import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runCreatePlaylistLimitTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  try {
    await page.goto("http://localhost:3000/login");
    await page.type('input[placeholder="введите логин"]', "admin");
    await page.type('input[placeholder="введите пароль"]', "admin");

    const loginBtn = await findButtonByText(page, "Войти");
    await loginBtn.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    await page.waitForSelector("i.fa-solid.fa-music");
    await page.click("i.fa-solid.fa-music");
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    for (let index = 1; index <= 30; index++) {
      const playlistTitle = `Плейлист${index}`;
      try {
        await checkPlaylistExists(page, playlistTitle);
        continue;
      } catch {
        await createPlaylist(page, playlistTitle);
      }
      await delay(300);
    }

    const createBtn = await findButtonByText(page, "создать плейлист");
    const isDisabled = await page.evaluate((btn) => btn.disabled, createBtn);

    if (!isDisabled) {
      throw new Error(
        "Кнопка 'Создать плейлист' не заблокирована после создания 30 плейлистов"
      );
    }

    await page.waitForSelector('div[class*="message_more"]', { timeout: 5000 });
    const errorText = await page.evaluate(() => {
      const element = document.querySelector('div[class*="message_more"]');
      return element ? element.textContent.trim() : null;
    });

    if (errorText !== "Слишком много плейлистов") {
      throw new Error(`Некорректное сообщение об ошибке: "${errorText}"`);
    }

    console.log(
      "15 тест выполнен успешно, ошибка при создании 31-го плейлиста"
    );
  } catch (error) {
    throw new Error(error.message);
  } finally {
    await delay(2000);
    await browser.close();
  }
};

async function createPlaylist(page, playlistTitle) {
  const createBtn = await findButtonByText(page, "создать плейлист");
  await createBtn.click();

  await page.waitForSelector('input[placeholder="Название плейлиста"]', {
    timeout: 5000,
  });
  await page.type('input[placeholder="Название плейлиста"]', playlistTitle);

  const confirmBtn = await findButtonByText(page, "Создать плейлист");
  await confirmBtn.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });
}

async function checkPlaylistExists(page, playlistTitle) {
  await page.waitForSelector('div[class*="playlist__name"]', { timeout: 5000 });
  const playlistElements = await page.$$('div[class*="playlist__name"]');

  for (const element of playlistElements) {
    const text = await page.evaluate((el) => el.textContent.trim(), element);
    if (text === playlistTitle) return;
  }

  throw new Error(`Плейлист "${playlistTitle}" не найден`);
}

async function findButtonByText(page, buttonText) {
  const buttons = await page.$$("button");
  for (const btn of buttons) {
    const text = await page.evaluate(
      (el) => el.textContent.trim().toLowerCase(),
      btn
    );
    if (text.includes(buttonText.toLowerCase())) {
      return btn;
    }
  }
  throw new Error(`Не найдена кнопка с текстом "${buttonText}"`);
}

runCreatePlaylistLimitTest().catch(console.error);
