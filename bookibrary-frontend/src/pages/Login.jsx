import { useState } from "react";
import axios from "axios";

function Login(){
   const [form,setForm]=useState({username:'',password:''});
   const [error,setError]=useState('');
   const [showPassword, setShowPassword] = useState(false);
//async means this funciton waill wait for API call
   async function handleTheLogin(e){
    e.preventDefault();
    try{
        const result=await axios.post('http://127.0.0.1:8000/api/token/',form);//endpoint
        localStorage.setItem('access',result.data.access);//save the token
        localStorage.setItem('refresh',result.data.refresh);//save refresh token
        window.location.href='/';//redirect to home page
        console.log(result.data);
    }catch(error){
        setError('Invalid Username or Password');
        console.error('Login error details:', error);
    }
   }

    return (
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-100 via-indigo-50 to-purple-100 p-4">
            <div className="w-full max-w-md rounded-2xl border border-indigo-100 bg-white p-8 shadow-xl">
                        <h1 className="pb-2 text-center text-4xl font-bold text-indigo-700">
                            Bookibrary
                        </h1>
                        <p className="mb-6 text-center text-sm text-gray-500">
                            Sign in to continue
                        </p>

                        {error && (
                            <div className="bg-red-100 text-red-700 px-4 py-2 rounded-md text-sm mb-4 text-center">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleTheLogin} className="space-y-4">
                            <div>
                                <label className="mb-2 block text-sm font-medium text-gray-700">Username</label>
                                <input
                                    type="text"
                                    value={form.username}
                                    onChange={(e) => setForm({ ...form, username: e.target.value })}
                                    placeholder="Username"
                                    className="w-full rounded-lg border border-gray-300 p-3 placeholder:text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                                    required
                                />
                            </div>
                            <div>
                                <label className="mb-2 block text-sm font-medium text-gray-700">Password</label>
                                <div className="relative">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={form.password}
                                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                                    placeholder="Password"
                                    className="w-full rounded-lg border border-gray-300 p-3 pr-24 placeholder:text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword((prev) => !prev)}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 py-1 text-xs text-indigo-700 hover:bg-indigo-50"
                                >
                                    {showPassword ? "Hide" : "Show"}
                                </button>
                                </div>
                            </div>
                            <button
                                type="submit"
                                className="mt-2 w-full rounded-lg bg-indigo-600 p-3 text-sm font-semibold text-white transition hover:bg-indigo-700">
                                Sign In
                            </button>
                        </form>
                </div>
        </div>
    );
}
export default Login;