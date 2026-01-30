import { useState } from 'react';
import { Card, CardHeader, CardBody, Button, Input, Checkbox, Link, Divider } from "@heroui/react";
import { Icon } from "@iconify/react";
import ftpLogo from '../assets/ftp.svg'; 

export default function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isVisible, setIsVisible] = useState(false);

  const toggleVisibility = () => setIsVisible(!isVisible);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch("http://127.0.0.1:8000/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("access_token", data.access_token);
        onLoginSuccess();
      } else {
        setError(data.detail || "Invalid credentials. Please try again.");
      }
    } catch (err) {
      setError("System unreachable. Contact IT Support.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex items-center justify-center min-h-screen bg-[#f8fafc] overflow-hidden">
      {/* Background Decorative Elements (Green Glow) */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-green-100/50 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-100/50 blur-[120px]" />

      <Card className="w-full max-w-105 p-4 sm:p-8 bg-white/80 backdrop-blur-md border border-white shadow-[0_20px_50px_rgba(0,0,0,0.05)] rounded-[2.5rem]">
        <CardHeader className="flex flex-col items-center gap-2 pb-10">
          {/* Logo Placeholder gamit ang ftp.svg */}
          <div className="mb-4">
            <img src={ftpLogo} alt="FTP Logo" className="w-20 h-20 object-contain" />
          </div>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight text-center">FTP Leave Portal</h1>
          <p className="text-slate-400 text-sm font-medium">Secure Employee Access</p>
        </CardHeader>

        <CardBody className="overflow-visible">
          <form onSubmit={handleLogin} className="flex flex-col gap-6">
            <Input
              isRequired
              label="Username"
              labelPlacement="outside"
              placeholder="Enter your username"
              variant="bordered"
              size="lg"
              classNames={{
                label: "font-bold text-slate-600",
                inputWrapper: "border-slate-200 focus-within:!border-green-600 shadow-sm",
              }}
              value={username}
              onValueChange={setUsername}
            />

            <Input
              isRequired
              label="Password"
              labelPlacement="outside"
              placeholder="••••••••"
              variant="bordered"
              size="lg"
              classNames={{
                label: "font-bold text-slate-600",
                inputWrapper: "border-slate-200 focus-within:!border-green-600 shadow-sm",
              }}
              endContent={
                <button className="focus:outline-none" type="button" onClick={toggleVisibility}>
                  {isVisible ? (
                    <Icon icon="solar:eye-closed-bold" className="text-2xl text-default-400" />
                  ) : (
                    <Icon icon="solar:eye-bold" className="text-2xl text-default-400" />
                  )}
                </button>
              }
              type={isVisible ? "text" : "password"}
              value={password}
              onValueChange={setPassword}
            />

            <div className="flex justify-between items-center px-1">
              <Checkbox 
                size="sm" 
                classNames={{ 
                    label: "text-slate-500 font-medium",
                    wrapper: "after:bg-green-600" // Green checkbox
                }}
              >
                Remember me
              </Checkbox>
              <Link size="sm" href="#" className="font-bold text-green-700 underline-offset-4 hover:text-green-800 hover:underline">
                Forgot password?
              </Link>
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-danger-50 rounded-xl border border-danger-100">
                <Icon icon="solar:danger-bold" className="text-danger" />
                <p className="text-danger text-xs font-bold">{error}</p>
              </div>
            )}

            <Button 
              type="submit" 
              isLoading={loading}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-black py-7 rounded-2xl shadow-xl shadow-green-100 transition-all active:scale-[0.98]"
            >
              SIGN IN TO DASHBOARD
            </Button>
          </form>

          <div className="mt-10 flex flex-col items-center gap-4">
            <Divider className="opacity-50" />
            <p className="text-slate-400 text-[11px] font-bold uppercase tracking-[0.2em]">
              Powered by FTP IT Dept. v1.0
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}