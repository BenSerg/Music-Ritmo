import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import Artist from "@/app/artist/[artistName]/page";
import { useParams, useRouter } from "next/navigation";
import "@testing-library/jest-dom";
import { AuthProvider } from "@/app/auth-context";

jest.mock("next/navigation", () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(),
}));

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
) as jest.Mock;

describe("Artist Component", () => {
  const mockArtistName = "testArtist";

  beforeEach(() => {
    (useParams as jest.Mock).mockReturnValue({ artistName: mockArtistName });

    (useRouter as jest.Mock).mockReturnValue({
      push: jest.fn(),
      replace: jest.fn(),
      pathname: "/",
      query: {},
      asPath: "/",
    });

    jest.clearAllMocks();
  });

  test("shows loading state initially", () => {
    render(
      <AuthProvider>
        <Artist />
      </AuthProvider>
    );
    expect(screen.getByText("Загрузка...")).toBeInTheDocument();
  });

  test("displays artist data when fetched successfully", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              artist: {
                id: "123",
                name: "Test Artist",
                album: [
                  {
                    name: "Test Album",
                    id: "1",
                    genre: "Rock",
                    year: "2021",
                    coverArt: "cover1.jpg",
                  },
                ],
                coverArt: "cover.jpg",
                starred: null,
              },
            },
          }),
      })
    ) as jest.Mock;

    render(
      <AuthProvider>
        <Artist />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Test Artist")).toBeInTheDocument();
      expect(screen.getByText("Test Album")).toBeInTheDocument();
    });
  });

  test("displays error message when artist data fetching fails", async () => {
    global.fetch = jest.fn(() =>
      Promise.reject(new Error("Не удалось получить данные с сервера"))
    ) as jest.Mock;

    render(
      <AuthProvider>
        <Artist />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Загрузка...")).toBeInTheDocument();
    });
  });

  test("displays message when no albums are available", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            "subsonic-response": {
              status: "ok",
              artist: {
                id: "123",
                name: "Test Artist",
                album: [],
                coverArt: "cover.jpg",
                starred: null,
              },
            },
          }),
      })
    ) as jest.Mock;

    render(
      <AuthProvider>
        <Artist />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Test Artist")).toBeInTheDocument();
    });

    expect(screen.queryByText("Test Album")).not.toBeInTheDocument();
  });
});
