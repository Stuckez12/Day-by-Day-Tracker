import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "bootstrap/dist/css/bootstrap.css";
import "./styles/base.scss";

createRoot(document.getElementById("WebRoot")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
