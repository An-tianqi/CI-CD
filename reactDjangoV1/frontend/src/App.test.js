// Home.test.js

import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import Home from './Home';

describe('Home component', () => {
  test('renders username and password input fields', () => {
    const { getByPlaceholderText } = render(<Home />);

    // Vérifier que les champs de formulaire sont rendus
    expect(getByPlaceholderText('Username')).toBeInTheDocument();
    expect(getByPlaceholderText('Password')).toBeInTheDocument();
  });

  test('calls onLogin when Login button is clicked', () => {
    // Mock de la fonction onLogin
    const mockOnLogin = jest.fn();

    const { getByPlaceholderText, getByText } = render(<Home onLogin={mockOnLogin} />);

    // Simuler la saisie dans les champs
    fireEvent.change(getByPlaceholderText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(getByPlaceholderText('Password'), { target: { value: 'testpassword' } });

    // Simuler le clic sur le bouton Login
    fireEvent.click(getByText('Login'));

    // Vérifier que la fonction onLogin a été appelée avec le bon username
    expect(mockOnLogin).toHaveBeenCalledWith('testuser');
  });

  test('does not call onLogin when Register button is clicked', () => {
    // Mock de la fonction onLogin
    const mockOnLogin = jest.fn();

    const { getByText } = render(<Home onLogin={mockOnLogin} />);

    // Simuler le clic sur le bouton Register
    fireEvent.click(getByText('Register'));

    // Vérifier que la fonction onLogin n'a pas été appelée
    expect(mockOnLogin).not.toHaveBeenCalled();
  });
});
