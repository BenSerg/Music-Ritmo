import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { Input } from "@/shared/input";

describe("Input Component", () => {
  test("renders input with default props", () => {
    render(<Input />);
    const input = screen.getByRole("textbox");
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("type", "text");
    expect(input).not.toBeDisabled();
    expect(input).not.toHaveAttribute("required");
    expect(input).toHaveAttribute("maxLength", "64");
    expect(input).toHaveAttribute("minLength", "5");
  });

  test("applies custom props", () => {
    render(
      <Input
        type="email"
        name="email"
        placeholder="Enter your email"
        value="test@example.com"
        disabled
        required
      />
    );
    const input = screen.getByRole("textbox");
    expect(input).toHaveAttribute("type", "email");
    expect(input).toHaveAttribute("name", "email");
    expect(input).toHaveAttribute("placeholder", "Enter your email");
    expect(input).toHaveValue("test@example.com");
    expect(input).toBeDisabled();
    expect(input).toHaveAttribute("required");
  });

  test("handles onChange event", () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "new value" } });
    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(handleChange).toHaveBeenCalledWith(
      expect.objectContaining({
        target: expect.objectContaining({ value: "new value" }),
      })
    );
  });

  test("handles onBlur event", () => {
    const handleBlur = jest.fn();
    render(<Input onBlur={handleBlur} />);
    const input = screen.getByRole("textbox");
    fireEvent.blur(input);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  test("handles onFocus event", () => {
    const handleFocus = jest.fn();
    render(<Input onFocus={handleFocus} />);
    const input = screen.getByRole("textbox");
    fireEvent.focus(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);
  });

  test("applies error class when error prop is true", () => {
    render(<Input error />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("input_error");
  });

  test("applies custom className", () => {
    render(<Input className="custom-class" />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("custom-class");
  });

  test("enforces minLength constraint", () => {
    render(<Input minLength={5} />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveAttribute("minLength", "5");
  });

  test("enforces maxLength constraint", () => {
    render(<Input maxLength={64} />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveAttribute("maxLength", "64");
  });

  test("renders input with empty value", () => {
    render(<Input value="" />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveValue("");
  });

  test("renders input with long value", () => {
    const longValue = "a".repeat(64);
    render(<Input value={longValue} />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveValue(longValue);
  });
});
