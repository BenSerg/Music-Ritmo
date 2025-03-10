import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { Tracklist } from "@/widgets/track-list";

jest.mock("next/link", () => {
  return jest.fn(({ children, href }) => <a href={href}>{children}</a>);
});

describe("Tracklist Component", () => {
  const mockOnFavouriteToggle = jest.fn();
  const mockOnRemove = jest.fn();

  const defaultProps = {
    name: "Test Track",
    name_link: "/track/test",
    artist: "Test Artist",
    artist_link: "/artist/test",
    favourite: "true",
    time: 150,
    showRemoveButton: true,
    onFavouriteToggle: mockOnFavouriteToggle,
    onRemove: mockOnRemove,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders track with name, artist, and time", () => {
    render(<Tracklist {...defaultProps} />);

    const trackName = screen.getByText("Test Track");
    expect(trackName).toBeInTheDocument();

    const artistName = screen.getByText("Test Artist");
    expect(artistName).toBeInTheDocument();

    const time = screen.getByText("02:30");
    expect(time).toBeInTheDocument();
  });

  test("renders links for track name and artist", () => {
    render(<Tracklist {...defaultProps} />);

    const trackLink = screen.getByRole("link", { name: "Test Track" });
    expect(trackLink).toHaveAttribute("href", "/track/test");

    const artistLink = screen.getByRole("link", { name: "Test Artist" });
    expect(artistLink).toHaveAttribute("href", "/artist/test");
  });

  test("renders filled star if favourite is true", () => {
    render(<Tracklist {...defaultProps} favourite="true" />);

    const filledStar = screen.getByTestId("filled-star");
    expect(filledStar).toBeInTheDocument();
  });

  test("renders empty star if favourite is false", () => {
    render(<Tracklist {...defaultProps} favourite="false" />);

    const emptyStar = screen.getByTestId("empty-star");
    expect(emptyStar).toBeInTheDocument();
  });

  test("calls onFavouriteToggle when favourite icon is clicked", () => {
    render(<Tracklist {...defaultProps} />);

    const favouriteIcon = screen.getByTestId("favourite-icon");
    fireEvent.click(favouriteIcon);

    expect(mockOnFavouriteToggle).toHaveBeenCalled();
  });

  test("renders remove button if showRemoveButton is true", () => {
    render(<Tracklist {...defaultProps} showRemoveButton={true} />);

    const removeButton = screen.getByTestId("remove-button");
    expect(removeButton).toBeInTheDocument();
  });

  test("does not render remove button if showRemoveButton is false", () => {
    render(<Tracklist {...defaultProps} showRemoveButton={false} />);

    const removeButton = screen.queryByTestId("remove-button");
    expect(removeButton).not.toBeInTheDocument();
  });

  test("calls onRemove when remove button is clicked", () => {
    render(<Tracklist {...defaultProps} showRemoveButton={true} />);

    const removeButton = screen.getByTestId("remove-button");
    fireEvent.click(removeButton);

    expect(mockOnRemove).toHaveBeenCalled();
  });
});
