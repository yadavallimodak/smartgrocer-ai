import React from 'react';
import { Tablet, Activity, TrendingDown, RefreshCcw, AlertCircle, ShoppingCart, Target, Search } from 'lucide-react';

export default function Dashboard() {
    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-gray-50 min-h-screen">
            {/* Top Header */}
            <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight">AgentGo Management</h1>
                    <p className="text-sm text-gray-500 mt-1">Fleet Health & Shopper Insights Overview</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="relative w-full sm:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search devices or metrics..."
                            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-[#10b981] text-sm"
                        />
                    </div>
                </div>
            </header>

            {/* KPI Summary Cards */}
            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Active Tablets */}
                <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                        <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center">
                            <Tablet className="w-6 h-6" />
                        </div>
                        <span className="flex items-center gap-1.5 px-2.5 py-1 bg-green-50 text-green-700 rounded-full text-xs font-semibold border border-green-100">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                            Healthy
                        </span>
                    </div>
                    <div>
                        <h3 className="text-3xl font-bold text-gray-900">142<span className="text-lg text-gray-400 font-medium"> / 145</span></h3>
                        <p className="text-sm font-medium text-gray-500 mt-1">Active Kiosks</p>
                    </div>
                </div>

                {/* Avg Response Time */}
                <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center">
                            <Activity className="w-6 h-6" />
                        </div>
                    </div>
                    <div>
                        <h3 className="text-3xl font-bold text-gray-900">1.2s</h3>
                        <p className="text-sm font-medium text-gray-500 mt-1">Avg Query Latency</p>
                    </div>
                </div>

                {/* Lost Sales Value */}
                <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                        <div className="w-12 h-12 bg-red-50 text-red-600 rounded-xl flex items-center justify-center">
                            <TrendingDown className="w-6 h-6" />
                        </div>
                        <span className="px-2.5 py-1 bg-red-50 text-red-700 rounded-full text-xs font-semibold">
                            +12% vs last week
                        </span>
                    </div>
                    <div>
                        <h3 className="text-3xl font-bold text-gray-900">$2,410</h3>
                        <p className="text-sm font-medium text-gray-500 mt-1">Est. Lost Sales (OOS)</p>
                    </div>
                </div>

                {/* Competitor Redirects */}
                <div className="bg-gradient-to-br from-[#10b981] to-[#0d9488] p-6 rounded-2xl shadow-lg flex flex-col justify-between text-white relative overflow-hidden">
                    <div className="absolute -right-6 -top-6 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
                    <div className="flex justify-between items-start mb-4 relative z-10">
                        <div className="w-12 h-12 bg-white/20 text-white rounded-xl flex items-center justify-center backdrop-blur-sm">
                            <RefreshCcw className="w-6 h-6" />
                        </div>
                    </div>
                    <div className="relative z-10">
                        <h3 className="text-3xl font-bold text-white">84</h3>
                        <p className="text-sm font-medium text-emerald-50 mt-1">Competitor Redirects</p>
                    </div>
                </div>
            </section>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Shopper Insights Column */}
                <div className="col-span-1 lg:col-span-2 space-y-6">
                    {/* Top OOS Queries */}
                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <ShoppingCart className="w-5 h-5 text-gray-400" />
                                Top Queried Out-of-Stock Items
                            </h2>
                            <button className="text-sm text-[#10b981] font-medium hover:underline">View All</button>
                        </div>
                        <div className="space-y-4">
                            {[
                                { item: "Organic Strawberries", queries: 145, trend: "+12%" },
                                { item: "Almond Breeze Unsweetened", queries: 98, trend: "+5%" },
                                { item: "Sourdough Boule", queries: 76, trend: "-2%" },
                                { item: "Vital Farms Pasture Eggs", queries: 64, trend: "+18%" },
                            ].map((row, i) => (
                                <div key={i} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-xl transition-colors border border-transparent hover:border-gray-100">
                                    <div className="flex items-center gap-4">
                                        <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center font-bold text-gray-500 text-sm">{i + 1}</div>
                                        <span className="font-semibold text-gray-800">{row.item}</span>
                                    </div>
                                    <div className="flex items-center gap-6">
                                        <span className="text-sm text-gray-500 font-medium">{row.queries} queries</span>
                                        <span className={`text-xs font-bold w-12 text-right ${row.trend.startsWith('+') ? 'text-red-500' : 'text-green-500'}`}>{row.trend}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Competitor Redirection Destinations */}
                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <Target className="w-5 h-5 text-gray-400" />
                                Top Competitor Destinations
                            </h2>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 border border-gray-100 rounded-xl bg-gray-50">
                                <span className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Whole Foods Market</span>
                                <div className="mt-2 flex items-baseline gap-2">
                                    <span className="text-2xl font-bold text-gray-900">42</span>
                                    <span className="text-sm text-gray-500">redirects</span>
                                </div>
                            </div>
                            <div className="p-4 border border-gray-100 rounded-xl bg-gray-50">
                                <span className="text-sm font-semibold text-gray-500 uppercase tracking-wider">H-E-B</span>
                                <div className="mt-2 flex items-baseline gap-2">
                                    <span className="text-2xl font-bold text-gray-900">28</span>
                                    <span className="text-sm text-gray-500">redirects</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Fleet Health Column */}
                <div className="col-span-1 space-y-6">
                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 h-full">
                        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                            <AlertCircle className="w-5 h-5 text-gray-400" />
                            Device Alerts
                        </h2>

                        <div className="space-y-4">
                            {/* Alert Card */}
                            <div className="p-4 border border-red-100 bg-red-50 rounded-xl">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h4 className="font-semibold text-red-900 text-sm">Kiosk Offline</h4>
                                        <p className="text-xs text-red-700 mt-1">Aisle 12 (Dairy)</p>
                                    </div>
                                    <span className="text-xs font-medium text-red-500 bg-red-100 px-2 py-1 rounded">12m ago</span>
                                </div>
                                <button className="mt-3 w-full py-1.5 bg-white border border-red-200 text-red-700 text-xs font-semibold rounded-lg hover:bg-red-50 transition-colors">
                                    Remote Restart
                                </button>
                            </div>

                            {/* Alert Card */}
                            <div className="p-4 border border-amber-100 bg-amber-50 rounded-xl">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h4 className="font-semibold text-amber-900 text-sm">High Latency</h4>
                                        <p className="text-xs text-amber-700 mt-1">Produce Section Endcap</p>
                                    </div>
                                    <span className="text-xs font-medium text-amber-600 bg-amber-100 px-2 py-1 rounded">1h ago</span>
                                </div>
                                <p className="mt-2 text-xs text-amber-800">Local node taking &gt;4s to respond.</p>
                            </div>

                            {/* Alert Card */}
                            <div className="p-4 border border-gray-100 bg-gray-50 rounded-xl">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h4 className="font-semibold text-gray-900 text-sm">Battery Low (15%)</h4>
                                        <p className="text-xs text-gray-600 mt-1">Checkout Lane 4</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-8">
                            <button className="w-full py-3 bg-[#10b981] hover:bg-[#0ea5e9] text-white font-semibold rounded-xl transition-all shadow-sm hover:shadow-md flex justify-center items-center gap-2">
                                <Tablet className="w-4 h-4" />
                                Deploy OTA Update
                            </button>
                            <p className="text-center text-xs text-gray-400 mt-2">v.1.2.4 available for 145 devices</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
