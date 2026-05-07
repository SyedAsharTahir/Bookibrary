import React, { useEffect, useState } from "react";
import API from "../api/axios";

function Home() {
    const [stats, setStats] = useState({ books: 0, members: 0, borrowings: 0, reservations: 0, fines: 0 });
    const [displayed, setDisplayed] = useState('');
    const fullText = "Welcome to Bookibrary 📚";

    useEffect(() => {
        let i = 0;
        const interval = setInterval(() => {
            setDisplayed(fullText.slice(0, i + 1));
            i++;
            if (i === fullText.length) clearInterval(interval);
        }, 80);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        API.get('books/').then(r => setStats(s => ({ ...s, books: r.data.length }))).catch(() => {});
        API.get('members/').then(r => setStats(s => ({ ...s, members: r.data.length }))).catch(() => {});
        API.get('borrowings/').then(r => setStats(s => ({ ...s, borrowings: r.data.length }))).catch(() => {});
        API.get('reservations/').then(r => setStats(s => ({ ...s, reservations: r.data.length }))).catch(() => {});
        API.get('fines/').then(r => setStats(s => ({ ...s, fines: r.data.length }))).catch(() => {});
    }, []);

    const cards = [
        { label: "Total Books", value: stats.books, icon: "📚" },
        { label: "Total Members", value: stats.members, icon: "👥" },
        { label: "Active Borrowings", value: stats.borrowings, icon: "📖" },
        { label: "Reservations", value: stats.reservations, icon: "🔖" },
        { label: "Fines Issued", value: stats.fines, icon: "💰" },
    ];

    return (
        <div>
            <div className="mb-10 rounded-2xl border border-border bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-500 px-8 py-16 text-center text-white shadow-lg">
                <h1 className="text-4xl md:text-5xl font-bold mb-3 min-h-[3rem]">
                    {displayed}<span className="animate-pulse">|</span>
                </h1>
                <p className="text-white/85 text-lg">Your modern library management system</p>
            </div>

            <h2 className="text-2xl font-bold mb-6">Library Overview</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                {cards.map(card => (
                    <div key={card.label} className="rounded-xl border border-border bg-card p-6 shadow-sm hover:shadow-md transition">
                        <span className="text-4xl mb-2">{card.icon}</span>
                        <span className="text-3xl font-bold text-slate-800">{card.value}</span>
                        <span className="text-sm mt-1 text-slate-500">{card.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Home;