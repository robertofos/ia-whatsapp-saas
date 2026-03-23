import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { authUser, loadingAuth } = useAuth();

  if (loadingAuth) {
    return <div className="p-6">Carregando...</div>;
  }

  if (!authUser) {
    return <Navigate to="/Login" replace />;
  }

  return children;
}