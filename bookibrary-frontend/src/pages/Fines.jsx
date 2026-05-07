import React, { useEffect, useState } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable";
import LoadingSpinner from "../components/LoadingSpinner";
import TableSkeleton from "../components/TableSkeleton";

function Fines() {
    const [fines, setFines] = useState([]);
    const [borrowings, setBorrowings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState({ borrowing: '', amount: '', paid: false });

    const fetchFines = () => {
        setLoading(true);
        API.get('fines/')
            .then(r => setFines(r.data))
            .catch(e => console.log(e))
            .finally(() => setLoading(false));
    };
    const change = (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setForm({ ...form, [e.target.name]: value });
    };
    const SendToDjango = () => {
        API.post('fines/', form).then(() => {
            fetchFines();
            setForm({ borrowing: '', amount: '', paid: false });
        }).catch(e => console.log(e));
    };
    const Del = (id) => {
        API.delete(`fines/${id}/`).then(() => fetchFines()).catch(e => console.log(e));
    };
    useEffect(() => {
        fetchFines();
        API.get('borrowings/').then(r => setBorrowings(r.data)).catch(e => console.log(e));
    }, []);

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">💰 Fines</h1>

            <div className="bg-card border border-border p-6 mb-8 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Add Fine</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                    <select name="borrowing" value={form.borrowing} onChange={change}
                        className="border border-border p-2 focus:outline-primary">
                        <option value="">Select Borrowing</option>
                        {borrowings.map(b => (
                            <option key={b.id} value={b.id}>Borrowing #{b.id}</option>
                        ))}
                    </select>
                    <input name="amount" value={form.amount} onChange={change} placeholder="Amount" type="number"
                        className="border border-border p-2 focus:outline-primary" />
                    <label className="flex items-center gap-2 text-sm">
                        <input name="paid" type="checkbox" checked={form.paid} onChange={change} className="w-4 h-4" />
                        Paid
                    </label>
                </div>
                <button onClick={SendToDjango}
                    className="mt-4 bg-primary text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                    Add Fine
                </button>
            </div>

            {loading ? (
                <div className="space-y-3">
                    <LoadingSpinner text="Loading fines..." />
                    <TableSkeleton rows={5} columns={6} />
                </div>
            ) : (
                <DataTable
                    columns={['ID', 'Borrowing', 'Amount', 'Issued Date', 'Status']}
                    data={fines}
                    onDelete={Del}
                >
                    {fines.map(fine => (
                        <React.Fragment key={fine.id}>
                            <td className="p-3 border-r border-border">{fine.id}</td>
                            <td className="p-3 border-r border-border">#{fine.borrowing}</td>
                            <td className="p-3 border-r border-border">Rs. {fine.amount}</td>
                            <td className="p-3 border-r border-border">{fine.issuedDate}</td>
                            <td className="p-3 border-r border-border">
                                <span className={`px-2 py-1 text-xs font-medium border border-border ${fine.paid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                    {fine.paid ? "PAID" : "UNPAID"}
                                </span>
                            </td>
                        </React.Fragment>
                    ))}
                </DataTable>
            )}
        </div>
    );
}

export default Fines;