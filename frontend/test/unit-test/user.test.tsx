import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { User } from "@/entities/user";

jest.mock("../src/app/auth-context", () => ({
  useAuth: jest.fn(() => ({
    user: "testUser",
    password: "testPassword",
    logout: jest.fn(),
  })),
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

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    headers: new Headers({ "Content-Type": "image/png" }),
    blob: () => Promise.resolve(new Blob()),
  })
) as jest.Mock;

global.URL.createObjectURL = jest.fn(() => "mock-url");

describe("User Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders user with avatar and name", async () => {
    render(<User />);
    const userName = screen.getByText("testUser");
    expect(userName).toBeInTheDocument();

    await waitFor(() => {
      const avatarImage = screen.getByAltText("User Avatar");
      expect(avatarImage).toBeInTheDocument();
    });
  });

  test("toggles menu on avatar click", async () => {
    render(<User />);
    const avatar = screen.getByAltText("User Avatar");

    fireEvent.click(avatar);
    const menu = screen.getByTestId("user-menu");
    expect(menu).toBeInTheDocument();

    fireEvent.click(avatar);
    expect(menu).not.toBeInTheDocument();
  });

  test("fetches avatar from backend", async () => {
    render(<User />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/rest/getAvatar?username=testUser&u=testUser&p=testPassword"
      );
    });

    const avatarImage = screen.getByAltText("User Avatar");
    expect(avatarImage).toBeInTheDocument();
  });

  test("renders default avatar if fetch fails", async () => {
    global.fetch = jest.fn(() =>
      Promise.reject("Failed to fetch")
    ) as jest.Mock;
    render(<User />);

    await waitFor(() => {
      const defaultAvatar = screen.getByAltText("User Avatar");
      expect(defaultAvatar).toHaveAttribute("src", "/images/logo.svg");
    });
  });
});
