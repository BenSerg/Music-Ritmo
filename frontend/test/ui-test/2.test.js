import puppeteer from "puppeteer";

const runLogoutTest = async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("http://localhost:3000/login");

  await page.type('input[placeholder="введите логин"]', "admin");
  await page.type('input[placeholder="введите пароль"]', "admin");

  const loginButton = await page.waitForSelector("button", { visible: true });

  if (loginButton) {
    await loginButton.click();
    await page.waitForNavigation({ waitUntil: "networkidle0" });

    if (!page.url().endsWith("/")) {
      throw new Error("После входа не произошёл редирект на главную страницу");
    }
  } else {
    await browser.close();
    return;
  }

  const userIcon = await page.waitForSelector('div[class*="user"]', {
    visible: true,
  });

  if (userIcon) {
    await userIcon.click();
  } else {
    throw new Error("Иконка пользователя не найдена");
  }

  const logoutButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((button) => button.textContent.includes("Выйти"));
  });

  if (logoutButton) {
    await logoutButton.click();
  } else {
    throw new Error("Кнопка выхода не найдена");
  }

  await page.waitForNavigation({ waitUntil: "networkidle0" });

  if (!page.url().endsWith("/login")) {
    throw new Error("После выхода не произошёл редирект на страницу логина");
  }

  console.log("2 тест выполнен успешно, выход из системы");

  await browser.close();
};

runLogoutTest().catch(console.error);
