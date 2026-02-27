import { Outlet, useLocation, Link } from "react-router";
import { Home, ShoppingCart, Store, LayoutDashboard, Monitor, Package } from "lucide-react";

export function Layout() {
    const location = useLocation();
    const isLanding = location.pathname === "/";
    const isManagementRoute = location.pathname.includes("/dashboard") || location.pathname.includes("/devices");

    return (
        <div className="min-h-screen bg-gray-50">
            {!isLanding && (
                <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex justify-between items-center h-16">
                            <Link to="/" className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-[#10b981] to-[#3b82f6] rounded-lg flex items-center justify-center">
                                    <ShoppingCart className="w-5 h-5 text-white" />
                                </div>
                                <span className="text-xl font-semibold text-gray-900">SmartGrocer AI</span>
                            </Link>

                            <div className="flex gap-2">
                                <Link
                                    to="/"
                                    className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${location.pathname === "/" ? "bg-[#10b981] text-white" : "text-gray-600 hover:bg-gray-100"
                                        }`}
                                >
                                    <Home className="w-4 h-4" />
                                    <span className="hidden sm:inline">Home</span>
                                </Link>
                                <Link
                                    to="/assistant"
                                    className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${location.pathname === "/assistant" ? "bg-[#10b981] text-white" : "text-gray-600 hover:bg-gray-100"
                                        }`}
                                >
                                    <ShoppingCart className="w-4 h-4" />
                                    <span className="hidden sm:inline">Assistant</span>
                                </Link>
                                <Link
                                    to="/products"
                                    className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${location.pathname === "/products" ? "bg-[#10b981] text-white" : "text-gray-600 hover:bg-gray-100"
                                        }`}
                                >
                                    <Package className="w-4 h-4" />
                                    <span className="hidden sm:inline">Products</span>
                                </Link>
                                <Link
                                    to="/stores"
                                    className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${location.pathname === "/stores" ? "bg-[#10b981] text-white" : "text-gray-600 hover:bg-gray-100"
                                        }`}
                                >
                                    <Store className="w-4 h-4" />
                                    <span className="hidden sm:inline">Stores</span>
                                </Link>
                                {!isManagementRoute && (
                                    <Link
                                        to="/dashboard"
                                        className="px-4 py-2 rounded-lg flex items-center gap-2 text-gray-600 hover:bg-gray-100 transition-colors border border-gray-200"
                                    >
                                        <LayoutDashboard className="w-4 h-4" />
                                        <span className="hidden sm:inline">Dashboard</span>
                                    </Link>
                                )}
                                {isManagementRoute && (
                                    <>
                                        <Link
                                            to="/dashboard"
                                            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${location.pathname === "/dashboard" ? "bg-[#10b981] text-white" : "text-gray-600 hover:bg-gray-100"
                                                }`}
                                        >
                                            <LayoutDashboard className="w-4 h-4" />
                                            <span className="hidden sm:inline">Dashboard</span>
                                        </Link>
                                        <Link
                                            to="/devices"
                                            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${location.pathname === "/devices" ? "bg-[#10b981] text-white" : "text-gray-600 hover:bg-gray-100"
                                                }`}
                                        >
                                            <Monitor className="w-4 h-4" />
                                            <span className="hidden sm:inline">Devices</span>
                                        </Link>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </nav>
            )}
            <main>
                <Outlet />
            </main>
        </div>
    );
}
