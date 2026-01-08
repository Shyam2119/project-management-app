import { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me');
      if (response.data.status === 'success') {
        const userData = response.data.data;
        if (userData.role) userData.role = userData.role.toLowerCase();
        setUser(userData);
        setIsAuthenticated(true);


      }
    } catch (error) {
      console.error('Error fetching user:', error);
      localStorage.removeItem('token');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);

      if (response.data.status === 'success') {
        const data = response.data.data;
        
        // Check if user selection is required (company login with multiple users)
        if (data.requires_user_selection) {
          return {
            success: true,
            requiresUserSelection: true,
            users: data.users,
            company: data.company
          };
        }

        const { access_token, user: userData } = data;

        // Store token
        localStorage.setItem('token', access_token);

        // Set user data
        setUser(userData);
        setIsAuthenticated(true);

        return { success: true, requiresPasswordSetup: false };
      } else {
        return {
          success: false,
          error: response.data.message || 'Login failed'
        };
      }
    } catch (error) {
      console.error('Login error:', error);

      // Handle different error types
      if (error.response) {
        // Server responded with error
        return {
          success: false,
          error: error.response.data?.message || 'Invalid credentials'
        };
      } else if (error.request) {
        // Request made but no response
        return {
          success: false,
          error: 'Cannot connect to server. Please check if backend is running.'
        };
      } else {
        // Something else happened
        return {
          success: false,
          error: 'An unexpected error occurred'
        };
      }
    }
  };

  const loginWithUserSelection = async (credentials, selectedUserId) => {
    try {
      const response = await api.post('/auth/login', {
        ...credentials,
        user_id: selectedUserId
      });

      if (response.data.status === 'success') {
        const { access_token, user: userData } = response.data.data;

        // Store token
        localStorage.setItem('token', access_token);

        // Set user data
        setUser(userData);
        setIsAuthenticated(true);

        return { success: true, requiresPasswordSetup: false };
      } else {
        return {
          success: false,
          error: response.data.message || 'Login failed'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed'
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      if (response.data.status === 'success') {
        return { 
          success: true, 
          message: response.data.message || 'Registration successful',
          requires_approval: response.data.data?.requires_approval || false
        };
      }
      return {
        success: false,
        error: response.data.message || 'Registration failed'
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/login');
  };

  const updateUserVerification = () => {
    if (user) {
      setUser({ ...user, is_verified: true });
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    loginWithUserSelection,
    register,
    registerAdmin: async (userData) => {
      try {
        const response = await api.post('/auth/register-company', userData);
        if (response.data.status === 'success') {
          return { success: true, message: 'Company registration successful' };
        }
        return {
          success: false,
          error: response.data.message || 'Registration failed'
        };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.message || 'Registration failed'
        };
      }
    },
    logout,
    setUser,
    updateUserVerification
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};