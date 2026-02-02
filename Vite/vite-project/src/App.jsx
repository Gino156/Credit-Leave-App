import { useState, useEffect } from 'react';
import { 
  Card, CardHeader, CardBody, Divider, Button, Chip, Spinner,
  User, Skeleton
} from "@heroui/react";

import LoginPage from './components/LoginPage';
import MainNavbar from './components/MainNavbar';
import LeaveHistoryTable from './components/LeaveHistoryTable';

// Icons
export const PlusIcon = ({ fill = "currentColor", size = 24 }) => (
  <svg fill="none" height={size} viewBox="0 0 24 24" width={size} xmlns="http://www.w3.org/2000/svg">
    <path d="M12 5V19M5 12H19" stroke={fill} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

function App() {
  // --- STATES ---
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("access_token"));
  const [leaveHistory, setLeaveHistory] = useState([]);
  const [apiData, setApiData] = useState("Loading...");
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- DATA FETCHING ---
  useEffect(() => {
    if (!isAuthenticated) return;

    const BASE_URL = "http://127.0.0.1:8000";
    const myToken = localStorage.getItem("access_token");

    // 1. Check Backend Health
    fetch(BASE_URL)
      .then(res => res.json())
      .then(data => setApiData(data.message))
      .catch(() => setApiData("Server Offline"));

    // 2. Fetch Leave History
    // Dahil sa backend logic sa taas, ang 'myToken' na ito ay may dalang 'id: 1'
    fetch(`${BASE_URL}/LeaveHistory`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${myToken}`,
        'Content-Type': 'application/json'
      }
    })
      .then((res) => {
        if (res.status === 401) {
          handleLogout();
          throw new Error("Session Expired");
        }
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((data) => {
        // Ang 'data' na darating dito ay puro records lang ni EmployeeID = 1 (Gino Reyes)
        setLeaveHistory(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Fetch Error:", error);
        setLoading(false);
      });
  }, [isAuthenticated]);

  // --- HANDLERS ---
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setIsAuthenticated(false);
    setLeaveHistory([]);
  };

  const handleRequestLeave = async () => {
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsSubmitting(false);
  };

  // Stats calculation based on filtered data
  const stats = [
    { label: "Ending balance", value: leaveHistory[0]?.EndingBalance || "0", color: "text-black-600" },
    { label: "Earned", value: "10", color: "text-blue-600" },
    { label: "Consumed", value: leaveHistory.filter(l => l.ApprovalStatus === 'Approved').length || "0", color: "text-red-600" },
    { label: "Available", value: leaveHistory[0]?.AvailableCredits || "0", color: "text-green-600" }
  ];

  // --- AUTH BOUNCER ---
  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  // --- MAIN DASHBOARD RENDER ---
  return (
    <div className="min-h-screen bg-gray-50 pb-10">
      <MainNavbar onLogout={handleLogout} />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-6 sm:gap-8">
        
        {/* PROFILE HEADER - This will show 'Gino Reyes' if the backend filter is working */}
        <section className="flex flex-col sm:flex-row justify-between items-center bg-white p-5 sm:p-6 rounded-2xl shadow-sm border border-gray-100 gap-4">
          <User
            avatarProps={{ 
              showFallback: true, 
              size: "lg", 
              isBordered: true,
              className: "border-green-600 border-2 bg-white text-slate-400" 
            }}
            description={`Employee ID: ${leaveHistory[0]?.EmployeeID || "Loading..."}`}
            name={loading ? <Skeleton className="h-4 w-32 rounded-lg" /> : (leaveHistory[0]?.EmployeeName || "User")}
            className="transition-transform hover:scale-105 uppercase font-bold"
          />
          <Button 
            color="success" 
            variant="shadow" 
            startContent={!isSubmitting && <PlusIcon size={20} />} 
            radius="full" 
            className="text-white font-bold w-full sm:w-auto bg-green-600"
            isLoading={isSubmitting}
            onPress={handleRequestLeave}
          >
            Request Leave
          </Button>
        </section>

        {/* STATS CARDS */}
        <div className="flex flex-row overflow-x-auto overflow-y-hidden gap-4 pb-4 sm:grid sm:grid-cols-4 sm:overflow-x-visible sm:pb-0 scrollbar-hide">
          {stats.map((stat, i) => (
            <Card key={i} className="min-w-35 sm:min-w-0 border-none shadow-sm shrink-0 sm:shrink">
              <CardBody className="flex flex-col items-center justify-center p-4 sm:py-8 gap-1">
                <p className={`text-2xl sm:text-4xl font-black ${stat.color}`}>{stat.value}</p>
                <p className="font-bold text-blue-500 uppercase text-[10px] tracking-wider">{stat.label}</p>
                <small className="text-gray-400 text-[10px]">Leaves</small>
              </CardBody>
            </Card>
          ))}
        </div>

        {/* BOTTOM SECTION */}
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-6 sm:gap-8">
          
          <Card className="shadow-sm xl:col-span-2 overflow-hidden">
            <CardHeader className="flex flex-col items-start px-6 pt-6 pb-2">
              <p className="text-tiny uppercase font-bold text-primary tracking-wider">Live Connection</p>
              <h2 className="text-xl font-bold">FastAPI Status</h2>
            </CardHeader>
            <Divider className="opacity-50" />
            <CardBody className="py-12 flex flex-col items-center justify-center">
              {loading ? <Spinner color="primary" /> : (
                <div className="text-center group">
                  <p className="text-lg font-bold mb-4 text-gray-700">{apiData}</p>
                  <Chip 
                    color={apiData.toLowerCase().includes("running") || apiData.toLowerCase().includes("welcome") ? "success" : "danger"} 
                    variant="flat"
                    className="px-4 py-1"
                  >
                    {apiData.toLowerCase().includes("running") || apiData.toLowerCase().includes("welcome") ? "● Server Online" : "○ Offline"}
                  </Chip>
                </div>
              )}
            </CardBody>
            <Divider className="opacity-50" />
            <div className="p-4 flex justify-between items-center bg-gray-50/30">
              <span className="text-[10px] text-gray-400 font-mono tracking-tighter">BUILD v1.0.0-PROD</span>
              <Button size="sm" variant="light" color="primary" className="font-bold" onPress={() => window.location.reload()}>Refresh</Button>
            </div>
          </Card>

          {/* LEAVE HISTORY TABLE */}
          <LeaveHistoryTable data={leaveHistory} loading={loading} />
          
        </div>
      </main>
    </div>
  );
}

export default App;