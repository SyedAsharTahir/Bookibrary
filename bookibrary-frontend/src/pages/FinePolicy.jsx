import React, { useEffect, useState } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable";

function FinePolicy() {
    const [policies, setPolicies] = useState([]);
    const [categories, setCategories] = useState([]);
    const [form, setForm] = useState({ category: '', finePerDay: '', maxFineDays: 30 });

    const fetchPolicies = () => {
        API.get('finepolicies/').then(r => setPolicies(r.data)).catch(e => console.log(e));
    };
    useEffect(() => {
        fetchPolicies();
        API.get('categories/').then(r => setCategories(r.data)).catch(e => console.log(e));
    }, []);

    const change = (e) => {
        const val = e.target.type === 'number' ? Number(e.target.value) : e.target.value;
        setForm({ ...form, [e.target.name]: val });
    };
    const sendToDjango = () => {
        if (!form.category || form.finePerDay === '') { alert("Please select a category and enter a fine amount"); return; }
        API.post('finepolicies/', form).then(() => {
            fetchPolicies();
            setForm({ category: '', finePerDay: '', maxFineDays: 30 });
        }).catch(e => console.log(e));
    };
    const Del = (id) => {
        if (window.confirm("Delete this policy?"))
            API.delete(`finepolicies/${id}/`).then(() => fetchPolicies()).catch(e => console.log(e));
    };
    const getCategoryName = (id) => categories.find(c => c.id === parseInt(id))?.name || id;

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">📋 Fine Policies</h1>

            <div className="bg-card border border-border p-6 mb-8 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Add Fine Policy</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select name="category" value={form.category} onChange={change}
                        className="border border-border p-2 focus:outline-primary">
                        <option value="">Select Category</option>
                        {categories.map(cat => (
                            <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                    </select>
                    <input name="finePerDay" placeholder="Fine Per Day (Rs.)" value={form.finePerDay} onChange={change} type="number"
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="maxFineDays" placeholder="Max Fine Days" value={form.maxFineDays} onChange={change} type="number"
                        className="border border-border p-2 focus:outline-primary" />
                </div>
                <button onClick={sendToDjango}
                    className="mt-4 bg-primary text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                    Add Policy
                </button>
            </div>

            <DataTable
                columns={['ID', 'Category', 'Fine/Day', 'Max Days']}
                data={policies}
                onDelete={Del}
            >
                {policies.map(p => (
                    <React.Fragment key={p.id}>
                        <td className="p-3 border-r border-border">{p.id}</td>
                        <td className="p-3 border-r border-border">{getCategoryName(p.category)}</td>
                        <td className="p-3 border-r border-border">Rs. {p.finePerDay}</td>
                        <td className="p-3 border-r border-border">{p.maxFineDays} days</td>
                    </React.Fragment>
                ))}
            </DataTable>
        </div>
    );
}

export default FinePolicy;