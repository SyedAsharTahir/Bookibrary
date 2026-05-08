import React, { useEffect, useState } from "react";
import API from "../api/axios"; // Ensure your axios instance is set up

const Author = () => {
    const [list, setList] = useState([]);

    const fetchData = async () => {
        const res = await API.get('authors/');
        setList(res.data);
    };

    useEffect(() => {
        fetchData();
    }, []);

    return (
        <div className="p-8">
            <h1 className="text-2xl font-bold mb-4">View Authors</h1>
            <p className="text-gray-600 mb-6">Authors are automatically created when books are added to the system.</p>
            
            <table className="w-full border">
                <thead><tr className="bg-gray-100"><th className="p-2 text-left">Name</th></tr></thead>
                <tbody>
                    {list.map(a => <tr key={a.id}><td className="p-2 border">{a.name}</td></tr>)}
                </tbody>
            </table>
            
            {list.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    <p>No authors found.</p>
                    <p className="text-sm mt-2">Authors will appear here when books are added to the system.</p>
                </div>
            )}
        </div>
    );
};

export default Author;