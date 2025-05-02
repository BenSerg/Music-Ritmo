import puppeteer from "puppeteer";

const runPasswordChangeTest = async () => {
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

  const newPasswordField = await page.waitForSelector(
    'input[placeholder="введите новый пароль"]',
    { visible: true }
  );

  const confirmPasswordField = await page.waitForSelector(
    'input[placeholder="подтвердите новый пароль"]',
    { visible: true }
  );

  const saveChangesButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((button) =>
      button.textContent.includes("Сохранить изменения")
    );
  });

  await newPasswordField.type("admin1");

  const passwordMismatchError = await page.evaluate(() => {
    const elements = Array.from(document.querySelectorAll("*"));
    return elements.some((el) =>
      el.textContent.includes("Пароли не совпадают")
    );
  });

  if (!passwordMismatchError) {
    throw new Error("Не появилось сообщение об ошибке несовпадения паролей");
  }

  const isSaveButtonDisabledInitially = await saveChangesButton.evaluate(
    (button) => button.disabled
  );
  if (!isSaveButtonDisabledInitially) {
    throw new Error(
      "Кнопка 'Сохранить изменения' должна быть неактивна при несовпадении паролей"
    );
  }

  await confirmPasswordField.type("admin1");

  await page.waitForFunction(
    (button) => !button.disabled,
    { timeout: 5000 },
    saveChangesButton
  );

  await saveChangesButton.click();

  console.log("5 тест выполнен успешно, изменение пароля");

  await browser.close();
};

runPasswordChangeTest().catch(console.error);
