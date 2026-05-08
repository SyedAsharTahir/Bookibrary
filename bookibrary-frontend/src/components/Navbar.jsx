import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { getRole, getName, logOut } from "../auth";

function Navbar({ onToggle }) {
  const [open, setOpen] = useState(true);

  const role = getRole();
  const name = getName();

  const isAdmin = role === "admin";
  const isAdminOrLibrarian = role === "admin" || role === "librarian";
  const linkBase =
    "flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-200 relative";
  const active = "bg-indigo-600 text-white shadow-md";
  const inactive = "text-gray-300 hover:bg-gray-800 hover:text-white";

  const linkClass = ({ isActive }) =>
    `${linkBase} ${isActive ? active : inactive}`;

  return (
    <div
      className={`h-screen bg-gray-900 text-white flex flex-col justify-between transition-all duration-300 fixed left-0 top-0 z-50 ${
        open ? "w-64" : "w-20"
      }`}
    >
      <div>
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-800">
          <span className="font-bold text-indigo-400">
            {open ? "Bookibrary" : "BK"}
          </span>

          <button
            onClick={() => {
              setOpen(!open);
              if (onToggle) onToggle();
            }}
            className="text-gray-400 hover:text-white transition"
          >
            ☰
          </button>
        </div>

        <nav className="mt-4 space-y-2">
          <NavLink to="/" className={linkClass}>
            🏠 {open && "Home"}
          </NavLink>
          {isAdminOrLibrarian && (
            <NavLink to="/dashboard" className={linkClass}>
              📊 {open && "Dashboard"}
            </NavLink>
          )}
          <NavLink to="/books" className={linkClass}>
            📚 {open && "Books"}
          </NavLink>
          <NavLink to="/chatbot" className={linkClass}>
            💬 {open && "AI Chat"}
          </NavLink>
          <NavLink to="/reservations" className={linkClass}>
            📌 {open && "Reservations"}
          </NavLink>
          <NavLink to="/borrowing" className={linkClass}>
            🔄 {open && "Borrowing"}
          </NavLink>
          <NavLink to="/notifications" className={linkClass}>
            🔔 {open && "Notifications"}
          </NavLink>

          {isAdminOrLibrarian && (
            <NavLink to="/fines" className={linkClass}>
              💰 {open && "Fines"}
            </NavLink>
          )}
          {isAdmin && (
            <NavLink to="/members" className={linkClass}>
              👥 {open && "Members"}
            </NavLink>
          )}
          {isAdmin && (
            <NavLink to="/finepolicy" className={linkClass}>
              📜 {open && "Fine Policy"}
            </NavLink>
          )}
          {isAdminOrLibrarian && (
            <NavLink to="/borrowinghistory" className={linkClass}>
              📈 {open && "History"}
            </NavLink>
          )}

          <NavLink to="/category" className={linkClass}>
            🗂 {open && "Category"}
          </NavLink>
          {isAdminOrLibrarian && (
            <>
              <NavLink to="/authors" className={linkClass}>
                ✍️ {open && "Authors"}
              </NavLink>
              <NavLink to="/publishers" className={linkClass}>
                🏢 {open && "Publishers"}
              </NavLink>
            </>
          )}
        </nav>
      </div>

      <div className="border-t border-gray-800 p-4">
        {open && (
          <div className="text-sm text-gray-400 mb-2">
            👤 {name} ({role})
          </div>
        )}

        <button
          onClick={logOut}
          className="w-full bg-red-600 hover:bg-red-700 text-white py-2 rounded-lg transition"
        >
          {open ? "Logout" : "⏻"}
        </button>
      </div>
    </div>
  );
}

export default Navbar;