import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runLyricsTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  const trackName = "I AM";

  try {
    await page.goto("http://localhost:3000/login");
    await page.type('input[placeholder="введите логин"]', "admin");
    await page.type('input[placeholder="введите пароль"]', "admin");

    const loginButton = await page.waitForSelector("button", { visible: true });
    if (!loginButton) throw new Error("Кнопка входа не найдена");

    await loginButton.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    await page.waitForSelector('input[placeholder="Поиск"]');
    await page.type('input[placeholder="Поиск"]', trackName);

    const searchIcon = await page.waitForSelector(
      '[data-testid="search-icon"]',
      { visible: true }
    );
    await searchIcon.click();

    await page.waitForSelector('div[class*="search__results"]', {
      timeout: 5000,
    });

    const trackElement = await page.evaluateHandle(() => {
      const results = Array.from(
        document.querySelectorAll('div[class*="search__result"]')
      );
      return results.find(
        (el) =>
          el.textContent.includes("Трек") && el.textContent.includes("I AM")
      );
    });

    if (!trackElement.asElement()) throw new Error("Трек 'I AM' не найден");

    await trackElement.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });
    await delay(1000);

    const lyricsIconSelector =
      'i.fa-regular.fa-star[class*="track__controlIcon"]';
    await page.waitForSelector(lyricsIconSelector, {
      visible: true,
      timeout: 10000,
    });

    await page.evaluate((selector) => {
      const icon = document.querySelector(selector);
      if (!icon) throw new Error("Иконка текста песни не найдена");
      icon.click();
    }, lyricsIconSelector);

    await delay(1000);

    const backButton = await page.waitForSelector('i[class*="arrow"]');
    if (backButton) {
      await backButton.click();
      await delay(1000);
    }

    const favoriteIconSelector =
      'i.fa-solid.fa-star[class*="header__buttons__icons"]';
    await page.waitForSelector(favoriteIconSelector, {
      visible: true,
      timeout: 10000,
    });

    await page.evaluate((selector) => {
      const icon = document.querySelector(selector);
      if (!icon) throw new Error("Иконка добавления в избранное не найдена");
      icon.click();
    }, favoriteIconSelector);

    await delay(1000);

    const playlistName = await page.$eval('h2[class*="playlist__name"]', (el) =>
      el.textContent.trim()
    );
    if (playlistName !== "I AM")
      throw new Error(`Ожидался трек "I AM", но найден: ${playlistName}`);

    console.log("12 тест выполнен успешно, добавление трека в избранное");
  } finally {
    await browser.close();
  }
};

runLyricsTest().catch(console.error);
