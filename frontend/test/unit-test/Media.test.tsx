import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Media from "../src/app/media/page";
import "@testing-library/jest-dom";

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
) as jest.Mock;

describe("Media Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders the media library page", () => {
    render(<Media />);
    expect(screen.getByText("Медиатека")).toBeInTheDocument();
    expect(screen.getByText("Запустить сканирование")).toBeInTheDocument();
  });

  test("shows error when scan initiation fails", async () => {
    global.fetch = jest.fn(() =>
      Promise.reject(new Error("Ошибка при запуске сканирования"))
    ) as jest.Mock;

    render(<Media />);

    fireEvent.click(screen.getByText("Запустить сканирование"));

    await waitFor(() => {
      expect(
        screen.getByText("Ошибка при запуске сканирования")
      ).toBeInTheDocument();
    });
  });

  test("updates scan status during scanning", async () => {
    global.fetch = jest.fn((url) => {
      if (url.includes("startScan")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              "subsonic-response": {
                status: "ok",
              },
            }),
        });
      } else if (url.includes("getScanStatus")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              "subsonic-response": {
                status: "ok",
                scanStatus: {
                  scanning: true,
                  count: 10,
                },
              },
            }),
        });
      }
      return Promise.reject(new Error("Unknown URL"));
    }) as jest.Mock;

    render(<Media />);

    fireEvent.click(screen.getByText("Запустить сканирование"));

    await waitFor(() => {
      expect(
        screen.getByText("Сканирование в процессе: найдено 10 элементов")
      ).toBeInTheDocument();
    });
  });

  test("shows error when scan status check fails", async () => {
    global.fetch = jest.fn((url) => {
      if (url.includes("startScan")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              "subsonic-response": {
                status: "ok",
              },
            }),
        });
      } else if (url.includes("getScanStatus")) {
        return Promise.reject(
          new Error("Ошибка при получении статуса сканирования")
        );
      }
      return Promise.reject(new Error("Unknown URL"));
    }) as jest.Mock;

    render(<Media />);

    fireEvent.click(screen.getByText("Запустить сканирование"));

    await waitFor(() => {
      expect(
        screen.getByText("Ошибка при получении статуса сканирования")
      ).toBeInTheDocument();
    });
  });
});
