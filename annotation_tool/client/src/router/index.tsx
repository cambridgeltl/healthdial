import {Navigate} from "react-router-dom";

import Welcome from "../Welcome"
import Login from "../Login"
import Register from "../Register"
import Assignment from "../Assignment"
import ConsentForm from "../ConsentForm";
import AssignmentResult from "../AssignmentResult"
import Admin from "../Admin";
import Example from "../Example";
import AllDone from "../AllDone";
import Instruction from "../Instruction";
import AudioCheck from "../AudioCheck";

const routes = [
    {
        // Welcome Page: Displays the welcome page of the application. It is the entry point of this application.
        path: "/welcome",
        element: <Welcome />
    },
    {
        // Root Redirect: Redirects from the root URL to the welcome page
        path: "/",
        element: <Navigate to= "/welcome" />
    },
    {
        // Login Page: Renders the login page where users can sign in
        path: '/login',
        element: <Login />
    },
    {
        // Registration Page: Shows the registration page for new users to create an account
        path: "/register",
        element: <Register />

    },
    {
        // Assignment Page: Displays the assignment interface for task-oriented dialogue system evaluation.
        path: "/assignment",
        element: <Assignment />
    },
    {
        // Consent Form: A page where users can read and agree to the consent form
        path: "/consent",
        element: <ConsentForm />
    },
    {
        // Assignment Result Page: The page we show to the user after completing an assignment.
        path: "/result",
        element: <AssignmentResult />
    },
    {
        // Admin Page: An administrative interface for managing the access control and download the data.
        path: "/admin",
        element: <Admin />
    },
    {
        path: "/done",
        element: <AllDone />
    },
    {
        path: "/instruction",
        element: <Instruction />
    },
    // {
    //     path: "/example",
    //     element: <Example />
    // },
    {
        path: "/audio",
        element: <AudioCheck />
    }

]

export default routes;
