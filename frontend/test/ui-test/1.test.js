import puppeteer from "puppeteer";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const runInvalidLoginTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("http://localhost:3000/login");

  await page.type('input[placeholder="введите логин"]', "admin1");
  await page.type('input[placeholder="введите пароль"]', "admin2");

  const loginButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((button) => button.textContent.includes("Войти"));
  });

  if (loginButton) {
    await loginButton.click();
  } else {
    throw new Error("Кнопка входа не найдена на странице");
  }

  await delay(1000);

  const loginErrorMessage = await page.evaluate(() => {
    const errorElement = [...document.querySelectorAll("div")].find((div) =>
      div.textContent.includes("Неверно введенный логин или пароль")
    );
    return errorElement ? errorElement.textContent : null;
  });

  if (!loginErrorMessage) {
    throw new Error(
      "Не отображается сообщение об ошибке при неверных данных входа"
    );
  }

  console.log("1 тест выполнен успешно, вход с неверными данными");

  await browser.close();
};

runInvalidLoginTest().catch(console.error);
