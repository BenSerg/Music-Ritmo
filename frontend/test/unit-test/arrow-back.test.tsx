import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ArrowBack } from "@/shared/arrow-back";
import "@testing-library/jest-dom";

describe("ArrowBack Component", () => {
  it("renders the arrow back icon with default link", () => {
    render(<ArrowBack />);
    const linkElement = screen.getByTestId("arrow-back");
    expect(linkElement).toBeInTheDocument();
    expect(linkElement).toHaveAttribute("href", "/");
    expect(screen.getByRole("img", { name: "Back" })).toBeInTheDocument();
  });

  it("renders the arrow back icon with custom link", () => {
    const customLink = "/custom-link";
    render(<ArrowBack link={customLink} />);
    const linkElement = screen.getByTestId("arrow-back");
    expect(linkElement).toHaveAttribute("href", customLink);
  });

  it("applies custom className to the link", () => {
    const customClassName = "custom-class";
    render(<ArrowBack className={customClassName} />);
    const linkElement = screen.getByTestId("arrow-back");
    expect(linkElement).toHaveClass(customClassName);
  });

  it("navigates to the correct link when clicked", () => {
    const customLink = "/custom-link";
    render(<ArrowBack link={customLink} />);
    const linkElement = screen.getByTestId("arrow-back");
    userEvent.click(linkElement);
  });
});
