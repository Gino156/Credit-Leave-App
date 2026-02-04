import { useState, useEffect } from 'react';
import { Button, Input, Checkbox, Link } from "@heroui/react";
import { Icon } from "@iconify/react";
import { motion, AnimatePresence } from "framer-motion";

// Siguraduhin na tama ang path na ito
import ftpLogo from '../assets/ftp.svg'; 

export default function LoginPage({ onLoginSuccess }) {
  const [step, setStep] = useState(1);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (step === 1) {
      const timer = setTimeout(() => setStep(2), 3000); 
      return () => clearTimeout(timer);
    }
  }, [step]);

  const toggleVisibility = () => setIsVisible(!isVisible);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch("http://172.96.10.161:8000/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("access_token", data.access_token);
        onLoginSuccess();
      } else {
        setError(data.detail || "Invalid credentials.");
      }
    } catch (err) {
      setError("System unreachable.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex items-center justify-center min-h-screen bg-[#fcfcfc] overflow-hidden font-sans">
      <AnimatePresence mode="wait">
        
        {/* STEP 1: REVISED SPLASH SCREEN */}
        {/* STEP 1: REVISED SPLASH SCREEN */}
        {step === 1 && (
          <motion.div 
            key="splash"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-green-600"
          >
            {/* Binawasan ang padding (mula p-8 naging p-4) para lumiit ang border */}
            {/* Dinagdagan ang size ng image (mula w-24 naging w-40) para lumaki ang logo */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, ease: "backOut" }}
              className="bg-white p-3 rounded-4xl shadow-2xl flex items-center justify-center"
            >
              <img 
                src={ftpLogo} 
                className="w-40 h-40 object-contain" 
                alt="FTP Logo" 
              />
            </motion.div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-8 text-center"
            >
              <h1 className="text-white text-3xl font-black tracking-tighter uppercase">FTP LEAVE APP</h1>
              <p className="text-green-100 text-xs font-bold tracking-[0.3em] mt-1 opacity-70">PORTAL V1.3</p>
            </motion.div>
          </motion.div>
        )}

        {/* STEP 2: INTRO CARD */}
        {step === 2 && (
          <motion.div 
            key="intro"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full max-w-sm flex flex-col items-center p-6"
          >
            <div className="w-full h-112.5 rounded-[3.5rem] overflow-hidden mb-10 shadow-xl relative">
               <img 
                src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=1000" 
                className="w-full h-full object-cover"
                alt="Working Team"
              />
              <div className="absolute inset-0 bg-linear-to-t from-green-900/40 to-transparent" />
            </div>
            <div className="text-center px-4">
              <h2 className="text-3xl font-black text-slate-800 leading-tight">Manage Leaves <br/>Easily.</h2>
              <p className="text-slate-500 mt-4 mb-10 text-lg">Track your credits and file applications in one tap.</p>
              <Button 
                onPress={() => setStep(3)}
                className="bg-green-600 text-white font-black w-full h-16 rounded-2xl shadow-xl shadow-green-200 text-lg"
              >
                GET STARTED
              </Button>
            </div>
          </motion.div>
        )}

        {/* STEP 3: LOGIN FORM */}
        {step === 3 && (
          <motion.div 
            key="login"
            initial={{ x: 30, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="w-full max-w-sm px-8"
          >
            <div className="mb-10 flex flex-col items-center sm:items-start">
               <img src={ftpLogo} alt="FTP Logo" className="w-20 h-20 mb-6" />
               <h1 className="text-4xl font-black text-slate-800 tracking-tight">FTP Leave App</h1>
               <p className="text-slate-400 font-bold mt-2">Secure Employee Access</p>
            </div>

            <form onSubmit={handleLogin} className="flex flex-col gap-5">
              <Input
                isRequired
                label="Username"
                labelPlacement="outside"
                placeholder="Enter username"
                variant="flat"
                size="lg"
                classNames={{ inputWrapper: "bg-slate-100 rounded-2xl h-14", label: "font-bold text-slate-600" }}
                value={username}
                onValueChange={setUsername}
              />

              <Input
                isRequired
                label="Password"
                labelPlacement="outside"
                placeholder="••••••••"
                variant="flat"
                size="lg"
                classNames={{ inputWrapper: "bg-slate-100 rounded-2xl h-14", label: "font-bold text-slate-600" }}
                type={isVisible ? "text" : "password"}
                endContent={
                  <button type="button" onClick={toggleVisibility}>
                    <Icon icon={isVisible ? "solar:eye-closed-bold" : "solar:eye-bold"} className="text-2xl text-slate-400" />
                  </button>
                }
                value={password}
                onValueChange={setPassword}
              />

              {error && (
                <div className="flex items-center gap-2 p-4 bg-red-50 rounded-2xl border border-red-100">
                  <Icon icon="solar:danger-bold" className="text-red-500" />
                  <p className="text-red-600 text-xs font-bold">{error}</p>
                </div>
              )}

              <Button 
                type="submit" 
                isLoading={loading}
                className="w-full bg-green-600 text-white font-black h-16 rounded-2xl shadow-xl shadow-green-200 mt-4"
              >
                LOG IN
              </Button>
            </form>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}