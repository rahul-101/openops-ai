import { Route, Routes } from "react-router-dom"
import { AuthLayout } from "./auth-layout"
import { LoginPage, RegisterPage, ForgotPasswordPage } from "./pages.tsx"
import { PublicRoute } from "@/components/auth/protected-route"

export function AuthRoutes() {
  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route
          index
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />
        <Route
          path="forgot-password"
          element={
            <PublicRoute>
              <ForgotPasswordPage />
            </PublicRoute>
          }
        />
      </Route>
    </Routes>
  )
}
