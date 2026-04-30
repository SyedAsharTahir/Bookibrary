import React, { useEffect, useState } from "react";
import API from "../api/axios";

const BorrowingHistory = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = async () => {
        try {
            setLoading(true);
            const response = await API.get('borrowinghistory/');
            setHistory(response.data);
        } catch (error) {
            console.error("Error fetching borrowing history:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchHistory(); }, []);

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">📁 Borrowing Archive</h1>
                <button onClick={fetchHistory}
                    className="border border-border px-4 py-2 text-sm font-medium hover:bg-muted">
                    🔄 Refresh
                </button>
            </div>

            <div className="border border-border shadow-md overflow-x-auto">
                <table className="min-w-full">
                    <thead>
                        <tr className="bg-primary text-white text-sm">
                            <th className="p-3 border-r border-border text-left">Book</th>
                            <th className="p-3 border-r border-border text-left">Member</th>
                            <th className="p-3 border-r border-border text-center">Borrow Date</th>
                            <th className="p-3 border-r border-border text-center">Return Date</th>
                            <th className="p-3 text-right">Fine Charged</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan="5" className="p-8 text-center text-sm">Loading archive...</td>
                            </tr>
                        ) : history.length > 0 ? (
                            history.map(item => (
                                <tr key={item.id} className="border-b border-border text-sm hover:bg-muted">
                                    <td className="p-3 border-r border-border">
                                        <div className="font-medium">{item.book_title}</div>
                                        <div className="text-xs text-gray-400">ID: {item.id}</div>
                                    </td>
                                    <td className="p-3 border-r border-border">{item.member_name}</td>
                                    <td className="p-3 border-r border-border text-center">{item.borrowDate}</td>
                                    <td className="p-3 border-r border-border text-center">{item.returnDate}</td>
                                    <td className="p-3 text-right font-medium">
                                        {item.fineCharged > 0
                                            ? <span className="text-red-600">Rs. {item.fineCharged}</span>
                                            : <span className="text-gray-400">—</span>
                                        }
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5" className="p-12 text-center text-sm text-gray-400">
                                    No archive records found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
            <p className="mt-4 text-xs text-gray-400">Records in this table are finalized and cannot be modified.</p>
        </div>
    );
};

export default BorrowingHistory;