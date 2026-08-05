import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LoginFormComponent, RegisterFormComponent, ForgotPasswordComponent } from "./pages"

export function AuthTabs() {
  return (
    <Tabs defaultValue="login" className="w-full max-w-md mx-auto">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="login">Login</TabsTrigger>
        <TabsTrigger value="register">Register</TabsTrigger>
        <TabsTrigger value="forgot-password">Forgot Password</TabsTrigger>
      </TabsList>
      <TabsContent value="login" className="mt-6">
        <LoginFormComponent />
      </TabsContent>
      <TabsContent value="register" className="mt-6">
        <RegisterFormComponent />
      </TabsContent>
      <TabsContent value="forgot-password" className="mt-6">
        <ForgotPasswordComponent />
      </TabsContent>
    </Tabs>
  )
}