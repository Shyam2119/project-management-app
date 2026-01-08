import { useState } from 'react';
import { userAPI } from '../../services/api';
import { X, Copy, Check } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function CreateUserModal({ isOpen, onClose, onSuccess }) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [createdUser, setCreatedUser] = useState(null);
  const [copied, setCopied] = useState(false);

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    role: 'employee',
    skills: '',
    weekly_capacity: 40,
    temp_password: 'Welcome@123'
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await userAPI.create(formData);

      if (response.data.status === 'success') {
        setCreatedUser(response.data.data);
      }
    } catch (err) {
      console.error('User creation error:', err);
      console.error('Error response:', err.response?.data);
      setError(err.response?.data?.message || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (createdUser) {
      onSuccess();
    }
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      role: 'employee',
      skills: '',
      weekly_capacity: 40,
      temp_password: 'Welcome@123'
    });
    setCreatedUser(null);
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 dark:text-gray-100 rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {createdUser ? 'User Created Successfully!' : 'Create New User'}
          </h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {!createdUser ? (
          // Create User Form
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Role
              </label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              >
                {user?.role === 'admin' && (
                  <option value="teamleader">Team Leader</option>
                )}
                <option value="employee">Employee</option>
              </select>
            </div>

            {/* First Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                First Name *
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
            </div>

            {/* Last Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Last Name *
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Phone
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            {/* Skills */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Skills (comma-separated)
              </label>
              <input
                type="text"
                name="skills"
                value={formData.skills}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="React, Node.js, Python"
              />
            </div>

            {/* Weekly Capacity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Weekly Capacity (hours)
              </label>
              <input
                type="number"
                name="weekly_capacity"
                value={formData.weekly_capacity}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                min="1"
                max="60"
              />
            </div>

            {/* Temporary Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Temporary Password
              </label>
              <input
                type="text"
                name="temp_password"
                value={formData.temp_password}
                onChange={handleChange}
                className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                User will be asked to change this on first login
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 btn btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Creating...' : 'Create User'}
              </button>
            </div>
          </form>
        ) : (
          // Success View
          <div className="p-6 space-y-4">
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-green-900 dark:text-green-100">User Created</h3>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                    {createdUser.user.full_name} has been added to the system.
                  </p>
                </div>
              </div>
            </div>

            {/* User Details */}
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                  Email
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={createdUser.user.email}
                    readOnly
                    className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white flex-1"
                  />
                  <button
                    onClick={() => copyToClipboard(createdUser.user.email)}
                    className="btn btn-secondary dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300 p-2"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                  Temporary Password
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={createdUser.temp_password}
                    readOnly
                    className="input dark:bg-gray-700 dark:border-gray-600 dark:text-white flex-1 font-mono"
                  />
                  <button
                    onClick={() => copyToClipboard(createdUser.temp_password)}
                    className="btn btn-secondary dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300 p-2"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  <strong>Important:</strong> Share these credentials with the user securely.
                  They will be prompted to change their password on first login.
                </p>
              </div>
            </div>

            {/* Close Button */}
            <button
              onClick={handleClose}
              className="w-full btn btn-primary"
            >
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  );
}