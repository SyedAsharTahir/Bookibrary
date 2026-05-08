//this file is made as a utillity file to act as a helper funciton to allow any component who logs in to import this file
//used by navbar
export function getRole(){
    const token=localStorage.getItem('accessToken');
    if (!token){return null;}
    try{
        // Parse JWT token correctly
        const parts = token.split('.');
        const header = parts[0].replace(/-/g, '+');
        const payload = JSON.parse(atob(parts[1]));
        return payload.role;
    }catch
    {
        return null;
    }
}
export function getName(){
    const token=localStorage.getItem('accessToken');
    if (!token){return null;}
    try{
        //JWT token ot three sections->HEADER[0].PAYLOAD[1].SIGN[2]
        //since payload is where all the data of user is stored whereas the header is the algo type
        //and sign is is for verification
        //so we split and aprse to find the payload
        const payload=token.split('.')[1]
        //decode it
        const decodeIt=JSON.parse(atob(payload))//atob->converts base64 to regular string and parse converts the string to python object
        return decodeIt.name;
    }catch
    {
        return null;
    }
}
export function logOut(){
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href='/login';//redirect to login
}