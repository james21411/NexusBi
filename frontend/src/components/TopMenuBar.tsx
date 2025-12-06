import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface MenuItem {
  label: string;
  items: { label: string; shortcut?: string; separator?: boolean }[];
}

interface TopMenuBarProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

const menuItems: MenuItem[] = [
  {
    label: 'Fichier',
    items: [
      { label: 'Nouveau tableau de bord', shortcut: 'Ctrl+N' },
      { label: 'Ouvrir', shortcut: 'Ctrl+O' },
      { label: 'Enregistrer', shortcut: 'Ctrl+S' },
      { label: 'Enregistrer sous...', shortcut: 'Ctrl+Shift+S' },
      { label: '', separator: true },
      { label: 'Importer des données' },
      { label: 'Exporter', shortcut: 'Ctrl+E' },
      { label: '', separator: true },
      { label: 'Paramètres', shortcut: 'Ctrl+,' },
      { label: 'Quitter', shortcut: 'Ctrl+Q' },
    ],
  },
  {
    label: 'Édition',
    items: [
      { label: 'Annuler', shortcut: 'Ctrl+Z' },
      { label: 'Rétablir', shortcut: 'Ctrl+Y' },
      { label: '', separator: true },
      { label: 'Couper', shortcut: 'Ctrl+X' },
      { label: 'Copier', shortcut: 'Ctrl+C' },
      { label: 'Coller', shortcut: 'Ctrl+V' },
      { label: '', separator: true },
      { label: 'Rechercher', shortcut: 'Ctrl+F' },
      { label: 'Remplacer', shortcut: 'Ctrl+H' },
    ],
  },
  {
    label: 'Affichage',
    items: [
      { label: 'Plein écran', shortcut: 'F11' },
      { label: 'Zoom avant', shortcut: 'Ctrl++' },
      { label: 'Zoom arrière', shortcut: 'Ctrl+-' },
      { label: 'Zoom par défaut', shortcut: 'Ctrl+0' },
      { label: '', separator: true },
      { label: 'Afficher la barre latérale' },
      { label: 'Afficher l\'assistant IA' },
      { label: 'Afficher la barre d\'outils' },
    ],
  },
  {
    label: 'Données',
    items: [
      { label: 'Actualiser tout', shortcut: 'F5' },
      { label: 'Actualiser la sélection' },
      { label: '', separator: true },
      { label: 'Nettoyer les données' },
      { label: 'Transformer les données' },
      { label: 'Gérer les relations' },
      { label: '', separator: true },
      { label: 'Requête SQL' },
    ],
  },
  {
    label: 'Insertion',
    items: [
      { label: 'Graphique en barres' },
      { label: 'Graphique en lignes' },
      { label: 'Graphique circulaire' },
      { label: 'Tableau' },
      { label: '', separator: true },
      { label: 'Carte' },
      { label: 'Jauge' },
      { label: 'Indicateur KPI' },
      { label: '', separator: true },
      { label: 'Zone de texte' },
      { label: 'Image' },
    ],
  },
  {
    label: 'Outils',
    items: [
      { label: 'Assistant IA', shortcut: 'Ctrl+K' },
      { label: 'Générateur de requêtes' },
      { label: 'Nettoyage de données' },
      { label: '', separator: true },
      { label: 'Console Python' },
      { label: 'Terminal' },
      { label: '', separator: true },
      { label: 'Extensions' },
    ],
  },
  {
    label: 'Aide',
    items: [
      { label: 'Documentation' },
      { label: 'Tutoriels vidéo' },
      { label: 'Raccourcis clavier', shortcut: 'Ctrl+K Ctrl+S' },
      { label: '', separator: true },
      { label: 'Communauté' },
      { label: 'Signaler un bug' },
      { label: '', separator: true },
      { label: 'À propos de NexusBi' },
    ],
  },
];

