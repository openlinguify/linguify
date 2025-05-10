import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { useFocusManagement } from '../hooks/useFocusManagement';
import FocusTrap from '../components/FocusTrap';

// Simple test component to test focus management
const TestComponent = () => {
  const { containerRef } = useFocusManagement({
    trapFocus: true,
    autoFocus: true
  });

  return (
    <div ref={containerRef as React.RefObject<HTMLDivElement>} data-testid="container">
      <input data-testid="input-1" />
      <button data-testid="button-1">Button 1</button>
      <a href="#" data-testid="link">Link</a>
      <button data-testid="button-2">Button 2</button>
    </div>
  );
};

// Test FocusTrap component
const TestFocusTrap = () => {
  return (
    <FocusTrap>
      <div data-testid="trap-container">
        <input data-testid="trap-input-1" />
        <button data-testid="trap-button-1">Button 1</button>
        <button data-testid="trap-button-2">Button 2</button>
      </div>
    </FocusTrap>
  );
};

describe('Focus Management', () => {
  test('useFocusManagement hook should auto-focus first element', async () => {
    render(<TestComponent />);
    
    // First element should be focused
    await waitFor(() => {
      expect(screen.getByTestId('input-1')).toHaveFocus();
    });
  });

  test('FocusTrap should trap focus within itself', async () => {
    render(<TestFocusTrap />);
    
    const user = userEvent.setup();
    
    // First element should be focused on mount
    await waitFor(() => {
      expect(screen.getByTestId('trap-input-1')).toHaveFocus();
    });
    
    // Tab should move to next element
    await user.tab();
    expect(screen.getByTestId('trap-button-1')).toHaveFocus();
    
    // Tab again should move to last element
    await user.tab();
    expect(screen.getByTestId('trap-button-2')).toHaveFocus();
    
    // Tab from last element should loop back to first element
    await user.tab();
    expect(screen.getByTestId('trap-input-1')).toHaveFocus();
    
    // Shift+Tab from first element should go to last element
    await user.keyboard('{Shift>}{Tab}{/Shift}');
    expect(screen.getByTestId('trap-button-2')).toHaveFocus();
  });
});