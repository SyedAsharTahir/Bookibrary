//src/ has app.js and pages/ and pages has books.jsx.....
import React from "react";
import { BrowserRouter,Routes,Route, Navigate} from "react-router-dom";
import Navbar from './components/Navbar';
import Books from './pages/Books'; 
import Fines from './pages/Fines';
import Borrowing from './pages/Borrowing';
import Reservation from './pages/Reservations';
import Members from './pages/Members';
import Home from "./pages/Home";
import Login from "./pages/Login";
import Category from "./pages/Category";
import FinePolicy from "./pages/FinePolicy"
import Notification from "./pages/Notifications"
import BorrowingHistory from "./pages/BorrowingHistory";
import Publisher from "./pages/Publisher"; 
import Author from "./pages/Author"; 
import Layout from "./components/Layout";
import { getRole } from "./auth";
function RoleProtection({children,roles}){
  const role=getRole();//get current users role frm jwt token from our helper in auth.js
  if(!roles.includes(role)){return <Navigate to="/" />;}//check if his role is in the allowed roles array,if not redirect to 
  //home page
  return children;//else render page normally
}
function RouteProtection({children}){
   const token=localStorage.getItem('accessToken');
   if(!token){
    return <Navigate to="/login"/>
   }
   return children;

}
//when fine page is visited render whatever exists in the element section
//the roles are passed explicitly and the child is<Fines/> which is apssed implicitly(react takes whatever
// betweent eh role protection tag as child)
//just a convention,could both be done either way
function APP() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/*" element={
          <RouteProtection>
            {/* Layout wraps the inner content so Navbar + styling is consistent */}
            <Layout>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/books" element={<Books />} />
                <Route path="/borrowing" element={<Borrowing />} />
                <Route path="/reservations" element={<Reservation />} /> 
                <Route path="/fines" element={
                  <RoleProtection roles={['admin', 'librarian']}>
                    <Fines /> 
                  </RoleProtection>
                } />
                <Route path="/members" element={
                  <RoleProtection roles={['admin']}>
                    <Members />
                  </RoleProtection>
                } />
                <Route path="/category" element={<Category />} />
                <Route path="/finepolicy" element={
                  <RoleProtection roles={['admin']}><FinePolicy /></RoleProtection>
                } />
                <Route path="/borrowinghistory" element={
                  <RoleProtection roles={['admin', 'librarian']}><BorrowingHistory /></RoleProtection>
                } />
                <Route path="/notifications" element={<Notification />} />
                <Route path="/authors" element={<RoleProtection roles={['admin', 'librarian']}><Author /></RoleProtection>} />
                <Route path="/publishers" element={<RoleProtection roles={['admin', 'librarian']}><Publisher /></RoleProtection>} />
              </Routes>
            </Layout>
          </RouteProtection>
        } />
      </Routes>
    </BrowserRouter>
  )
}
export default APP;