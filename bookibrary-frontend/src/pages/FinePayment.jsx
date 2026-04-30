import React, { useState } from "react";
import API from "../api/axios";

const FinePayment = ({ fineId, amountDue, onSuccess }) => {
    const [payment, setPayment] = useState({
        fine: fineId,
        amountpaid: amountDue || '',
        method: 'cash'
    });
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setPayment(prev => ({ ...prev, [name]: value }));
    };

    const handlePayment = async () => {
        if (!payment.amountpaid || payment.amountpaid <= 0) {
            alert("Please enter a valid amount.");
            return;
        }

        setLoading(true);
        try {
            await API.post('finepayment/', payment);
            alert("Payment processed successfully!");
            if (onSuccess) onSuccess(); // Callback to refresh parent list
        } catch (error) {
            console.error("Payment submission failed:", error);
            alert("Failed to process payment. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Process Fine Payment</h2>
            
            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-slate-600">Amount (Rs.)</label>
                    <input 
                        type="number" 
                        name="amountpaid"
                        value={payment.amountpaid} 
                        onChange={handleChange}
                        className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-600">Payment Method</label>
                    <select 
                        name="method" 
                        value={payment.method} 
                        onChange={handleChange}
                        className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                    >
                        <option value="cash">Cash</option>
                        <option value="online">Online</option>
                    </select>
                </div>

                <button 
                    onClick={handlePayment}
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
                >
                    {loading ? "Processing..." : "Complete Payment"}
                </button>
            </div>
        </div>
    );
};

export default FinePayment;