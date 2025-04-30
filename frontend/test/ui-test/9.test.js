import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runEmptySearchTest = async () => {
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

  const searchQuery = "qwerty";
  await page.waitForSelector('input[placeholder="Поиск"]');
  await page.type('input[placeholder="Поиск"]', searchQuery);

  const searchIcon = await page.waitForSelector('[data-testid="search-icon"]');
  await searchIcon.click();
  await delay(1000);

  await page.waitForSelector('div[class*="search__no_results"]', {
    visible: true,
    timeout: 5000,
  });

  const noResultsMessage = await page.evaluate(() => {
    const element = document.querySelector('div[class*="search__no_results"]');
    return element ? element.textContent.trim() : null;
  });

  if (noResultsMessage !== "Ничего не найдено") {
    throw new Error(
      `Ожидалось сообщение "Ничего не найдено", получено: "${noResultsMessage}"`
    );
  }

  console.log("9 тест выполнен успешно, поиск несуществующего контента");

  await browser.close();
};

runEmptySearchTest().catch(console.error);
