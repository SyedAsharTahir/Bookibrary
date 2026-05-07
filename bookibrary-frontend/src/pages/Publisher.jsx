import React, { useEffect, useState } from "react";
import API from "../api/axios"; // Ensure your axios instance is set up

const Publisher = () => {
    const [list, setList] = useState([]);
    const [name, setName] = useState("");

    const fetchData = async () => {
        const res = await API.get('publishers/');
        setList(res.data);
    };

   const handleAdd = async (e) => {
        e.preventDefault();
        if (!name.trim()) return; // Simple validation
        try {
            await API.post('publishers/', { name });
            setName("");
            fetchData();
        } catch (error) {
            console.error("Error adding publisher:", error);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

   return (
        <div className="p-8">
            {/* 2. Updated header text */}
            <h1 className="text-2xl font-bold mb-4">Manage Publishers</h1>
            
            <form onSubmit={handleAdd} className="mb-6 flex gap-2">
                <input 
                    className="border p-2 rounded"
                    placeholder="Publisher Name" 
                    value={name} 
                    onChange={(e) => setName(e.target.value)} 
                />
                <button className="bg-blue-600 text-white px-4 py-2 rounded">Add Publisher</button>
            </form>

            <table className="w-full border">
                <thead>
                    <tr className="bg-gray-100">
                        <th className="p-2">Name</th>
                    </tr>
                </thead>
                <tbody>
                    {list.map(p => (
                        <tr key={p.id}>
                            <td className="p-2 border">{p.name}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Publisher;