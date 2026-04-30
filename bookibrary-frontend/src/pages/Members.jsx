import React, { useEffect, useState } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable"; // Ensure this path is correct

function Members() {
    const [members, setMembers] = useState([]);
    const [form, setForm] = useState({
        name: '', email: '', phone: '', role: 'member', password: ''
    });

    const fetchMembers = () => {
        API.get('member/').then(response => setMembers(response.data)).catch(error => console.log(error));
    }

    useEffect(() => {
        fetchMembers();
    }, []);

    const change = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    }

    const SendToDjango = () => {
        API.post('member/', form).then(() => {
            fetchMembers();
            setForm({ name: '', email: '', phone: '', role: 'member', password: '' });
        }).catch(error => console.log(error));
    }

    const Del = (id) => {
        API.delete(`member/${id}/`).then(() => fetchMembers()).catch(error => console.log(error));
    }

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">👥 Members</h1>

            {/* Add Member Form */}
            <div className="bg-card border border-border p-6 mb-8 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Add Member</h2>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <input name="name" placeholder="Name" value={form.name} onChange={change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="email" placeholder="Email" value={form.email} onChange={change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="password" placeholder="Password" value={form.password} onChange={change} type="password"
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="phone" placeholder="Phone" value={form.phone} onChange={change}
                        className="border border-border p-2 focus:outline-primary" />
                    <select name="role" value={form.role} onChange={change}
                        className="border border-border p-2 focus:outline-primary">
                        <option value="member">Member</option>
                        <option value="librarian">Librarian</option>
                        <option value="admin">Administrator</option>
                    </select>
                </div>
                <button onClick={SendToDjango}
                    className="mt-4 bg-primary text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                    Add Member
                </button>
            </div>

            {/* Using the DataTable Component */}
            <DataTable 
                columns={['ID', 'Name', 'Email', 'Phone', 'Role', 'Joined']}
                data={members}
                onDelete={Del}
            >
                {members.map(m => (
                    <tr key={m.id} className="border-b border-border text-sm text-center hover:bg-muted">
                        <td className="p-3 border-r border-border">{m.id}</td>
                        <td className="p-3 border-r border-border">{m.name}</td>
                        <td className="p-3 border-r border-border">{m.email}</td>
                        <td className="p-3 border-r border-border">{m.phone}</td>
                        <td className="p-3 border-r border-border">
                            <span className="px-2 py-1 bg-muted border border-border text-xs font-medium">
                                {m.role.toUpperCase()}
                            </span>
                        </td>
                        <td className="p-3 border-r border-border">{m.joinedDate}</td>
                    </tr>
                ))}
            </DataTable>
        </div>
    );
}

export default Members;