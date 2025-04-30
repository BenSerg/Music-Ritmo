import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Playlist } from "@/entities/playlist";

jest.mock("../src/app/auth-context", () => ({
  useAuth: () => ({
    user: "testUser",
    password: "testPassword",
    setUser: jest.fn(),
    setPassword: jest.fn(),
  }),
}));

jest.mock("../src/shared/button", () => ({
  Button: jest.fn(({ children, onClick }) => (
    <button onClick={onClick}>{children}</button>
  )),
}));

jest.mock("next/image", () => ({
  __esModule: true,
  default: (props: {
    src: string;
    alt: string;
    width: number;
    height: number;
    className?: string;
  }) => (
    <img
      src={props.src}
      alt={props.alt}
      width={props.width}
      height={props.height}
      className={props.className}
    />
  ),
}));

jest.mock("next/link", () => {
  return jest.fn(({ children, href }) => <a href={href}>{children}</a>);
});

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ "subsonic-response": { status: "ok" } }),
    blob: () => Promise.resolve(new Blob()),
  })
) as jest.Mock;

global.URL.createObjectURL = jest.fn(() => "mock-url");

describe("Playlist Component", () => {
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  test("renders playlist with name and link", () => {
    render(
      <Playlist name="Test Playlist" link="/playlist/test" showDelete={false} />
    );

    const playlistName = screen.getByText("Test Playlist");
    expect(playlistName).toBeInTheDocument();

    const playlistLink = screen.getByRole("link");
    expect(playlistLink).toHaveAttribute("href", "/playlist/test");
  });

  test("renders delete icon if showDelete is true", () => {
    render(
      <Playlist name="Test Playlist" link="/playlist/test" showDelete={true} />
    );

    const deleteIcon = screen.getByRole("button", { name: /delete/i });
    expect(deleteIcon).toBeInTheDocument();
  });

  test("does not render delete icon if showDelete is false", () => {
    render(
      <Playlist name="Test Playlist" link="/playlist/test" showDelete={false} />
    );

    const deleteIcon = screen.queryByRole("button", { name: /delete/i });
    expect(deleteIcon).not.toBeInTheDocument();
  });

  test("opens modal on delete icon click", () => {
    render(
      <Playlist name="Test Playlist" link="/playlist/test" showDelete={true} />
    );

    const deleteIcon = screen.getByRole("button", { name: /delete/i });
    fireEvent.click(deleteIcon);

    const modal = screen.getByText(
      "Вы уверены, что хотите удалить плейлист Test Playlist?"
    );
    expect(modal).toBeInTheDocument();
  });

  test("closes modal on cancel button click", () => {
    render(
      <Playlist name="Test Playlist" link="/playlist/test" showDelete={true} />
    );

    const deleteIcon = screen.getByRole("button", { name: /delete/i });
    fireEvent.click(deleteIcon);

    const cancelButton = screen.getByText("Нет");
    fireEvent.click(cancelButton);

    const modal = screen.queryByText(
      "Вы уверены, что хотите удалить плейлист Test Playlist?"
    );
    expect(modal).not.toBeInTheDocument();
  });

  test("calls onDelete and closes modal on confirm button click", async () => {
    render(
      <Playlist
        name="Test Playlist"
        link="/playlist/test"
        showDelete={true}
        playlist_id="123"
        onDelete={mockOnDelete}
      />
    );

    const deleteIcon = screen.getByRole("button", { name: /delete/i });
    fireEvent.click(deleteIcon);

    const confirmButton = screen.getByText("Да");
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(mockOnDelete).toHaveBeenCalledWith("123");
    });

    await waitFor(
      () => {
        expect(
          screen.queryByText(
            "Вы уверены, что хотите удалить плейлист Test Playlist?"
          )
        ).not.toBeInTheDocument();
      },
      { timeout: 2000 }
    );
  });

  test("renders cover art if coverArt is provided", async () => {
    render(
      <Playlist
        name="Test Playlist"
        link="/playlist/test"
        showDelete={false}
        coverArt="123"
      />
    );

    await waitFor(() => {
      const coverImage = screen.getByRole("img", {
        name: "Test Playlist cover",
      });
      expect(coverImage).toBeInTheDocument();
      expect(coverImage).toHaveAttribute("src", "mock-url");
    });
  });

  test("does not render cover art if coverArt is not provided", () => {
    render(
      <Playlist name="Test Playlist" link="/playlist/test" showDelete={false} />
    );

    const coverImage = screen.queryByRole("img");
    expect(coverImage).not.toBeInTheDocument();
  });

  test("handles cover art fetch error", async () => {
    global.fetch = jest.fn(() =>
      Promise.reject("Failed to fetch")
    ) as jest.Mock;
    render(
      <Playlist
        name="Test Playlist"
        link="/playlist/test"
        showDelete={false}
        coverArt="123"
      />
    );

    await waitFor(() => {
      const coverImage = screen.queryByRole("img");
      expect(coverImage).not.toBeInTheDocument();
    });
  });
});
