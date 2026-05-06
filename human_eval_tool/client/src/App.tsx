import React, {useEffect} from 'react';
import './index.css';
import {useLocation, useRoutes,useNavigate} from 'react-router-dom'
import routes from "./router"
import useToken from './service/TokenService'

// Component to redirect to the assignment page
function ToAssignment(){
    const navigateTo = useNavigate()
    useEffect(() => {
        navigateTo("/assignment")
    }, [navigateTo]);
    return <div/>
}

// Component to handle authentication-based routing
function AuthRouter(){
    const { getToken } = useToken();

    const isAuthenticated = getToken() !== null
    const location = useLocation()
    const routers = useRoutes(routes)

    // Redirects to the assignment page if authenticated and trying to access login
    if (isAuthenticated && location.pathname === '/login'){
        return <ToAssignment />
    }

    // Redirects to login if not authenticated and trying to access restricted pages
    // if (!isAuthenticated && (location.pathname === '/assignment' || location.pathname === '/admin')){
    //     return <ToLogin />
    // }

    // Returns the regular routing setup
    return routers
}


function App() {


    return (
        <div className='App'>
            {/*<VoiceChatBox/>*/}
            <AuthRouter />
        </div>
    );
}

export default App;
