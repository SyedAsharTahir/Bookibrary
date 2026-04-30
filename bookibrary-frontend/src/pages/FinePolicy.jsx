import React, { useEffect, useState } from "react";
import API from "../api/axios";

function FinePolicy(){
    const [policies,setPolicies]=useState([]);
    const [categories,setCategories]=useState([]);
    const [form,setForm]=useState({category:'',finePerDay:'',maxFineDays:30});
    const fetchPolicies=()=>{
        API.get('finepolicy/').then(r=>setPolicies(r.data)).catch(e=>console.log(e));
    }
    useEffect(()=>{
        fetchPolicies();
        API.get('category/').then(r=>setCategories(r.data)).catch(e=>console.log(e));
    },[]);
    const change=(e)=>{
        const val=e.target.type==='number'?Number(e.target.value):e.target.value;
        setForm({...form,[e.target.name]:val});
    };
    const sendToDjango=()=>{
        if(!form.category || form.finePerDay===''){alert("Please Select Category and enter a Fine Amount");return;}
        API.post('finepolicy/',form).then(()=>{
            fetchPolicies();
            setForm({category:'',finePerDay:'',maxFineDays:30});
        }).catch(e=>console.log(e));
    };
    const Del=(id)=>{
        if(window.confirm("Are you sure you want to delete this policy?")){
        API.delete(`finepolicy/${id}/`).then(()=>fetchPolicies()).catch(e=>console.log(e));
    }
    };
    const getCategoryName=(id)=>{
        const cat=categories.find(c=>c.id===parseInt(id));
        return cat?cat.name:id;
    };
    return(  <div className="bg-gray-100 min-h-screen p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">📋 Fine Policies</h1>

            <div className="bg-white rounded-lg shadow p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-700 mb-4">Add Fine Policy</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select name="category" value={form.category} onChange={change}
                        className="border border-gray-300 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">Select Category</option>
                        {categories.map(cat => (
                            <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                    </select>
                    <input name="finePerDay" placeholder="Fine Per Day (Rs.)" value={form.finePerDay} onChange={change} type="number"
                        className="border border-gray-300 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    <input name="maxFineDays" placeholder="Max Fine Days" value={form.maxFineDays} onChange={change} type="number"
                        className="border border-gray-300 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
                <button onClick={sendToDjango}
                    className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md text-sm font-medium transition">
                    Add Policy
                </button>
            </div>

            <div className="bg-white rounded-lg shadow overflow-x-auto">
                <table className="min-w-full border">
                    <thead>
                        <tr className="bg-blue-800 text-white text-sm text-center">
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">ID</span></th>
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">Category</span></th>
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">Fine/Day</span></th>
                            <th className="p-0"><span className="block py-3 px-4 border-r border-blue-600">Max Days</span></th>
                            <th className="py-3 px-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {policies.map(policy => (
                            <tr key={policy.id} className="border-b text-sm text-center text-gray-700 hover:bg-gray-50">
                                <td className="p-3">{policy.id}</td>
                                <td className="p-3">{getCategoryName(policy.category)}</td>
                                <td className="p-3">Rs. {policy.finePerDay}</td>
                                <td className="p-3">{policy.maxFineDays} days</td>
                                <td className="p-3 flex justify-center gap-2">
                                    <button onClick={() => Del(policy.id)}
                                        className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md text-xs transition">
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
export default FinePolicy;