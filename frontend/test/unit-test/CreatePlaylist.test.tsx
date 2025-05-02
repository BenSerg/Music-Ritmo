import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import CreatePlaylist from "@/app/create-playlist/page";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/auth-context";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
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

describe("CreatePlaylist Component", () => {
  const mockUser = "testUser";
  const mockPassword = "testPassword";
  const mockPush = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    (useAuth as jest.Mock).mockReturnValue({
      user: mockUser,
      password: mockPassword,
    });

    jest.clearAllMocks();
  });

  test("renders the create playlist form", () => {
    render(<CreatePlaylist />);
    expect(screen.getByText("Создание плейлиста")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Название плейлиста")
    ).toBeInTheDocument();
    expect(screen.getByText("Создать плейлист")).toBeInTheDocument();
  });

  test("shows error when playlist name is too short", async () => {
    render(<CreatePlaylist />);

    const input = screen.getByPlaceholderText("Название плейлиста");
    fireEvent.change(input, { target: { value: "abc" } });

    expect(
      screen.getByText(
        "Длина названия плейлиста не может быть короче 5 символов"
      )
    ).toBeInTheDocument();
  });

  test("shows error when playlist name already exists", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              playlists: {
                playlist: [{ name: "Existing Playlist" }],
              },
            },
          }),
      })
    ) as jest.Mock;

    render(<CreatePlaylist />);

    await waitFor(() => {
      expect(screen.queryByText("Загрузка...")).not.toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText("Название плейлиста");
    fireEvent.change(input, { target: { value: "Existing Playlist" } });

    expect(
      screen.getByText("Плейлист с таким названием уже существует")
    ).toBeInTheDocument();
  });

  test("disables create button when playlist name is invalid", async () => {
    render(<CreatePlaylist />);

    const input = screen.getByPlaceholderText("Название плейлиста");
    const createButton = screen.getByText("Создать плейлист");

    fireEvent.change(input, { target: { value: "abcd" } });
    expect(createButton).toBeDisabled();

    fireEvent.change(input, { target: { value: "abcde" } });
    expect(createButton).not.toBeDisabled();
  });

  test("creates playlist successfully", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
            },
          }),
      })
    ) as jest.Mock;

    render(<CreatePlaylist />);

    const input = screen.getByPlaceholderText("Название плейлиста");
    const createButton = screen.getByText("Создать плейлист");

    fireEvent.change(input, { target: { value: "New Playlist" } });
    fireEvent.click(createButton);

    expect(screen.getByText("Создание...")).toBeInTheDocument();

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/playlists");
    });
  });

  test("shows error when playlist creation fails", async () => {
    global.fetch = jest.fn(() =>
      Promise.reject(new Error("Не удалось создать плейлист"))
    ) as jest.Mock;

    render(<CreatePlaylist />);

    const input = screen.getByPlaceholderText("Название плейлиста");
    const createButton = screen.getByText("Создать плейлист");

    fireEvent.change(input, { target: { value: "New Playlist" } });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(
        screen.getByText("Произошла ошибка при создании плейлиста")
      ).toBeInTheDocument();
    });
  });
});
