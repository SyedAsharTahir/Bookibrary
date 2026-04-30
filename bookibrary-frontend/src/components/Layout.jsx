import React from 'react';
import Navbar from './Navbar';

const Layout = ({ children }) => {
  return (
    // These classes now pull from your config!
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main className="max-w-7xl mx-auto p-6">
        {children}
      </main>
    </div>
  );
};

export default Layout;