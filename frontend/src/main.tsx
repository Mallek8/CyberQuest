import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { AppProviders } from "./app/providers";
import "./styles/index.css";

const root = document.getElementById("root");
if (!root) {
  throw new Error("Root element missing.");
}

createRoot(root).render(
  <StrictMode>
    <AppProviders />
  </StrictMode>,
);
