import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, User, History, Ban, Shield, LogOut, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/stores/auth";
import { useState } from "react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Объявления" },
  { to: "/profile", icon: User, label: "Профиль" },
  { to: "/history", icon: History, label: "История" },
  { to: "/blacklist", icon: Ban, label: "Чёрный список" },
];

export function MainLayout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => { logout(); navigate("/login"); };

  const nav = (
    <nav className="flex flex-col gap-1 p-4">
      {navItems.map((item) => (
        <NavLink key={item.to} to={item.to} end={item.to === "/"}
          onClick={() => setSidebarOpen(false)}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${isActive ? "bg-primary/10 text-primary font-medium" : "text-muted-foreground hover:bg-muted hover:text-foreground"}`
          }>
          <item.icon className="h-4 w-4" />
          {item.label}
        </NavLink>
      ))}
      {user?.role === "ADMIN" && (
        <>
          <Separator className="my-2" />
          <NavLink to="/admin" onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${isActive ? "bg-primary/10 text-primary font-medium" : "text-muted-foreground hover:bg-muted hover:text-foreground"}`
            }>
            <Shield className="h-4 w-4" />
            Админка
          </NavLink>
        </>
      )}
    </nav>
  );

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop sidebar */}
      <aside className="hidden w-56 flex-col border-r border-border bg-card md:flex">
        <div className="p-4">
          <h1 className="text-lg font-bold text-foreground">P2P Aggregator</h1>
          <Badge variant="outline" className="mt-1 text-[10px] border-yellow-500/50 text-yellow-500">READ-ONLY</Badge>
        </div>
        <Separator />
        {nav}
        <div className="mt-auto p-4">
          <div className="text-xs text-muted-foreground mb-2 truncate">{user?.email}</div>
          <Button variant="ghost" size="sm" className="w-full justify-start text-muted-foreground" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />Выйти
          </Button>
        </div>
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={() => setSidebarOpen(false)} />}
      <aside className={`fixed inset-y-0 left-0 z-50 w-56 flex-col border-r border-border bg-card transition-transform md:hidden ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex items-center justify-between p-4">
          <h1 className="text-lg font-bold">P2P Aggregator</h1>
          <Button variant="ghost" size="sm" onClick={() => setSidebarOpen(false)}><X className="h-4 w-4" /></Button>
        </div>
        <Separator />
        {nav}
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center gap-4 border-b border-border bg-card px-4 md:hidden">
          <Button variant="ghost" size="sm" onClick={() => setSidebarOpen(true)}><Menu className="h-5 w-5" /></Button>
          <span className="font-semibold">P2P Aggregator</span>
          <Badge variant="outline" className="text-[10px] border-yellow-500/50 text-yellow-500">READ-ONLY</Badge>
        </header>
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
