import React, { useEffect, useState } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable";

function Reservations() {
    const [reservations, setReservations] = useState([]);
    const [books, setBooks] = useState([]);
    const [members, setMembers] = useState([]);
    const [form, setForm] = useState({ status: '', book: '', member: '' });

    const fetchReservations = () => {
        API.get('reservations/').then(r => setReservations(r.data)).catch(e => console.log(e));
    };
    useEffect(() => {
        fetchReservations();
        API.get('books/').then(r => setBooks(r.data)).catch(e => console.log(e));
        API.get('members/').then(r => setMembers(r.data)).catch(e => console.log(e));
    }, []);

    const change = (e) => setForm({ ...form, [e.target.name]: e.target.value });

    const SendToDjango = () => {
        API.post('reservations/', form).then(() => {
            fetchReservations();
            setForm({ status: '', book: '', member: '' });
        }).catch(e => console.log(e));
    };
    const Del = (id) => {
        API.delete(`reservations/${id}/`).then(() => fetchReservations()).catch(e => console.log(e));
    };

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">🔖 Reservations</h1>

            <div className="bg-card border border-border p-6 mb-8 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Add Reservation</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                    <select name="status" value={form.status} onChange={change}
                        className="border border-border p-2 focus:outline-primary">
                        <option value="">Select Status</option>
                        <option value="pending">Pending</option>
                        <option value="fulfilled">Fulfilled</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                </div>
                <button onClick={SendToDjango}
                    className="mt-4 bg-primary text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                    Add Reservation
                </button>
            </div>

            <DataTable
                columns={['ID', 'Book', 'Member', 'Reserved Date', 'Status']}
                data={reservations}
                onDelete={Del}
            >
                {reservations.map(r => (
                    <React.Fragment key={r.id}>
                        <td className="p-3 border-r border-border">{r.id}</td>
                        <td className="p-3 border-r border-border">{r.book}</td>
                        <td className="p-3 border-r border-border">{r.member}</td>
                        <td className="p-3 border-r border-border">{r.reservedDate}</td>
                        <td className="p-3 border-r border-border">
                            <span className={`px-2 py-1 text-xs font-medium border border-border ${
                                r.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                r.status === 'fulfilled' ? 'bg-green-100 text-green-800' :
                                'bg-red-100 text-red-800'
                            }`}>
                                {r.status?.toUpperCase()}
                            </span>
                        </td>
                    </React.Fragment>
                ))}
            </DataTable>
        </div>
    );
}

export default Reservations;