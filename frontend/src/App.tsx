import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login/Login';
import ForgotPassword from './pages/ForgotPassword/ForgotPassword';
import SignUp from './pages/SignUp/SignUp';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/" element={<Login />} /> {/* Default route */}
      </Routes>
    </Router>
  );
};

export default App;