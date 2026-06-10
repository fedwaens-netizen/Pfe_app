import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Navbar from './components/Navbar';

import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import AdminDashboard from './pages/AdminDashboard';
import Home from './pages/Home';
import ForYou from './pages/ForYou';
import Destination from './pages/Destination';
import Hotels from './pages/Hotels';
import Taxis from './pages/Taxis';
import MyBookings from './pages/MyBookings';
import Currency from './pages/Currency';
import History from './pages/History';
import Profile from './pages/Profile';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function AppContent() {
  const { user } = useContext(AuthContext);

  return (
    <>
      <Navbar />
      <div className="page-wrapper">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/for-you" 
            element={
              <ProtectedRoute>
                <ForYou />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/destination/:name" 
            element={
              <ProtectedRoute>
                <Destination />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/hotels" 
            element={
              <ProtectedRoute>
                <Hotels />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/taxis" 
            element={
              <ProtectedRoute>
                <Taxis />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/my-bookings" 
            element={
              <ProtectedRoute>
                <MyBookings />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/currency" 
            element={
              <ProtectedRoute>
                <Currency />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/history" 
            element={
              <ProtectedRoute>
                <History />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
