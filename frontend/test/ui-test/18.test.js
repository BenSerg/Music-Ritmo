import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runTagEditorTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  const trackTitle = "I AM";

  await page.goto("http://localhost:3000/login");
  await page.type('input[placeholder="введите логин"]', "admin");
  await page.type('input[placeholder="введите пароль"]', "admin");
  await page.click("button");
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  await page.type('input[placeholder="Поиск"]', trackTitle);
  await page.click('[data-testid="search-icon"]');
  await page.waitForSelector('div[class*="search__results"]');

  const trackHandles = await page.$$('div[class*="search__result"]');
  let found = false;
  for (const handle of trackHandles) {
    const text = await page.evaluate((el) => el.textContent, handle);
    if (text.includes("I AM")) {
      await handle.click();
      found = true;
      break;
    }
  }

  if (!found) {
    throw new Error("Трек 'I AM' не найден в результатах поиска");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });
  await delay(1000);

  const tagIconSelector = 'i.fa-solid.fa-info[class*="track__infoIcon"]';
  await page.waitForSelector(tagIconSelector, { visible: true });
  await page.click(tagIconSelector);
  await page.waitForSelector("table", { visible: true });

  const tagRows = await page.$$("table tr");
  let titleTagUpdated = false;

  for (const row of tagRows) {
    const inputs = await row.$$("td input");
    if (inputs.length < 2) continue;

    const key = await page.evaluate((el) => el.value, inputs[0]);
    if (key === "title") {
      await inputs[1].click({ clickCount: 3 });
      await inputs[1].type("I AMM");
      titleTagUpdated = true;
      break;
    }
  }

  if (!titleTagUpdated) {
    throw new Error("Тег 'title' не найден для редактирования");
  }

  const buttons = await page.$$("button");
  let addTagButton = null;
  for (const btn of buttons) {
    const text = await page.evaluate((el) => el.textContent, btn);
    if (text.includes("добавить тег")) {
      addTagButton = btn;
      break;
    }
  }

  if (!addTagButton) {
    throw new Error("Кнопка 'добавить тег' не найдена");
  }

  await addTagButton.click();
  await delay(500);

  const allButtons = await page.$$("button");
  let saveButton = null;
  for (const btn of allButtons) {
    const text = await page.evaluate((el) => el.textContent, btn);
    if (text.includes("сохранить")) {
      saveButton = btn;
      break;
    }
  }

  if (!saveButton) {
    throw new Error("Кнопка 'сохранить' не найдена");
  }

  await saveButton.click();

  console.log("18 тест выполнен успешно, редактирование тегов трека");

  await browser.close();
};

runTagEditorTest().catch(console.error);
