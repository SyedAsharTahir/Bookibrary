import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

const Layout = () => {
  const [navbarOpen, setNavbarOpen] = useState(true);
  
  useEffect(() => {
    // Listen for navbar state changes
    const handleNavbarChange = () => {
      setNavbarOpen(!navbarOpen);
    };
    
    // This is a simple solution - in a real app you'd use context or state management
    window.addEventListener('navbar-toggle', handleNavbarChange);
    
    return () => {
      window.removeEventListener('navbar-toggle', handleNavbarChange);
    };
  }, [navbarOpen]);

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      <Navbar onToggle={() => setNavbarOpen(!navbarOpen)} />
      <main className="flex-1 p-6 bg-background" style={{ marginLeft: navbarOpen ? '256px' : '80px', transition: 'margin-left 0.3s' }}>
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;