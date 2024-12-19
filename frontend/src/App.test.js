import { render, screen } from '@testing-library/react';
import App from './App';

test('renders header title', () => {
  render(<App />);
  const headerElement = screen.getByText(/Cours de Langues/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders sidebar', () => {
  render(<App />);
  const sidebarElement = screen.getByRole('navigation');
  expect(sidebarElement).toBeInTheDocument();
});
