import React, { useEffect, useState } from "react";
import API from "../api/axios";
import { getRole } from "../auth";

function Category(){
    const [categories,setCategories]=useState([]);
    const role=getRole();
    const fetchCategories=()=>{
        API.get('categories/').then(r=>setCategories(r.data)).catch(e=>console.log(e));
    }
    useEffect(()=>{fetchCategories();},[]);

    return(
        <div className="bg-gray-100 min-h-screen p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">📂 Categories</h1>

            
            <div className="bg-white rounded-lg shadow overflow-x-auto">
                <table className="min-w-full border">
                    <thead>
                        <tr className="bg-blue-800 text-white text-sm text-center">
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">ID</span></th>
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">Name</span></th>
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">Description</span></th>
                            <th className="p-0"><span className="block py-3 px-4">Books Count</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        {categories.map(cat => (
                            <tr key={cat.id} className="border-b text-sm text-center text-gray-700 hover:bg-gray-50">
                                <td className="p-3">{cat.id}</td>
                                <td className="p-3">{cat.name}</td>
                                <td className="p-3">{cat.description}</td>
                                <td className="p-3">{cat.book_count}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
export default Category;