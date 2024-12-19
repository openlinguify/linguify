import React from "react";
import ReactDOM from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";
import "./styles/global.css";
import App from "./App";

// Check if the root element exists
const rootElement = document.getElementById("root");
if (!rootElement) {
    throw new Error("Root element not found. Ensure an element with id 'root' exists in your HTML.");
}

const root = ReactDOM.createRoot(rootElement);

// Define ErrorBoundary with proper typing
type ErrorBoundaryProps = {
    children: React.ReactNode;
};

const ErrorBoundary: React.FC<ErrorBoundaryProps> = ({ children }) => {
    try {
        return <>{children}</>;
    } catch (error) {
        console.error("ErrorBoundary caught an error:", error);
        return <p>Something went wrong!</p>;
    }
};

root.render(
    <ErrorBoundary>
        <App />
    </ErrorBoundary>
);
