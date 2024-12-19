import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HeaderProfile from './components/layout/HeaderProfile';
import Sidebar from './components/layout/Sidebar';
import MainContent from './components/features/MainContent';

const App: React.FC = () => {
    return (
        <Router>
            <HeaderProfile />
            <div className="d-flex">
                <Sidebar />
                <MainContent />
            </div>
        </Router>
    );
};

export default App;
