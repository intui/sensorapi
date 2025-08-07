import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Database, MapPin, Thermometer, BarChart3, Activity, Zap } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Sensors', href: '/sensors', icon: Thermometer },
    { name: 'Locations', href: '/locations', icon: MapPin },
    { name: 'Sensor Types', href: '/sensor-types', icon: Database },
    { name: 'Readings', href: '/readings', icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Modern Dark Navigation */}
      <nav className="bg-gray-900/50 backdrop-blur-xl border-b border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <div className="w-10 h-10 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <span className="ml-3 text-xl font-bold text-white">
                  Sensor Hub
                </span>
              </div>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                        isActive
                          ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/30'
                          : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content - Remove padding to let dashboard handle its own spacing */}
      <main>
        {children}
      </main>
    </div>
  );
};

export default Layout;