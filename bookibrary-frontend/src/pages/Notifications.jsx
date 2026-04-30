import React, { useEffect, useState } from "react";
import API from "../api/axios";

function Notifications(){
    const[notifications,setNotifications]=useState([]);
    const fetchNotifications=()=>{
        API.get('notifications/').then(r=>setNotifications(r.data)).catch(e=>console.log(e));
    };
    useEffect(()=>{
        fetchNotifications();
    },[]);
    const markAsRead=(id)=>{
        API.patch(`notifications/${id}/`,{isRead:true}).then(()=>fetchNotifications()).catch(e=>console.error(e));
    };
    const markAsAllRead=async()=>{
        const Unread=notifications.filter(n=>!n.isRead);
        try{
            await Promise.all(Unread.map(n=>API.patch(`notifications/${n.id}/`,{isRead:true})));
            fetchNotifications();
        }catch(e){console.error("Update Failed",e)}
    }
    const getTypeStyles=(type)=>{
        switch(type){
            case 'overdue': return 'bg-red-100 text-red-800 border-red-200';
            case 'reservation': return 'bg-green-100 text-green-800 border-green-200';
            default: return 'bg-blue-100 text-blue-800 border-blue-200';
        }
    };
    return (
        <div className="max-w-2xl mx-auto p-6">
            <div className="flex justify-between items-end mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Notifications</h1>
                    {notifications.some(n => !n.isRead) && (
                        <button 
                            onClick={markAsAllRead}
                            className="text-sm text-blue-600 hover:underline mt-1"
                        >
                            Mark all as read
                        </button>
                    )}
                </div>
                <span className="bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-sm">
                    {notifications.filter(n => !n.isRead).length} Unread
                </span>
            </div>

            <div className="space-y-4">
                {notifications.map((n) => (
                    <div 
                        key={n.id} 
                        className={`p-4 rounded-lg border transition ${n.isRead ? 'bg-white opacity-75' : 'bg-white shadow-md border-l-4 border-l-blue-600'}`}
                    >
                        <div className="flex justify-between items-start">
                            <span className={`text-xs font-semibold px-2 py-1 rounded uppercase ${getTypeStyles(n.type)}`}>
                                {n.type}
                            </span>
                            {/* Formatted date for better UI */}
                            <span className="text-xs text-gray-500">
                                {new Date(n.dateOfCreation).toLocaleDateString()}
                            </span>
                        </div>
                        
                        <p className={`mt-2 ${n.isRead ? 'text-gray-600' : 'text-gray-900 font-medium'}`}>
                            {n.message}
                        </p>

                        {!n.isRead && (
                            <button 
                                onClick={() => markAsRead(n.id)}
                                className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-semibold"
                            >
                                Mark as read
                            </button>
                        )}
                    </div>
                ))}

                {notifications.length === 0 && (
                    <p className="text-center text-gray-500 mt-10">No notifications yet.</p>
                )}
            </div>
        </div>
    );
};
export default Notifications;//to allow it to be used in app.js or router