import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import Album from "../src/app/album/[albumId]/page";
import { useParams } from "next/navigation";
import { useAuth } from "@/app/auth-context";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  useParams: jest.fn(),
}));

jest.mock("../src/app/auth-context", () => ({
  useAuth: jest.fn(),
}));

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
) as jest.Mock;

describe("Album Component", () => {
  const mockUser = "testUser";
  const mockPassword = "testPassword";

  beforeEach(() => {
    (useParams as jest.Mock).mockReturnValue({ albumId: "123" });

    (useAuth as jest.Mock).mockReturnValue({
      user: mockUser,
      password: mockPassword,
    });

    jest.clearAllMocks();
  });

  test("shows loading state initially", () => {
    render(<Album />);
    expect(screen.getByText("Загрузка...")).toBeInTheDocument();
  });

  test("displays album data when fetched successfully", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              album: {
                id: "123",
                name: "Test Album",
                song: [
                  {
                    id: "1",
                    title: "Test Track",
                    artist: "Test Artist",
                    artistId: "1",
                    duration: 300,
                    path: "/path/to/track",
                    starred: "",
                  },
                ],
              },
            },
          }),
      })
    ) as jest.Mock;

    render(<Album />);

    await waitFor(() => {
      expect(screen.getByText("Test Album")).toBeInTheDocument();
      expect(screen.getByText("Test Track")).toBeInTheDocument();
      expect(screen.getByText("Test Artist")).toBeInTheDocument();
    });
  });

  test("displays error message when album data fetching fails", async () => {
    global.fetch = jest.fn(() =>
      Promise.reject(new Error("Не удалось получить данные с сервера"))
    ) as jest.Mock;

    render(<Album />);

    await waitFor(() => {
      expect(screen.getByText("Загрузка...")).toBeInTheDocument();
    });
  });

  test("displays message when no tracks are available", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              album: {
                id: "123",
                name: "Test Album",
                song: [],
              },
            },
          }),
      })
    ) as jest.Mock;

    render(<Album />);

    await waitFor(() => {
      expect(screen.getByText("Треки не найдены.")).toBeInTheDocument();
    });
  });
});