export function TopMenuBar({ currentView = 'dashboard', onViewChange, onShowImportModal }: TopMenuBarProps) {
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setActiveMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="bg-[#0056D2] flex flex-col">
      {/* Ligne du haut - Menus principaux */}
      <div className="text-white h-9 flex items-center px-4 relative z-50" ref={menuRef}>
        {/* Logo et nom */}
        <div className="flex items-center gap-3 mr-6">
          <div className="w-6 h-6 bg-white rounded flex items-center justify-center">
            <span className="text-[#0056D2]">N</span>
          </div>
          <span className="text-white">NexusBi</span>
        </div>

        {/* Menus */}
        <div className="flex items-center gap-1">
          {menuItems.map((menu) => (
            <div key={menu.label} className="relative">
              <button
                className={`px-3 py-1 rounded hover:bg-white/10 transition-colors flex items-center gap-1 ${
                  activeMenu === menu.label ? 'bg-white/20' : ''
                }`}
                onClick={() => setActiveMenu(activeMenu === menu.label ? null : menu.label)}
              >
                {menu.label}
                <ChevronDown size={14} />
              </button>

              {/* Dropdown */}
              {activeMenu === menu.label && (
                <div className="absolute top-full left-0 mt-1 bg-white text-gray-800 rounded-lg shadow-xl border border-gray-200 min-w-[240px] py-1 z-50">
                  {menu.items.map((item, index) => (
                    item.separator ? (
                      <div key={index} className="h-px bg-gray-200 my-1" />
                    ) : (
                      <button
                        key={index}
                        className="w-full px-4 py-2 hover:bg-gray-100 flex items-center justify-between transition-colors text-left"
                        onClick={() => setActiveMenu(null)}
                      >
                        <span>{item.label}</span>
                        {item.shortcut && (
                          <span className="text-gray-500 ml-8">{item.shortcut}</span>
                        )}
                      </button>
                    )
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Zone droite - Info utilisateur */}
        <div className="ml-auto flex items-center gap-4">
          <div className="text-white/80 flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>En ligne</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-white/20 rounded-full flex items-center justify-center">
              <span>JD</span>
            </div>
            <span>Jean Dupont</span>
          </div>
        </div>
      </div>

      {/* Ligne du bas - Navigation des vues */}
      <div className="bg-[#0046b2] px-4 py-2 flex items-center gap-2">
        <button
          onClick={() => onViewChange?.('dashboard')}
          className={`px-4 py-1.5 rounded transition-colors ${
            currentView === 'dashboard' 
              ? 'bg-white text-[#0056D2]' 
              : 'text-white hover:bg-white/10'
          }`}
        >
          Tableau de Bord
        </button>
        <button
          onClick={() => onViewChange?.('sources')}
          className={`px-4 py-1.5 rounded transition-colors ${
            currentView === 'sources' 
              ? 'bg-white text-[#0056D2]' 
              : 'text-white hover:bg-white/10'
          }`}
        >
          Sources de Données
        </button>
        <button
          onClick={() => onViewChange?.('analytics')}
          className={`px-4 py-1.5 rounded transition-colors ${
            currentView === 'analytics' 
              ? 'bg-white text-[#0056D2]' 
              : 'text-white hover:bg-white/10'
          }`}
        >
          Analyses
        </button>
        <button
          onClick={() => onViewChange?.('reports')}
          className={`px-4 py-1.5 rounded transition-colors ${
            currentView === 'reports' 
              ? 'bg-white text-[#0056D2]' 
              : 'text-white hover:bg-white/10'
          }`}
        >
          Rapports
        </button>
        <button
          onClick={() => onViewChange?.('cleaning')}
          className={`px-4 py-1.5 rounded transition-colors ${
            currentView === 'cleaning' 
              ? 'bg-white text-[#0056D2]' 
              : 'text-white hover:bg-white/10'
          }`}
        >
          Nettoyage
        </button>
        <div className="ml-auto">
          <button
            onClick={() => onShowImportModal?.()}
            className="px-4 py-1.5 rounded bg-[#FF6B00] text-white hover:bg-[#e56100] transition-colors"
          >
            Import SQL
          </button>
        </div>
      </div>
    </div>
  );
}