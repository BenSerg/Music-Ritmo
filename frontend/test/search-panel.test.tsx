import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { SearchPanel } from "@/features/search-panel";
import { useRouter } from "next/navigation";

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

describe("SearchPanel Component", () => {
  const mockPush = jest.fn();
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  test("renders search input and icon", () => {
    render(<SearchPanel />);

    const searchInput = screen.getByPlaceholderText("Поиск");
    expect(searchInput).toBeInTheDocument();

    const searchIcon = screen.getByTestId("search-icon");
    expect(searchIcon).toBeInTheDocument();
  });

  test("updates query state on input change", () => {
    render(<SearchPanel />);

    const searchInput = screen.getByPlaceholderText("Поиск");
    fireEvent.change(searchInput, { target: { value: "Test" } });

    expect(searchInput).toHaveValue("Test");
  });

  test("displays search results on successful search", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              searchResult3: {
                song: [
                  {
                    id: "1",
                    title: "Test Song",
                    artist: "Test Artist",
                    album: "Test Album",
                  },
                ],
                album: [
                  {
                    id: "2",
                    title: "Test Album",
                    artist: "Test Artist",
                    album: "Test Album",
                  },
                ],
                artist: [
                  {
                    id: "3",
                    name: "Test Artist",
                  },
                ],
              },
            },
          }),
      })
    ) as jest.Mock;

    render(<SearchPanel />);

    const searchInput = screen.getByPlaceholderText("Поиск");
    fireEvent.change(searchInput, { target: { value: "Test" } });

    const searchIcon = screen.getByTestId("search-icon");
    fireEvent.click(searchIcon);

    await waitFor(() => {
      const songResult = screen.getByText("Test Song");
      expect(songResult).toBeInTheDocument();

      const albumResult = screen.getByText("Альбом Test Album");
      expect(albumResult).toBeInTheDocument();

      const artistResult = screen.getByText("Исполнитель Test Artist");
      expect(artistResult).toBeInTheDocument();
    });
  });

  test("displays 'Ничего не найдено' when no results are found", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              searchResult3: {
                song: [],
                album: [],
                artist: [],
              },
            },
          }),
      })
    ) as jest.Mock;

    render(<SearchPanel />);

    const searchInput = screen.getByPlaceholderText("Поиск");
    fireEvent.change(searchInput, { target: { value: "Test" } });

    const searchIcon = screen.getByTestId("search-icon");
    fireEvent.click(searchIcon);

    await waitFor(() => {
      const noResults = screen.getByText("Ничего не найдено");
      expect(noResults).toBeInTheDocument();
    });
  });

  test("navigates to correct page when a result is selected", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              searchResult3: {
                song: [
                  {
                    id: "1",
                    title: "Test Song",
                    artist: "Test Artist",
                    album: "Test Album",
                  },
                ],
                album: [],
                artist: [],
              },
            },
          }),
      })
    ) as jest.Mock;

    render(<SearchPanel />);

    const searchInput = screen.getByPlaceholderText("Поиск");
    fireEvent.change(searchInput, { target: { value: "Test" } });

    const searchIcon = screen.getByTestId("search-icon");
    fireEvent.click(searchIcon);

    await waitFor(() => {
      const songResult = screen.getByText("Test Song");
      fireEvent.click(songResult);

      expect(mockPush).toHaveBeenCalledWith("/track/1");
    });
  });
});
