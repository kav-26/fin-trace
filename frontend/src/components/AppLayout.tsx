import { Link, Outlet, useLocation } from "react-router-dom"
import { Search, FileText, BarChart3, History, Database } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { path: "/", label: "Investigate", icon: Search },
  { path: "/report", label: "Report", icon: FileText },
  { path: "/financial-data", label: "Financial Data", icon: BarChart3 },
  { path: "/history", label: "History", icon: History },
  { path: "/data-sources", label: "Data & Sources", icon: Database },
]

export default function AppLayout() {
  const location = useLocation()

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 flex flex-col">
        <div className="px-6 py-5 border-b border-slate-800">
          <div className="text-xs font-mono tracking-widest text-amber-400">FIN-TRACE</div>
          <div className="text-sm text-slate-400 mt-1">Financial Investigation Engine</div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-amber-400/10 text-amber-400"
                    : "text-slate-400 hover:text-slate-100 hover:bg-slate-900"
                )}
              >
                <Icon size={16} />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="px-6 py-4 border-t border-slate-800 text-xs text-slate-500 font-mono">
          v0.1.0 — local
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}