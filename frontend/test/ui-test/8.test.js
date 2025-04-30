import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runWideSearchTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  const searchQuery = "a";

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

  await page.waitForSelector('input[placeholder="Поиск"]');
  await page.type('input[placeholder="Поиск"]', searchQuery);

  const searchIcon = await page.waitForSelector('[data-testid="search-icon"]');
  await searchIcon.click();

  await page.waitForSelector(`div[class*="search__results"]`, {
    visible: true,
    timeout: 5000,
  });

  const showAllResultsButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((b) =>
      b.textContent.includes("Показать все результаты")
    );
  });

  if (showAllResultsButton) {
    await showAllResultsButton.click();
  } else {
    throw new Error("Кнопка 'Показать все результаты' не найдена");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });
  if (!page.url().includes("/search")) {
    throw new Error("Не выполнен переход на страницу всех результатов");
  }

  await page.waitForSelector('div[class*="playlist__name"]', { visible: true });
  const playlistElements = await page.$$('div[class*="playlist__name"]');
  if (playlistElements.length > 0) {
    await playlistElements[0].click();
  } else {
    throw new Error("Плейлисты не найдены");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });

  const backButtonFromPlaylist = await page.waitForSelector(
    'i[class*="arrow"]'
  );
  if (backButtonFromPlaylist) {
    await backButtonFromPlaylist.click();
    await delay(1000);
  }

  await page.waitForSelector('div[class*="artist__name"]', { visible: true });
  const artistElements = await page.$$('div[class*="artist__name"]');
  if (artistElements.length > 0) {
    await artistElements[0].click();
  } else {
    throw new Error("Артисты не найдены");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });

  const backButtonFromArtist = await page.waitForSelector('i[class*="arrow"]');
  if (backButtonFromArtist) {
    await backButtonFromArtist.click();
    await delay(1000);
  }

  await page.waitForSelector('h2[class*="playlist__name"]', { visible: true });
  const trackElements = await page.$$('h2[class*="playlist__name"]');
  if (trackElements.length > 0) {
    await trackElements[0].click();
  } else {
    throw new Error("Треки не найдены");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });

  const playButtons = await page.$$('div[class*="track__playPause"]');
  if (playButtons.length > 0) {
    await playButtons[0].click();
    await delay(3000);
  }

  console.log("8 тест выполнен успешно, поиск с большим совпадением");

  await browser.close();
};

runWideSearchTest().catch(console.error);
