import React from "react";
import { render, screen } from "@testing-library/react";
import { Header } from "@/widgets/header";

jest.mock("../src/shared/logo", () => ({
  Logo: jest.fn(() => <div data-testid="logo" />),
}));

jest.mock("../src/entities/user", () => ({
  User: jest.fn(() => <div data-testid="user" />),
}));

jest.mock("next/link", () => {
  return jest.fn(({ children, href }) => (
    <a href={href} data-testid="link">
      {children}
    </a>
  ));
});

describe("Header Component", () => {
  test("renders header with logo, buttons, and user", () => {
    render(<Header />);

    const headerElement = screen.getByTestId("header");
    expect(headerElement).toBeInTheDocument();

    const logoElement = screen.getByTestId("logo");
    expect(logoElement).toBeInTheDocument();

    const links = screen.getAllByTestId("link");
    expect(links).toHaveLength(2);

    expect(links[0]).toHaveAttribute("href", "/playlists");

    expect(links[1]).toHaveAttribute("href", "/favourite-track");

    const userElement = screen.getByTestId("user");
    expect(userElement).toBeInTheDocument();
  });

  test("renders icons correctly", () => {
    render(<Header />);

    const musicIcon = screen.getByRole("img", { name: /music/i });
    expect(musicIcon).toBeInTheDocument();
    expect(musicIcon).toHaveClass("fa-solid", "fa-music");

    const starIcon = screen.getByRole("img", { name: /star/i });
    expect(starIcon).toBeInTheDocument();
    expect(starIcon).toHaveClass("fa-solid", "fa-star");
  });

  test("has correct structure", () => {
    render(<Header />);

    const headerElement = screen.getByTestId("header");
    expect(headerElement.children).toHaveLength(2);

    const logoContainer = headerElement.children[0];
    expect(logoContainer).toHaveClass("header__logo");

    const buttonsContainer = headerElement.children[1];
    expect(buttonsContainer).toHaveClass("header__buttons");
  });
});
