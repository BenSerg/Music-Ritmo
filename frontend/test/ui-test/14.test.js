import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runRenamePlaylistTest = async () => {
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

    const originalPlaylistName = "Плейлист1";
    await createPlaylist(page, originalPlaylistName);
    await checkPlaylistExists(page, originalPlaylistName);

    await openPlaylistForEditing(page, originalPlaylistName);

    const editBtn = await findButtonByText(page, "Редактировать");
    await editBtn.click();

    await page.waitForSelector('input[placeholder="Название плейлиста"]', {
      timeout: 5000,
    });

    const nameInput = await page.$('input[placeholder="Название плейлиста"]');
    await nameInput.click({ clickCount: 3 });
    await page.keyboard.press("Backspace");
    await nameInput.type("Плейлист3");

    const saveBtn = await findButtonByText(page, "Сохранить");
    await saveBtn.click();
    await delay(1000);

    const successMessage = await page.evaluate(() => {
      const divs = Array.from(document.querySelectorAll("div"));
      const messageDiv = divs.find(
        (div) =>
          div.className === "" &&
          div.textContent.trim() === "Название успешно сохранено"
      );
      return messageDiv ? messageDiv.textContent.trim() : null;
    });

    if (successMessage !== "Название успешно сохранено") {
      throw new Error("Не найдено сообщение об успешном сохранении названия");
    }

    console.log("14 тест выполнен успешно, редактирование названия плейлиста");
  } catch (error) {
    throw new Error(error.message);
  } finally {
    await delay(1000);
    await browser.close();
  }
};

async function createPlaylist(page, playlistName) {
  const createBtn = await findButtonByText(page, "создать плейлист");
  await createBtn.click();
  await page.waitForSelector('input[placeholder="Название плейлиста"]', {
    timeout: 5000,
  });
  await page.type('input[placeholder="Название плейлиста"]', playlistName);
  const confirmBtn = await findButtonByText(page, "Создать плейлист");
  await confirmBtn.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });
}

async function checkPlaylistExists(page, playlistName) {
  await page.waitForSelector('div[class*="playlist__name"]', { timeout: 5000 });
  const elements = await page.$$('div[class*="playlist__name"]');
  for (const element of elements) {
    const text = await page.evaluate((el) => el.textContent.trim(), element);
    if (text === playlistName) return;
  }
  throw new Error(`Не найден плейлист с названием "${playlistName}"`);
}

async function openPlaylistForEditing(page, playlistName) {
  await page.waitForSelector('div[class*="playlist__name"]', { timeout: 5000 });
  const playlistElements = await page.$$('div[class*="playlist__name"]');
  for (const element of playlistElements) {
    const text = await page.evaluate((el) => el.textContent.trim(), element);
    if (text === playlistName) {
      await element.click();
      await page.waitForNavigation({ waitUntil: "networkidle0" });
      return;
    }
  }
  throw new Error(
    `Не удалось открыть плейлист "${playlistName}" для редактирования`
  );
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
  throw new Error(`Не найдена кнопка с текстом "${text}"`);
}

runRenamePlaylistTest().catch(console.error);
