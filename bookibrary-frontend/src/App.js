import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Books from "./pages/Books";
import Fines from "./pages/Fines";
import Borrowing from "./pages/Borrowing";
import Reservation from "./pages/Reservations";
import Members from "./pages/Members";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Category from "./pages/Category";
import FinePolicy from "./pages/FinePolicy";
import Notification from "./pages/Notifications";
import BorrowingHistory from "./pages/BorrowingHistory";
import Publisher from "./pages/Publisher"; 
import Author from "./pages/Author"; 
import Layout from "./components/Layout";
import Dashboard from "./pages/DashBoard";
import Recommendations from "./pages/Recommendations";
import { getRole } from "./auth";

function RoleProtection({ children, roles }) {
  const role = getRole();
  if (!roles || !roles.includes(role)) {
    return <Navigate to="/" />;
  }
  return children;
}

function RouteProtection({ children }) {
  const token = localStorage.getItem("accessToken");
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <RouteProtection>
              <Layout />
            </RouteProtection>
          }
        >
          <Route index element={<Home />} />
          <Route
            path="dashboard"
            element={
              <RoleProtection roles={["admin", "librarian"]}>
                <Dashboard />
              </RoleProtection>
            }
          />
          <Route path="books" element={<Books />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="borrowing" element={<Borrowing />} />
          <Route path="reservations" element={<Reservation />} />
          <Route
            path="fines"
            element={
              <RoleProtection roles={["admin", "librarian"]}>
                <Fines />
              </RoleProtection>
            }
          />
          <Route
            path="members"
            element={
              <RoleProtection roles={["admin"]}>
                <Members />
              </RoleProtection>
            }
          />
          <Route path="category" element={<Category />} />
          <Route
            path="finepolicy"
            element={
              <RoleProtection roles={["admin"]}>
                <FinePolicy />
              </RoleProtection>
            }
          />
          <Route
            path="borrowinghistory"
            element={
              <RoleProtection roles={["admin", "librarian"]}>
                <BorrowingHistory />
              </RoleProtection>
            }
          />
          <Route path="notifications" element={<Notification />} />
          <Route
            path="authors"
            element={
              <RoleProtection roles={["admin", "librarian"]}>
                <Author />
              </RoleProtection>
            }
          />
          <Route
            path="publishers"
            element={
              <RoleProtection roles={["admin", "librarian"]}>
                <Publisher />
              </RoleProtection>
            }
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;