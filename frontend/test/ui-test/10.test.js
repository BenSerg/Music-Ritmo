import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runTrackPlaybackByGenreTest = async () => {
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

  await page.waitForSelector('[data-testid="playlist-link"]', {
    visible: true,
    timeout: 10000,
  });

  const rockPlaylist = await page.$('a[href="/genre/Рок"]');
  if (rockPlaylist) {
    await rockPlaylist.evaluate((link) => link.click());
    await Promise.race([
      page.waitForNavigation({ waitUntil: "networkidle0" }),
      page.waitForSelector('[data-testid="genre-page"]', { timeout: 5000 }),
      page.waitForSelector('[data-testid="track-list"]', { timeout: 5000 }),
    ]);

    if (page.url().includes("/login")) {
      throw new Error("Редирект на страницу логина после перехода по жанру");
    }
  } else {
    throw new Error("Плейлист жанра 'Рок' не найден");
  }

  await page.waitForSelector('h2[class*="playlist__name"]', {
    visible: true,
  });
  const trackList = await page.$$('h2[class*="playlist__name"]');
  if (trackList.length > 0) {
    await trackList[0].click();
  } else {
    throw new Error("Треки жанра 'Рок' не найдены");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });

  try {
    const playButtons = await page.$$('div[class*="track__playPause"]');
    if (playButtons.length > 0) {
      await playButtons[0].click();
      await delay(1000);
    } else {
      throw new Error("Кнопка воспроизведения трека не найдена");
    }
  } catch {
    throw new Error("Ошибка при попытке воспроизведения трека");
  }

  console.log("10 тест выполнен успешно, воспроизведение трека из жанра");

  await browser.close();
};

runTrackPlaybackByGenreTest().catch(console.error);
