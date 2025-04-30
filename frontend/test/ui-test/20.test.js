import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runPlayerControlsTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  const loginUrl = "http://localhost:3000/login";
  const username = "admin";
  const password = "admin";
  const trackToSearch = "ASPHALT 8";
  const expectedSecondTrack = "Undead";
  const expectedFinalTrack = "Как je";

  try {
    await page.goto(loginUrl);
    await page.type('input[placeholder="введите логин"]', username);
    await page.type('input[placeholder="введите пароль"]', password);
    await page.click("button");
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    await page.waitForSelector('input[placeholder="Поиск"]');
    await page.type('input[placeholder="Поиск"]', trackToSearch);
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
          el.textContent.includes("Трек") &&
          el.textContent.includes("ASPHALT 8")
      );
    });

    if (!foundTrack.asElement()) throw new Error("Трек 'ASPHALT 8' не найден");
    await foundTrack.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });
    await delay(2000);

    const safeClick = async (selector, actionDescription) => {
      try {
        await page.waitForSelector(selector, { visible: true, timeout: 5000 });
        await page.evaluate((sel) => {
          const element = document.querySelector(sel);
          if (element) element.click();
          else throw new Error(`Элемент ${sel} не найден`);
        }, selector);
        await delay(500);
      } catch {
        throw new Error(`Ошибка при действии: ${actionDescription}`);
      }
    };

    for (let attempt = 0; attempt < 5; attempt++) {
      await safeClick(
        'div[class*="track__controls"] > div:first-child',
        `Установка режима (попытка ${attempt + 1})`
      );
      const currentMode = await page.evaluate(() => {
        const icon = document.querySelector(
          'div[class*="track__controls"] > div:first-child i'
        );
        return icon ? icon.className : null;
      });
      if (currentMode && currentMode.includes("fa-arrow-right-long")) break;
      if (attempt === 4)
        throw new Error(
          "Не удалось установить режим последовательного воспроизведения"
        );
    }

    const initialTrack = await page.$eval('h2[class*="track__name"]', (el) =>
      el.textContent.trim()
    );
    await safeClick(
      'i.fa-solid.fa-forward[class*="track__controlIcon"]',
      "Переключение трека вперед"
    );

    await page.waitForFunction(
      (previous) => {
        const current = document
          .querySelector('h2[class*="track__name"]')
          ?.textContent.trim();
        return current && current !== previous;
      },
      { timeout: 5000 },
      initialTrack
    );

    const nextTrack = await page.$eval('h2[class*="track__name"]', (el) =>
      el.textContent.trim()
    );
    if (nextTrack !== expectedSecondTrack) {
      throw new Error(
        `Ожидался трек '${expectedSecondTrack}', получено: '${nextTrack}'`
      );
    }

    const urlBeforeSecondClick = page.url();
    await safeClick(
      'i.fa-solid.fa-forward[class*="track__controlIcon"]',
      "Повторное переключение трека"
    );
    await delay(1000);
    if (page.url() !== urlBeforeSecondClick)
      throw new Error("Обнаружен неожиданный редирект при переключении");

    for (let attempt = 0; attempt < 5; attempt++) {
      await safeClick(
        'div[class*="track__controls"] > div:first-child',
        `Установка повтора (попытка ${attempt + 1})`
      );
      const currentMode = await page.evaluate(() => {
        const icon = document.querySelector(
          'div[class*="track__controls"] > div:first-child i'
        );
        return icon ? icon.className : null;
      });
      if (currentMode && currentMode.includes("fa-repeat")) break;
      if (attempt === 4) throw new Error("Не удалось установить режим повтора");
    }

    const trackBeforeRepeat = await page.$eval(
      'h2[class*="track__name"]',
      (el) => el.textContent.trim()
    );
    await safeClick(
      'i.fa-solid.fa-forward[class*="track__controlIcon"]',
      "Переключение трека в режиме повтора"
    );

    await page.waitForFunction(
      (prev) => {
        const current = document
          .querySelector('h2[class*="track__name"]')
          ?.textContent.trim();
        return current && current !== prev;
      },
      { timeout: 5000 },
      trackBeforeRepeat
    );

    const trackAfterRepeat = await page.$eval(
      'h2[class*="track__name"]',
      (el) => el.textContent.trim()
    );
    if (trackAfterRepeat !== expectedFinalTrack) {
      throw new Error(
        `Ожидался трек '${expectedFinalTrack}', получено: '${trackAfterRepeat}'`
      );
    }

    console.log("20 тест выполнен успешно, изменение очереди воспроизведения");
  } catch (error) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    await page.screenshot({ path: `error-${timestamp}.png` });
    throw new Error(error.message);
  } finally {
    await browser.close();
  }
};

runPlayerControlsTest().catch(console.error);
