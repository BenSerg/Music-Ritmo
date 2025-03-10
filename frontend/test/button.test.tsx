import React from "react";
import { render, fireEvent, screen } from "@testing-library/react";
import { Button } from "@/shared/button";

describe("Button Component", () => {
  test("renders button with text", () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText("Click Me")).toBeInTheDocument();
  });

  test("applies default class", () => {
    render(<Button />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("normal");
    expect(button).toHaveClass("green");
  });

  test("applies custom class", () => {
    render(<Button className="custom-class" />);
    expect(screen.getByRole("button")).toHaveClass("custom-class");
  });

  test("changes button type", () => {
    render(<Button type="transparent" />);
    expect(screen.getByRole("button")).toHaveClass("transparent");
  });

  test("changes button color", () => {
    render(<Button color="white" />);
    expect(screen.getByRole("button")).toHaveClass("white");
  });

  test("calls onClick handler when clicked", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} />);
    fireEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test("disables button after click", () => {
    render(<Button />);
    const button = screen.getByRole("button");
    fireEvent.click(button);
    expect(button).toBeDisabled();
  });

  test("disables button via disabled prop", () => {
    render(<Button disabled />);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  test("renders button with no children", () => {
    render(<Button />);
    expect(screen.getByRole("button")).toBeEmptyDOMElement();
  });

  test("renders button with long text", () => {
    const longText = "This is a very long text for the button";
    render(<Button>{longText}</Button>);
    expect(screen.getByText(longText)).toBeInTheDocument();
  });
});
