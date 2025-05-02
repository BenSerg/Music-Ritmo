import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runSearchTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  const trackName = "I AM";
  const artistName = "MACAN";
  const albumName = "Swan Songs";

  await page.goto("http://localhost:3000/login");
  await page.type('input[placeholder="введите логин"]', "admin");
  await page.type('input[placeholder="введите пароль"]', "admin");

  const loginButton = await page.waitForSelector("button", { visible: true });
  if (!loginButton) throw new Error("Кнопка входа не найдена");
  await loginButton.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  await page.waitForSelector('input[placeholder="Поиск"]');
  await page.type('input[placeholder="Поиск"]', trackName);

  const searchIcon = await page.waitForSelector('[data-testid="search-icon"]', {
    visible: true,
  });
  await searchIcon.click();

  await page.waitForSelector('div[class*="search__results"]');
  const trackElements = await page.$$('div[class*="search__result"]');

  let trackFound = false;
  for (const element of trackElements) {
    const text = await page.evaluate((el) => el.innerText, element);
    if (text.includes(`Трек ${trackName}`)) {
      await element.click();
      trackFound = true;
      break;
    }
  }
  if (!trackFound) throw new Error(`Трек '${trackName}' не найден`);
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  try {
    const playButton = await page.waitForSelector(
      'div[class*="track__playPause"]',
      { visible: true, timeout: 5000 }
    );
    await playButton.click();
    await delay(1000);
  } catch {}

  const backButton = await page.waitForSelector('i[class*="arrow"]');
  if (!backButton) throw new Error("Кнопка 'Назад' не найдена");
  await backButton.click();
  await delay(1000);

  await page.click('input[placeholder="Поиск"]', { clickCount: 3 });
  await page.keyboard.press("Backspace");
  await page.type('input[placeholder="Поиск"]', artistName);

  const searchIcon2 = await page.waitForSelector(
    '[data-testid="search-icon"]',
    { visible: true }
  );
  await searchIcon2.click();

  await page.waitForSelector('div[class*="search__results"]');
  const artistItems = await page.$$('div[class*="search__result"]');

  let artistFound = false;
  for (const item of artistItems) {
    const text = await page.evaluate((el) => el.innerText, item);
    if (text.includes(`Исполнитель ${artistName}`)) {
      await item.click();
      artistFound = true;
      break;
    }
  }
  if (!artistFound) throw new Error(`Артист '${artistName}' не найден`);
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  const albums = await page.$$('div[class*="playlist"]');
  if (albums.length === 0) throw new Error("Альбомы не найдены");
  await albums[0].click();

  await page.waitForSelector('div[class*="playlist__details"]', {
    visible: true,
  });
  const tracks = await page.$$('div[class*="playlist__details"]');
  if (tracks.length === 0) throw new Error("Треки в альбоме не найдены");

  const trackLink = await tracks[0].$('h2[class*="playlist__name"]');
  if (!trackLink) throw new Error("Название трека не найдено");
  await trackLink.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  try {
    const playButton = await page.waitForSelector(
      'div[class*="track__playPause"]',
      { visible: true, timeout: 5000 }
    );
    await playButton.click();
    await delay(1000);
  } catch {}

  for (let i = 0; i < 3; i++) {
    const backBtn = await page.waitForSelector('i[class*="arrow"]');
    if (!backBtn) throw new Error("Одна из кнопок 'Назад' не найдена");
    await backBtn.click();
    await delay(1000);
  }

  await page.waitForSelector('input[placeholder="Поиск"]');
  await page.click('input[placeholder="Поиск"]', { clickCount: 3 });
  await page.keyboard.press("Backspace");
  await page.type('input[placeholder="Поиск"]', albumName);

  const searchIcon3 = await page.waitForSelector(
    '[data-testid="search-icon"]',
    { visible: true }
  );
  await searchIcon3.click();

  await page.waitForSelector('div[class*="search__results"]');
  const albumResults = await page.$$('div[class*="search__result"]');

  let albumFound = false;
  for (const element of albumResults) {
    const text = await page.evaluate((el) => el.innerText, element);
    if (text.includes(`Альбом ${albumName}`)) {
      await element.click();
      albumFound = true;
      await page.waitForNavigation({ waitUntil: "networkidle0" });
      break;
    }
  }
  if (!albumFound) throw new Error(`Альбом '${albumName}' не найден`);

  await page.waitForSelector('div[class*="playlist__details"]', {
    timeout: 5000,
  });
  const albumTracks = await page.$$('div[class*="playlist__details"]');
  if (albumTracks.length === 0) throw new Error("Треки в альбоме не найдены");

  const firstTrack = await albumTracks[0].$('h2[class*="playlist__name"]');
  if (!firstTrack) throw new Error("Трек в альбоме не найден");
  await firstTrack.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  try {
    const playButton = await page.waitForSelector(
      'div[class*="track__playPause"]',
      { visible: true, timeout: 5000 }
    );
    await playButton.click();
    await delay(1000);
  } catch {}

  console.log("7 тест выполнен успешно, поиск трека, артиста, альбома");

  await browser.close();
};

runSearchTest().catch(console.error);
