import React from "react";
import { render, screen } from "@testing-library/react";
import { Logo } from "@/shared/logo";

interface ImageProps {
  src: string;
  className: string;
  alt: string;
  width: number;
  height: number;
}

jest.mock("next/image", () => ({
  __esModule: true,
  default: (props: ImageProps) => (
    <img
      src={props.src}
      className={props.className}
      alt={props.alt}
      width={props.width}
      height={props.height}
      data-testid="mock-image"
    />
  ),
}));

describe("Logo Component", () => {
  test("renders logo with default props", () => {
    render(<Logo />);
    const logoElement = screen.getByTestId("logo");
    expect(logoElement).toBeInTheDocument();
    expect(logoElement).toHaveClass("normal");
    expect(screen.getByText("musicRitmo")).toBeInTheDocument();
    const imageElement = screen.getByTestId("mock-image");
    expect(imageElement).toBeInTheDocument();
  });

  test("renders logo with type 'big'", () => {
    render(<Logo type="big" />);
    const logoElement = screen.getByTestId("logo");
    expect(logoElement).toHaveClass("big");
  });

  test("renders image with correct attributes", () => {
    render(<Logo />);
    const imageElement = screen.getByTestId("mock-image");
    expect(imageElement).toHaveAttribute("alt", "logo");
    expect(imageElement).toHaveAttribute("width", "300");
    expect(imageElement).toHaveAttribute("height", "300");
  });

  test("renders logo without text", () => {
    render(<Logo />);
    const textElement = screen.queryByText("musicRitmo");
    expect(textElement).toBeInTheDocument();
  });

  test("renders logo without image", () => {
    render(<Logo />);
    const imageElement = screen.queryByTestId("mock-image");
    expect(imageElement).toBeInTheDocument();
  });
});
