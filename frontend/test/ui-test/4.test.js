import puppeteer from "puppeteer";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const runLoginEditTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("http://localhost:3000/login");
  await page.type('input[placeholder="введите логин"]', "admin");
  await page.type('input[placeholder="введите пароль"]', "admin");
  await page.click("button");

  await page.waitForNavigation({ waitUntil: "networkidle0" });

  await page.click('div[class*="user"]');
  await page.waitForSelector('div[data-testid="user-menu"]', { visible: true });
  await page.click('div[data-testid="user-menu"] a[href="/settings"]');
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  await delay(1000);

  const errorMessageElement = await page.$('div[class*="errorMessage"]');
  if (errorMessageElement) {
    const errorText = await page.evaluate(
      (el) => el.textContent,
      errorMessageElement
    );
    if (errorText !== "Этот логин уже занят.") {
      throw new Error(
        `Ожидалось сообщение 'Этот логин уже занят.', получено: "${errorText}"`
      );
    }
  } else {
    throw new Error("Сообщение 'Этот логин уже занят.' не найдено");
  }

  const loginInput = await page.evaluateHandle(() => {
    const inputs = document.querySelectorAll("input");
    return Array.from(inputs).find((input) => input.value === "admin") || null;
  });

  if (!loginInput) {
    throw new Error('Поле ввода с логином "admin" не найдено');
  }

  const loginInputElement = loginInput.asElement();
  await loginInputElement.click();
  await loginInputElement.type("2");

  const saveButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((button) =>
      button.textContent.includes("Сохранить изменения")
    );
  });

  if (saveButton) {
    await saveButton.click();
  } else {
    throw new Error("Кнопка 'Сохранить изменения' не найдена");
  }

  await delay(1000);

  const headerText = await page.$eval("h1", (el) => el.textContent.trim());
  if (!headerText.includes("admin2")) {
    throw new Error(
      `Ожидался логин 'admin2' в заголовке, получено: "${headerText}"`
    );
  }

  console.log("4 тест выполнен успешно, изменение логина пользователя");

  await browser.close();
};

runLoginEditTest().catch(console.error);
