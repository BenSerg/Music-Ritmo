import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runLyricsTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  const trackTitle = "I AM";
  const loginUrl = "http://localhost:3000/login";
  const searchInputSelector = 'input[placeholder="Поиск"]';
  const lyricsIconSelector =
    'i.fa-solid.fa-list-ul[class*="track__controlIcon"]';
  const lyricsTextSelector = 'p[class*="track_lirics"]';

  try {
    await page.goto(loginUrl);
    await page.type('input[placeholder="введите логин"]', "admin");
    await page.type('input[placeholder="введите пароль"]', "admin");
    await page.click("button");
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    await page.waitForSelector(searchInputSelector);
    await page.type(searchInputSelector, trackTitle);
    const searchIcon = await page.waitForSelector(
      '[data-testid="search-icon"]',
      { visible: true }
    );
    await searchIcon.click();

    await page.waitForSelector('div[class*="search__results"]', {
      timeout: 5000,
    });

    const foundTrack = await page.evaluateHandle(() => {
      return Array.from(
        document.querySelectorAll('div[class*="search__result"]')
      ).find(
        (el) =>
          el.textContent.includes("Трек") && el.textContent.includes("I AM")
      );
    });

    if (!foundTrack.asElement())
      throw new Error("Трек не найден в результатах поиска");
    await foundTrack.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });
    await delay(1000);

    await page.waitForSelector(lyricsIconSelector, {
      visible: true,
      timeout: 10000,
    });
    await page.evaluate((selector) => {
      const icon = document.querySelector(selector);
      if (icon) icon.click();
      else throw new Error("Иконка текста песни не найдена");
    }, lyricsIconSelector);

    await delay(1000);
    await page.waitForSelector(lyricsTextSelector, {
      visible: true,
      timeout: 5000,
    });

    const lyricsContent = await page.evaluate((selector) => {
      const el = document.querySelector(selector);
      return el ? el.textContent.trim() : null;
    }, lyricsTextSelector);

    if (lyricsContent !== "Текст песни не найден") {
      throw new Error(
        `Неверный текст: ожидался 'Текст песни не найден', получено: '${lyricsContent}'`
      );
    }

    console.log("19 тест выполнен успешно, просмотр текста трека");
  } catch (error) {
    await page.screenshot({ path: "lyrics-error.png" });
    throw new Error(error.message);
  } finally {
    await browser.close();
  }
};

runLyricsTest().catch(console.error);
