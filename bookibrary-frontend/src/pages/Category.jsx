import React, { useEffect, useState } from "react";
import API from "../api/axios";
import { getRole } from "../auth";

function Category(){
    const [categories,setCategories]=useState([]);
    const [form,setForm]=useState({name: '',description:''});
    const role=getRole();
    const fetchCategories=()=>{
        API.get('category/').then(r=>setCategories(r.data)).catch(e=>console.log(e));
    }
    useEffect(()=>{fetchCategories();},[]);
    const change=(e)=>setForm({...form,[e.target.name]:e.target.value});
    const sendToDjango=()=>{
        API.post('category/',form).then(()=>{
            fetchCategories();
            setForm({name:'',description:''});
        }).catch(e=>console.log(e));
    }
    const Del=(id)=>{
        API.delete(`category/${id}/`).then(()=>fetchCategories()).catch(e=>console.log(e));
    }

    return(
        <div className="bg-gray-100 min-h-screen p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">📂 Categories</h1>

            {role === 'admin' || role === 'librarian' ? (
                <div className="bg-white rounded-lg shadow p-6 mb-8">
                    <h2 className="text-xl font-semibold text-gray-700 mb-4">Add Category</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input name="name" placeholder="Category Name" value={form.name} onChange={change}
                            className="border border-gray-300 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                        <input name="description" placeholder="Description" value={form.description} onChange={change}
                            className="border border-gray-300 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>
                    <button onClick={sendToDjango}
                        className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md text-sm font-medium transition">
                        Add Category
                    </button>
                </div>
            ) : null}

            <div className="bg-white rounded-lg shadow overflow-x-auto">
                <table className="min-w-full border">
                    <thead>
                        <tr className="bg-blue-800 text-white text-sm text-center">
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">ID</span></th>
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">Name</span></th>
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">Description</span></th>
                            {role === 'admin' || role === 'librarian' ? <th className="py-3 px-4">Actions</th> : null}
                        </tr>
                    </thead>
                    <tbody>
                        {categories.map(cat => (
                            <tr key={cat.id} className="border-b text-sm text-center text-gray-700 hover:bg-gray-50">
                                <td className="p-3">{cat.id}</td>
                                <td className="p-3">{cat.name}</td>
                                <td className="p-3">{cat.description}</td>
                                {role === 'admin' || role === 'librarian' ? (
                                    <td className="p-3 flex justify-center gap-2">
                                        <button onClick={() => Del(cat.id)}
                                            className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md text-xs transition">
                                            Delete
                                        </button>
                                    </td>
                                ) : null}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
export default Category;