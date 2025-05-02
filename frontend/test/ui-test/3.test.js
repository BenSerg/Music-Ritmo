import puppeteer from "puppeteer";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const runChangeAvatarTest = async () => {
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

  const settingsLink = await page.waitForSelector(
    'div[data-testid="user-menu"] a[href="/settings"]',
    { visible: true }
  );

  await settingsLink.click();
  await page.waitForNavigation({ waitUntil: "networkidle0" });

  const originalAvatarSrc = await page.$eval('img[alt="User Avatar"]', (img) =>
    img.getAttribute("src")
  );
  await delay(1000);

  const changeAvatarButton = await page.evaluateHandle(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    return buttons.find((button) =>
      button.textContent.includes("Сменить аватар")
    );
  });

  if (changeAvatarButton) {
    await changeAvatarButton.click();
  } else {
    throw new Error("Кнопка смены аватара не найдена");
  }

  await delay(1000);

  await page.waitForFunction(
    (originalSrc) => {
      const avatar = document.querySelector('img[alt="User Avatar"]');
      return avatar && avatar.getAttribute("src") !== originalSrc;
    },
    { timeout: 5000 },
    originalAvatarSrc
  );

  const newAvatarSrc = await page.$eval('img[alt="User Avatar"]', (img) =>
    img.getAttribute("src")
  );

  if (originalAvatarSrc === newAvatarSrc) {
    throw new Error("Аватар не изменился после нажатия на кнопку смены");
  }

  console.log("3 тест выполнен успешно, изменение аватара профиля");

  await browser.close();
};

runChangeAvatarTest().catch(console.error);
