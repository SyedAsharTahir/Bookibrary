import axios from 'axios';
//defined django api bas eurl once  and each page just imprts this api without repeating fulla ddress each time
const API =axios.create(
    {
        baseURL:'http://127.0.0.1:8000/api/'
    }
);
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken'); 
       if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config
    },
    (error)=>{
        console.error('Error:',error);
        return Promise.reject(error);
    }
);
export default API;