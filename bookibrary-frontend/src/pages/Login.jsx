import { useState } from "react";
import axios from "axios";

function Login(){
   const [form,setForm]=useState({username:'',password:''});
   const [error,setError]=useState('');
//async means this funciton waill wait for API call
   async function handleTheLogin(e){
    e.preventDefault();
    try{
        const result=await axios.post('http://127.0.0.1:8000/api/token/',form);//endpoint
        localStorage.setItem('accessToken',result.data.access);//save the token
        localStorage.setItem('refreshToken',result.data.refresh);
        window.location.href='/';//redirect to home page
        console.log(result.data);
    }catch(error){setError('Invalid Username or Password')};
   }

    return (
        <div className="flex items-center justify-center min-h-screen min-w-screen dark:bg-gray-900 bg-gray-100">
            <div className="grid gap-8 m-4">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-[26px]">
                    <div className="border-[20px] border-transparent rounded-[20px] dark:bg-gray-900 bg-white shadow-lg p-8">
                        
                        <h1 className="pt-4 pb-2 font-bold text-4xl dark:text-gray-400 text-center">
                            📚 Bookibrary
                        </h1>
                        <p className="text-center text-gray-500 mb-6 text-sm">Sign in to your account</p>

                        {error && (
                            <div className="bg-red-100 text-red-700 px-4 py-2 rounded-md text-sm mb-4 text-center">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleTheLogin} className="space-y-4">
                            <div>
                                <label className="mb-2 dark:text-gray-400 text-lg">Username</label>
                                <input
                                    type="text"
                                    value={form.username}
                                    onChange={(e) => setForm({ ...form, username: e.target.value })}
                                    placeholder="Username"
                                    className="border dark:bg-indigo-700 dark:text-gray-300 dark:border-gray-700 p-3 shadow-md placeholder:text-base border-gray-300 rounded-lg w-full focus:scale-105 ease-in-out duration-300"
                                    required
                                />
                            </div>
                            <div>
                                <label className="mb-2 dark:text-gray-400 text-lg">Password</label>
                                <input
                                    type="password"
                                    value={form.password}
                                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                                    placeholder="Password"
                                    className="border dark:bg-indigo-700 dark:text-gray-300 dark:border-gray-700 p-3 shadow-md placeholder:text-base border-gray-300 rounded-lg w-full focus:scale-105 ease-in-out duration-300"
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                className="bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg mt-6 p-2 text-white rounded-lg w-full hover:scale-105 hover:from-purple-500 hover:to-blue-500 transition duration-300 ease-in-out">
                                SIGN IN
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
export default Login;