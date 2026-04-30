import React, { useEffect, useState, useCallback } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable";

function Borrowing() {
    const [borrowings, setBorrowings] = useState([]);
    const [books, setBooks] = useState([]);
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState({
        book: '', member: '', dueDate: '', returnDate: '', returned: false
    });

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [borrowRes, bookRes, memberRes] = await Promise.all([
                API.get('borrowing/'),
                API.get('books/'),
                API.get('member/')
            ]);
            setBorrowings(borrowRes.data);
            setBooks(bookRes.data);
            setMembers(memberRes.data);
        } catch (err) {
            console.error("Failed to fetch data:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const change = (e) => {
        const { name, value, type, checked } = e.target;
        setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    };

    const SendToDjango = async () => {
        try {
            await API.post('borrowing/', form);
            await fetchData();
            setForm({ book: '', member: '', dueDate: '', returnDate: '', returned: false });
        } catch (err) {
            alert("Error adding record. Please check your inputs.");
        }
    };

    const Del = async (id) => {
        if (window.confirm("Delete this borrowing record?")) {
            try {
                await API.delete(`borrowing/${id}/`);
                fetchData();
            } catch (err) {
                console.error(err);
            }
        }
    };

    const getBookTitle = (id) => books.find(b => b.id === parseInt(id))?.title || `#${id}`;
    const getMemberName = (id) => members.find(m => m.id === parseInt(id))?.name || `#${id}`;

    if (loading) return <div className="p-8 text-sm">Loading records...</div>;

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">📖 Borrowing Records</h1>

            <div className="bg-card border border-border p-6 mb-8 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Add Borrowing Record</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                    <select name="book" value={form.book} onChange={change}
                        className="border border-border p-2 focus:outline-primary">
                        <option value="">Select Book</option>
                        {books.map(b => (
                            <option key={b.id} value={b.id}>{b.title}</option>
                        ))}
                    </select>
                    <select name="member" value={form.member} onChange={change}
                        className="border border-border p-2 focus:outline-primary">
                        <option value="">Select Member</option>
                        {members.map(m => (
                            <option key={m.id} value={m.id}>{m.name}</option>
                        ))}
                    </select>
                    <input name="dueDate" type="date" value={form.dueDate} onChange={change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="returnDate" type="date" value={form.returnDate} onChange={change}
                        className="border border-border p-2 focus:outline-primary" />
                    <label className="flex items-center gap-2 text-sm">
                        <input name="returned" type="checkbox" checked={form.returned} onChange={change} className="w-4 h-4" />
                        Returned
                    </label>
                </div>
                <button onClick={SendToDjango}
                    className="mt-4 bg-primary text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                    Add Record
                </button>
            </div>

            <DataTable
                columns={['ID', 'Book', 'Member', 'Due Date', 'Return Date', 'Status']}
                data={borrowings}
                onDelete={Del}
            >
                {borrowings.map(b => (
                    <React.Fragment key={b.id}>
                        <td className="p-3 border-r border-border">{b.id}</td>
                        <td className="p-3 border-r border-border">{getBookTitle(b.book)}</td>
                        <td className="p-3 border-r border-border">{getMemberName(b.member)}</td>
                        <td className="p-3 border-r border-border">{b.dueDate}</td>
                        <td className="p-3 border-r border-border">{b.returnDate || '—'}</td>
                        <td className="p-3 border-r border-border">
                            <span className={`px-2 py-1 text-xs font-medium border border-border ${b.returned ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                {b.returned ? 'RETURNED' : 'ACTIVE'}
                            </span>
                        </td>
                    </React.Fragment>
                ))}
            </DataTable>
        </div>
    );
}

export default Borrowing;