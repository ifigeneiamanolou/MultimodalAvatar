import React from "react";
import '../../global.css';
import {
    BrowserRouter as Router,
    Routes,
    Route,
} from "react-router-dom";
import Home from "./pages/home";
import Login from "./pages/login";
import Signup from "./pages/signup";
import Menu from "./pages/menu";
import Forgot from "./pages/forgotPass";

function App() {
    return (
        <Router>
            <Routes>
                # Include here all pages of the application with the corresponding path :
                <Route path="/" element={<Home />} />
                <Route path = "/login" element = {<Login/>}/>
                <Route path = "/signup" element = {<Signup/>}/>
                <Route path = "/menu" element = {<Menu/>}/>
                <Route path = "/forgot" element = {<Forgot/>}/>
            </Routes>
        </Router>
    );
}

export default App;