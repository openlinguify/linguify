import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/global.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

const ErrorBoundary = ({ children }) => {
    try {
        return children;
    } catch (error) {
        console.error(error);
        return <p>Something went wrong!</p>;
    }
};

root.render(
    <ErrorBoundary>
        <App />
    </ErrorBoundary>
);
