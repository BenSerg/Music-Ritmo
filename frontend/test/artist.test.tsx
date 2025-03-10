import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { Artist } from "@/entities/artist";

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

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    blob: () => Promise.resolve(new Blob()),
  })
) as jest.Mock;

global.URL.createObjectURL = jest.fn(() => "mock-url");

describe("Artist Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, "log").mockImplementation(() => {});
    jest.spyOn(console, "error").mockImplementation(() => {});

    jest.spyOn(Math, "random").mockReturnValue(0.1);
  });

  afterEach(() => {
    jest.spyOn(Math, "random").mockRestore();
  });

  test("renders artist with name and link", () => {
    render(<Artist name="Test Artist" link="/artist/test" />);

    const artistName = screen.getByText("Test Artist");
    expect(artistName).toBeInTheDocument();

    const artistLink = screen.getByRole("link");
    expect(artistLink).toHaveAttribute("href", "/artist/test");
  });

  test("applies random background color", () => {
    render(<Artist name="Test Artist" link="/artist/test" />);

    const artistElement = screen.getByRole("link");
    expect(artistElement).toHaveStyle("background-color: #949E7B");
  });

  test("renders cover art if coverArt is provided", async () => {
    render(<Artist name="Test Artist" link="/artist/test" coverArt="123" />);

    await waitFor(() => {
      const coverImage = screen.getByRole("img", { name: "Test Artist cover" });
      expect(coverImage).toBeInTheDocument();
      expect(coverImage).toHaveAttribute("src", "mock-url");
    });
  });

  test("does not render cover art if coverArt is not provided", () => {
    render(<Artist name="Test Artist" link="/artist/test" />);

    const coverImage = screen.queryByRole("img");
    expect(coverImage).not.toBeInTheDocument();
  });

  test("handles cover art fetch error", async () => {
    global.fetch = jest.fn(() =>
      Promise.reject("Failed to fetch")
    ) as jest.Mock;
    render(<Artist name="Test Artist" link="/artist/test" coverArt="123" />);

    await waitFor(() => {
      const coverImage = screen.queryByRole("img");
      expect(coverImage).not.toBeInTheDocument();
    });
  });
});
