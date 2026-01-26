import { useState, useEffect } from 'react';
import { 
  Card, CardHeader, CardBody, Divider, Button, Chip, Spinner,
  Table, TableHeader, TableColumn, TableBody, TableRow, TableCell,
  Navbar, NavbarBrand, NavbarContent, NavbarItem, NavbarMenuToggle, NavbarMenu, NavbarMenuItem, Link,
  User
} from "@heroui/react";


// Icons
export const AcmeLogo = () => (
  <svg fill="none" height="36" viewBox="0 0 32 32" width="36">
    <path clipRule="evenodd" fillRule="evenodd" d="M21.5 6H8L5 26H8.5L9.5 19H17.5L18 16H10L10.8 11H20.8L21.5 6Z" fill="currentColor" />
  </svg>
);

export const PlusIcon = ({ fill = "currentColor", size = 24 }) => (
  <svg fill="none" height={size} viewBox="0 0 24 24" width={size} xmlns="http://www.w3.org/2000/svg">
    <path d="M12 5V19M5 12H19" stroke={fill} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

function App() {
  const [leaveHistory, setLeaveHistory] = useState([]);
  const [apiData, setApiData] = useState("Loading...");
  const [loading, setLoading] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then(res => res.json())
      .then(data => { setApiData(data.message); setLoading(false); })
      .catch(() => { setApiData("Server Offline"); setLoading(false); });

    fetch("http://localhost:8000/LeaveHistory") 
      .then((res) => res.json())
      .then((data) => {
        setLeaveHistory(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setLoading(false);
      });
  }, []);

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'danger';
      default: return 'default';
    }
  };

  const stats = [
    { label: "Ending balance", value: "8", color: "text-black-600", bg: "bg-green-50" },
    { label: "Earned", value: "10", color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Consumed", value: "1", color: "text-red-600", bg: "bg-orange-50" },
    { label: "Available", value: "18", color: "text-green-600", bg: "bg-green-50" }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-10">
      {/* NAVBAR */}
      <Navbar isMenuOpen={isMenuOpen} onMenuOpenChange={setIsMenuOpen} isBordered className="bg-white">
        <NavbarContent>
          <NavbarMenuToggle aria-label={isMenuOpen ? "Close menu" : "Open menu"} className="sm:hidden" />
          <NavbarBrand>
            <AcmeLogo />
            <p className="font-bold text-inherit ml-2 tracking-tight">LEAVE CREDIT APP</p>
          </NavbarBrand>
        </NavbarContent>

        <NavbarContent className="hidden sm:flex gap-8" justify="center">
          <NavbarItem><Link color="foreground" href="#">Dashboard</Link></NavbarItem>
          <NavbarItem isActive><Link href="#" aria-current="page">Leave Credits</Link></NavbarItem>
          <NavbarItem><Link color="foreground" href="#">Settings</Link></NavbarItem>
        </NavbarContent>

        {/* <NavbarContent justify="end">
          <NavbarItem>
            <Button as={Link} color="primary" href="#" variant="flat" radius="full" size="sm" className="font-semibold">Login</Button>
          </NavbarItem>
        </NavbarContent> */}

        <NavbarMenu>
          <NavbarMenuItem><Link className="w-full" href="#" size="lg">Dashboard</Link></NavbarMenuItem>
          <NavbarMenuItem><Link className="w-full" href="#" size="lg">Settings</Link></NavbarMenuItem>
          <NavbarMenuItem><Link className="w-full" color="danger" href="#" size="lg">Log Out</Link></NavbarMenuItem>
        </NavbarMenu>
      </Navbar>

      {/* MAIN CONTENT */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 flex flex-col gap-6 sm:gap-8">
        
        {/* PROFILE HEADER - Responsive Layout */}
        <section className="flex flex-col sm:flex-row justify-between items-center bg-white p-5 sm:p-6 rounded-2xl shadow-sm border border-gray-100 gap-4">
          <User
            avatarProps={{showFallback: true, size: "lg", src: "", isBordered: true, color: "default" }}
            description="Employee ID: E25-0296"
            name="Gino Reyes"
            className="transition-transform hover:scale-105"
          />
          <Button color="success" variant="shadow" startContent={<PlusIcon size={20} />} radius="full" className="text-white font-bold w-full sm:w-auto">
            Request Leave
          </Button>
        </section>

        {/* STATS CARDS - Mobile Scrollable, Desktop Grid */}
        <div className="flex flex-row overflow-x-auto overflow-y-hidden gap-4 pb-4 sm:grid sm:grid-cols-4 sm:overflow-x-visible sm:pb-0 scrollbar-hide  ">
          {stats.map((stat, i) => (
            <Card 
              key={i} 
              className="min-w-35 sm:min-w-0 border-none shadow-sm shrink-0 sm:shrink"
            >
              <CardBody className="flex flex-col items-center justify-center p-4 sm:py-8 gap-1">
                {/* Large Number */}
                <p className={`text-2xl sm:text-4xl font-black ${stat.color}`}>
                  {stat.value}
                </p>
                
                {/* Label (e.g., EARNED) */}
                <p className="font-bold text-blue-500 uppercase text-[10px] tracking-wider">
                  {stat.label}
                </p>
                
                {/* Sub-label (Leaves) */}
                <small className="text-gray-400 text-[10px]">
                  Leaves
                </small>
              </CardBody>
            </Card>
          ))}
        </div>

        {/* BOTTOM SECTION: STATUS & HISTORY */}
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-6 sm:gap-8">
          
          {/* SYSTEM STATUS (2/5 width on large) */}
          <Card className="shadow-sm xl:col-span-2 overflow-hidden">
            <CardHeader className="flex flex-col items-start px-6 pt-6 pb-2">
              <p className="text-tiny uppercase font-bold text-primary tracking-wider">Live Connection</p>
              <h2 className="text-xl font-bold">FastAPI Status</h2>
            </CardHeader>
            <Divider className="opacity-50" />
            <CardBody className="py-12 flex flex-col items-center justify-center">
              {loading ? <Spinner color="primary" /> : (
                <div className="text-center group">
                  <p className="text-lg font-bold mb-4 text-gray-700 transition-colors group-hover:text-primary">{apiData}</p>
                  <Chip 
                    color={apiData.includes("Welcome") ? "success" : "danger"} 
                    variant="flat"
                    className="px-4 py-1"
                  >
                    {apiData.includes("Welcome") ? "● Server Online" : "○ Offline"}
                  </Chip>
                </div>
              )}
            </CardBody>
            <Divider className="opacity-50" />
            <div className="p-4 flex justify-between items-center bg-gray-50/30">
              <span className="text-[10px] text-gray-400 font-mono tracking-tighter">BUILD v1.0.0-BETA</span>
              <Button size="sm" variant="light" color="primary" className="font-bold" onPress={() => window.location.reload()}>Refresh</Button>
            </div>
          </Card>

          {/* HISTORY TABLE (3/5 width on large) */}
          <Card className="shadow-sm xl:col-span-3">
            <CardHeader className="px-6 pt-6 pb-2 flex justify-between items-center">
              <h2 className="text-xl font-bold">Leave History</h2>
              <Link href="#" size="sm" className="font-bold underline-offset-4" showAnchorIcon>Details</Link>
            </CardHeader>
            <Divider className="opacity-50" />
            <CardBody className="px-2 sm:px-4">
              <Table isStriped aria-label="Leave History" removeWrapper shadow="none" className="min-w-full">
                <TableHeader>
                  <TableColumn className="bg-transparent text-gray-400">ID</TableColumn>
                  <TableColumn className="bg-transparent text-gray-400">DATE CREATED</TableColumn>
                  <TableColumn className="bg-transparent text-gray-400">BEGIN DATE</TableColumn>
                  <TableColumn className="bg-transparent text-gray-400">END DATE</TableColumn>
                  <TableColumn className="bg-transparent text-gray-400">TYPE</TableColumn>
                  <TableColumn className="bg-transparent text-gray-400">STATUS</TableColumn>
                </TableHeader>
                <TableBody emptyContent={"No rows to display."} isLoading={loading}>
                  {leaveHistory.map((item) => (
                    <TableRow key={item.LeaveApplicationId} className="border-b border-gray-50 last:border-none">
                      <TableCell className="font-bold">{item.LeaveApplicationId}</TableCell>
                      <TableCell className="text-xs">{item.DateCreated}</TableCell>
                      <TableCell className="text-xs">{item.BeginDate}</TableCell>
                      <TableCell className="text-xs">{item.EndDate}</TableCell>
                      <TableCell className="text-xs">{item.TimeOffType}</TableCell>
                      <TableCell>
                        <Chip size="sm" color={getStatusColor(item.ApprovalStatus)} variant="dot" className="border-none font-bold">
                          {item.ApprovalStatus}
                        </Chip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardBody>
          </Card>

        </div>
      </main>
    </div>
  );
}

export default App;