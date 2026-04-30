import React, { useState } from "react";
import {Link} from 'react-router-dom';
import { getRole,getName,logOut } from "../auth";

function Navbar()
{
  const [mobileOpen,setMobileOpen]=useState(false);
  const role=getRole();
  const name=getName();
        const linkClass = "text-gray-300 hover:text-white border-b-2 border-transparent hover:border-gray-300 px-1 pt-1 inline-flex items-center text-sm font-medium";
    const mobileLinkClass = "text-gray-300 hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium";

    return (
        <nav className="bg-gray-900 text-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <span className="text-xl font-bold">Bookibrary</span>
                        <div className="hidden md:flex md:ml-6 md:space-x-8">
                            <Link to="/" className={linkClass}>Home</Link>
                            <Link to="/books" className={linkClass}>Books</Link>
                            <Link to="/reservations" className={linkClass}>Reservations</Link>
                            <Link to="/borrowing" className={linkClass}>Borrowing</Link>
                            <Link to="/notifications" className={linkClass}>Notifications</Link>
                            {(role === 'admin' || role === 'librarian') && (
                               <>
                                    <Link to="/fines" className={linkClass}>Fines</Link>
                                    <Link to="/members" className={linkClass}>Members</Link>
                                    {/* ADD THESE FOR PROJECT COMPLIANCE */}
                                    <Link to="/finepolicy" className={linkClass}>Fine Policy</Link>
                                    <Link to="/borrowinghistory" className={linkClass}>History</Link>
                                </>
                            )}
                        </div>
                    </div>

                    <div className="hidden md:flex items-center gap-4">
                        <span className="text-sm text-gray-300">👤 {name} ({role})</span>
                        <button onClick={logOut}
                            className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md text-sm transition">
                            Logout
                        </button>
                    </div>

                    {/* Mobile menu button */}
                    <div className="flex items-center md:hidden">
                        <button onClick={() => setMobileOpen(!mobileOpen)} className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none">
                            <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            {mobileOpen && (
                <div className="md:hidden px-2 pt-2 pb-3 space-y-1">
                    <Link to="/" className={mobileLinkClass}>Home</Link>
                    <Link to="/books" className={mobileLinkClass}>Books</Link>
                    <Link to="/reservations" className={mobileLinkClass}>Reservations</Link>
                    <Link to="/borrowing" className={mobileLinkClass}>Borrowing</Link>
                    {(role === 'admin' || role === 'librarian') && (
                         <>
                                    <Link to="/fines" className={linkClass}>Fines</Link>
                                    <Link to="/members" className={linkClass}>Members</Link>
                                    {/* ADD THESE FOR PROJECT COMPLIANCE */}
                                    <Link to="/finepolicy" className={linkClass}>Fine Policy</Link>
                                    <Link to="/borrowinghistory" className={linkClass}>History</Link>
                        </>
                    )}
                    <button onClick={logOut} className="w-full text-left text-red-400 hover:bg-gray-700 block px-3 py-2 rounded-md text-base font-medium">
                        Logout
                    </button>
                </div>
            )}
        </nav>
    );
}

export default Navbar;