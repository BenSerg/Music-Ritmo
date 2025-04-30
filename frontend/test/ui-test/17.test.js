import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runCombinedTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  const trackTitle = "I AM";

  await page.goto("http://localhost:3000/login");
  await page.type('input[placeholder="введите логин"]', "admin");
  await page.type('input[placeholder="введите пароль"]', "admin");

  const loginButton = await page.waitForSelector("button", { visible: true });
  await loginButton.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

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

  await page.waitForSelector('p[class*="track__artist"]', {
    visible: true,
    timeout: 5000,
  });

  const artistElement = await page.$('p[class*="track__artist"]');
  if (!artistElement) {
    throw new Error("Элемент исполнителя не найден на странице трека");
  }

  await artistElement.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  if (!page.url().includes("/artist/")) {
    throw new Error("Не выполнен переход на страницу артиста");
  }

  console.log("17 тест выполнен успешно, переход на страницу артиста из трека");

  await browser.close();
};

runCombinedTest().catch(console.error);
