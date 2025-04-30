import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runTrackToPlaylistTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  const trackTitle = "I AM";
  const playlistTitle = "Плейлист1";

  await page.goto("http://localhost:3000/login");
  await page.type('input[placeholder="введите логин"]', "admin");
  await page.type('input[placeholder="введите пароль"]', "admin");

  const loginButton = await page.waitForSelector("button", { visible: true });
  await loginButton.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  await page.waitForSelector("i.fa-solid.fa-music");
  await page.click("i.fa-solid.fa-music");
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  await createPlaylist(page, playlistTitle);
  await delay(1000);

  for (let i = 0; i < 3; i++) {
    const backIcon = await page.waitForSelector('i[class*="arrow"]');
    if (!backIcon) throw new Error("Кнопка возврата не найдена");
    await backIcon.click();
    await delay(1000);
  }

  await page.waitForSelector('input[placeholder="Поиск"]');
  await page.type('input[placeholder="Поиск"]', trackTitle);

  const searchButton = await page.waitForSelector(
    '[data-testid="search-icon"]',
    {
      visible: true,
    }
  );
  await searchButton.click();

  await page.waitForSelector('div[class*="search__results"]', {
    timeout: 5000,
  });

  const trackElementHandle = await page.evaluateHandle(() => {
    const results = Array.from(
      document.querySelectorAll('div[class*="search__result"]')
    );
    return results.find(
      (el) => el.textContent.includes("Трек") && el.textContent.includes("I AM")
    );
  });

  if (!trackElementHandle.asElement()) {
    throw new Error("Трек 'I AM' не найден в результатах поиска");
  }

  await trackElementHandle.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });
  await delay(1000);

  const shareButton = await page.waitForSelector(
    'i.fa-solid.fa-share[class*="track__controlIcon"]',
    {
      visible: true,
      timeout: 10000,
    }
  );
  await shareButton.click();

  await page.waitForSelector('div[class*="modalContent"]');

  const playlistItem = await page.waitForSelector(
    'div[class*="track_playlistItem"]'
  );
  await playlistItem.click();

  await page.waitForSelector('p[class*="successMessage"]');

  const closeButton = await page.waitForSelector("i.fa-solid.fa-xmark", {
    visible: true,
  });
  await closeButton.click();

  const backButton = await page.waitForSelector('i[class*="arrow"]');
  if (backButton) await backButton.click();
  await delay(1000);

  await page.waitForSelector("i.fa-solid.fa-music");
  await page.click("i.fa-solid.fa-music");
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  const playlistElements = await page.$$('div[class*="playlist__name"]');
  let playlistFound = false;
  for (const el of playlistElements) {
    const text = await page.evaluate((el) => el.textContent.trim(), el);
    if (text === playlistTitle) {
      await el.click();
      await page.waitForNavigation({ waitUntil: "networkidle0" });
      playlistFound = true;
      break;
    }
  }

  if (!playlistFound) {
    throw new Error(`Плейлист "${playlistTitle}" не найден`);
  }

  await page.waitForSelector('h2[class*="playlist__name"]', { timeout: 5000 });
  const trackElements = await page.$$('h2[class*="playlist__name"]');
  let trackInPlaylist = false;
  for (const el of trackElements) {
    const text = await page.evaluate((el) => el.textContent.trim(), el);
    if (text.includes(trackTitle)) {
      trackInPlaylist = true;
      break;
    }
  }

  if (!trackInPlaylist) {
    throw new Error(
      `Трек "${trackTitle}" не найден в плейлисте "${playlistTitle}"`
    );
  }

  console.log("16 тест выполнен успешно, добавление трека в плейлист");
  await browser.close();
};

async function createPlaylist(page, playlistTitle) {
  const createButton = await findButtonByText(page, "создать плейлист");
  await createButton.click();
  await page.waitForSelector('input[placeholder="Название плейлиста"]', {
    timeout: 5000,
  });
  await page.type('input[placeholder="Название плейлиста"]', playlistTitle);
  const confirmButton = await findButtonByText(page, "Создать плейлист");
  await confirmButton.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });
}

async function findButtonByText(page, text) {
  const buttons = await page.$$("button");
  for (const button of buttons) {
    const buttonText = await page.evaluate(
      (el) => el.textContent.trim().toLowerCase(),
      button
    );
    if (buttonText.includes(text.toLowerCase())) return button;
  }
  throw new Error(`Кнопка с текстом "${text}" не найдена`);
}

runTrackToPlaylistTest().catch(console.error);
