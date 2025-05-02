import React from "react";
import { render, screen } from "@testing-library/react";
import { Container } from "@/shared/container";

jest.mock("../src/shared/arrow-back", () => ({
  ArrowBack: jest.fn(({ className, link }) => (
    <div data-testid="arrow-back" className={className} data-link={link} />
  )),
}));

describe("Container Component", () => {
  test("renders container with children", () => {
    render(<Container>Test Content</Container>);
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  test("applies custom styles", () => {
    const customStyle = { backgroundColor: "red" };
    render(<Container style={customStyle} />);
    const container = screen.getByTestId("container");
    expect(container).toHaveStyle("background-color: red");
  });

  test("applies default direction (column)", () => {
    render(<Container />);
    const container = screen.getByTestId("container");
    expect(container).toHaveClass("column");
  });

  test("applies row direction", () => {
    render(<Container direction="row" />);
    const container = screen.getByTestId("container");
    expect(container).toHaveClass("row");
  });

  test("renders ArrowBack when arrow prop is true", () => {
    render(<Container arrow={true} link_arrow="/back" />);
    const arrowBack = screen.getByTestId("arrow-back");
    expect(arrowBack).toBeInTheDocument();
    expect(arrowBack).toHaveClass("arrow");
    expect(arrowBack).toHaveAttribute("data-link", "/back");
  });

  test("does not render ArrowBack when arrow prop is false", () => {
    render(<Container arrow={false} />);
    const arrowBack = screen.queryByTestId("arrow-back");
    expect(arrowBack).not.toBeInTheDocument();
  });

  test("renders container without children", () => {
    render(<Container />);
    const container = screen.getByTestId("container");
    expect(container).toBeEmptyDOMElement();
  });

  test("renders container with long text", () => {
    const longText = "This is a very long text inside the container";
    render(<Container>{longText}</Container>);
    expect(screen.getByText(longText)).toBeInTheDocument();
  });
});
