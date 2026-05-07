import React, { useEffect, useState } from "react";
import axios from "../api/axios";

function Dashboard() {
  const [stats, setStats] = useState({
    total_books: 0,
    total_members: 0,
    active_borrowings: 0,
    overdue_books: 0,
    total_fines: 0,
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await axios.get("/dashboard/stats/");
      setStats(res.data);
    } catch (err) {
      console.log("Dashboard error:", err);
    }
  };

  const Card = ({ title, value, color }) => (
    <div className={`p-6 rounded-xl shadow-md text-white ${color}`}>
      <h2 className="text-sm opacity-80">{title}</h2>
      <p className="text-2xl font-bold mt-2">{value}</p>
    </div>
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">📊 Library Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card title="Total Books" value={stats.total_books} color="bg-blue-600" />
        <Card title="Total Members" value={stats.total_members} color="bg-green-600" />
        <Card title="Active Borrowings" value={stats.active_borrowings} color="bg-purple-600" />
        <Card title="Overdue Books" value={stats.overdue_books} color="bg-red-600" />
        <Card title="Total Fines" value={`Rs ${stats.total_fines}`} color="bg-yellow-600" />
      </div>
    </div>
  );
}

export default Dashboard;