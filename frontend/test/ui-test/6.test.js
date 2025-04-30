import puppeteer from "puppeteer";

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const runRegistrationTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("http://localhost:3000/login", { waitUntil: "networkidle0" });
  await delay(1000);

  const registrationButton = await page.$(
    'button[data-testid="go-to-registration"]'
  );
  if (!registrationButton) throw new Error("Кнопка регистрации не найдена");

  await page.evaluate(() => {
    const button = document.querySelector(
      'button[data-testid="go-to-registration"]'
    );
    if (button) button.click();
  });

  await page.waitForSelector('input[placeholder="придумайте логин"]', {
    timeout: 5000,
  });

  await page.type('input[placeholder="придумайте логин"]', "admin2");
  await page.type('input[placeholder="придумайте пароль"]', "admin2");
  await delay(500);

  const submitButtonHandle = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((button) =>
      button.textContent.includes("Зарегистрироваться")
    );
  });

  if (!submitButtonHandle)
    throw new Error("Кнопка 'Зарегистрироваться' не найдена");

  const submitButton = submitButtonHandle.asElement();
  if (!submitButton)
    throw new Error("Объект кнопки регистрации не является элементом");

  await submitButton.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  if (!page.url().endsWith("/")) {
    throw new Error(
      "После регистрации не произошёл переход на главную страницу"
    );
  }

  console.log("6 тест выполнен успешно, регистрация нового пользователя");

  await browser.close();
};

runRegistrationTest().catch(console.error);
