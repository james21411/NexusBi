import { Home, Database, Settings } from 'lucide-react';
import { 
  LayoutDashboard, 
  FolderOpen, 
  BarChart3, 
  FileText, 
  Sparkles, 
  Users, 
  Settings as SettingsIcon,
  Bell,
  HelpCircle,
  Archive
} from 'lucide-react';
import { useState } from 'react';

interface SidebarProps {
  onNavigate?: (view: string) => void;
  activeView?: string;
}

export function Sidebar({ onNavigate, activeView = 'dashboard' }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Accueil' },
    { id: 'data-sources', icon: Database, label: 'Sources' },
    { id: 'reports', icon: FileText, label: 'Rapports' },
    { id: 'analytics', icon: BarChart3, label: 'Analyses' },
    { id: 'projects', icon: FolderOpen, label: 'Projets' },
    { id: 'ai-assistant', icon: Sparkles, label: 'Assistant IA' },
    { id: 'team', icon: Users, label: 'Équipe' },
    { id: 'archive', icon: Archive, label: 'Archive' },
  ];

  const bottomItems = [
    { id: 'notifications', icon: Bell, label: 'Notifications', badge: 3 },
    { id: 'help', icon: HelpCircle, label: 'Aide' },
    { id: 'settings', icon: SettingsIcon, label: 'Paramètres' },
  ];

  return (
    <div className="w-20 bg-[#0056D2] flex flex-col items-center py-6">
      {/* Logo */}
      <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center mb-8">
        <span className="text-[#0056D2]">N</span>
      </div>
      
      {/* Menu principal */}
      <div className="flex-1 flex flex-col items-center gap-3 w-full px-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate?.(item.id)}
              className={`relative w-14 h-14 flex flex-col items-center justify-center rounded-lg transition-all group ${
                isActive 
                  ? 'bg-white text-[#0056D2]' 
                  : 'text-white hover:bg-white/10'
              }`}
              title={item.label}
            >
              <Icon size={22} />
              
              {/* Tooltip */}
              <div className="absolute left-full ml-3 px-3 py-1.5 bg-gray-900 text-white rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                {item.label}
                <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900"></div>
              </div>

              {/* Indicateur actif */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[#FF6B00] rounded-r"></div>
              )}
            </button>
          );
        })}
      </div>
      
      {/* Menu du bas */}
      <div className="flex flex-col items-center gap-3 w-full px-2 border-t border-white/20 pt-4">
        {bottomItems.map((item) => {
          const Icon = item.icon;
          
          return (
            <button
              key={item.id}
              className="relative w-14 h-14 flex flex-col items-center justify-center text-white hover:bg-white/10 rounded-lg transition-all group"
              title={item.label}
            >
              <Icon size={22} />
              
              {/* Badge de notification */}
              {item.badge && (
                <div className="absolute top-2 right-2 w-5 h-5 bg-[#FF6B00] text-white rounded-full flex items-center justify-center text-xs">
                  {item.badge}
                </div>
              )}
              
              {/* Tooltip */}
              <div className="absolute left-full ml-3 px-3 py-1.5 bg-gray-900 text-white rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                {item.label}
                <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900"></div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}