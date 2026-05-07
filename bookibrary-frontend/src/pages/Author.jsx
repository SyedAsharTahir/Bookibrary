import React, { useEffect, useState } from "react";
import API from "../api/axios"; // Ensure your axios instance is set up

const Author = () => {
    const [list, setList] = useState([]);
    const [name, setName] = useState("");

    const fetchData = async () => {
        const res = await API.get('authors/');
        setList(res.data);
    };

    const handleAdd = async (e) => {
        e.preventDefault();
        await API.post('authors/', { name });
        setName("");
        fetchData();
    };

    useEffect(() => {
        fetchData();
    }, []);

    return (
        <div className="p-8">
            <h1 className="text-2xl font-bold mb-4">Manage Authors</h1>
            
            <form onSubmit={handleAdd} className="mb-6 flex gap-2">
                <input 
                    className="border p-2 rounded"
                    placeholder="Author Name" 
                    value={name} 
                    onChange={(e) => setName(e.target.value)} 
                />
                <button className="bg-blue-600 text-white px-4 py-2 rounded">Add Author</button>
            </form>

            <table className="w-full border">
                <thead><tr className="bg-gray-100"><th className="p-2">Name</th></tr></thead>
                <tbody>
                    {list.map(a => <tr key={a.id}><td className="p-2 border">{a.name}</td></tr>)}
                </tbody>
            </table>
        </div>
    );
};

export default Author;