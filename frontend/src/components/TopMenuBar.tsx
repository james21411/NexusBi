import { useState, useRef, useEffect } from 'react';
import { ChevronDown, User } from 'lucide-react';
import { AuthPanel } from './AuthPanel';

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
      { label: 'Paramètres', shortcut: 'Ctrl+,' },
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
    <header className="bg-blue-900 flex flex-col" style={{backgroundColor: '#1e3a8a'}}>
      {/* Ligne du haut - Menus principaux */}
      <nav className="text-white h-12 flex items-center px-5 relative z-50" style={{color: 'white', minHeight: '48px'}} ref={menuRef}>
        {/* Logo et nom avec icône utilisateur */}
        <figure className="flex items-center gap-3 mr-6">
          <div className="w-8 h-8 bg-[var(--primary-foreground)] rounded flex items-center justify-center">
            <span className="text-[var(--primary)] font-medium text-lg">N</span>
          </div>
          <span className="text-white text-lg font-medium">NexusBi</span>
          <User className="text-white" size={20} />
        </figure>

        {/* Menus */}
        <menu className="flex items-center gap-2">
          {menuItems.map((menu) => (
            <div key={menu.label} className="relative">
              <button
                className={`px-5 py-2 rounded-lg hover:bg-blue-800 transition-colors flex items-center gap-2 text-base whitespace-nowrap ${
                  activeMenu === menu.label ? 'bg-blue-700 text-white' : 'text-white'
                }`}
                style={{minHeight: '40px', minWidth: '140px'}}
                onClick={() => setActiveMenu(activeMenu === menu.label ? null : menu.label)}
              >
                {menu.label}
                <ChevronDown size={12} />
              </button>

              {/* Dropdown */}
              {activeMenu === menu.label && (
                <div className="absolute top-full left-0 mt-1 bg-blue-950 text-white shadow-xl border border-blue-800 min-w-[360px] py-2 z-50" style={{backgroundColor: '#172554', color: 'white', borderColor: '#1e3a8a'}}>
                  {menu.items.map((item, index) => (
                    item.separator ? (
                      <div key={index} className="h-px bg-blue-600 my-1" />
                    ) : (
                      <button
                        key={index}
                        className="w-full px-5 py-3 hover:bg-blue-900 flex items-center justify-between transition-colors text-left text-base whitespace-nowrap"
                        style={{color: 'white', minHeight: '44px'}}
                        onClick={() => {
                          setActiveMenu(null);
                          if (item.label === 'Paramètres') {
                            onViewChange?.('settings');
                          }
                        }}
                      >
                        <span>{item.label}</span>
                        {item.shortcut && (
                          <span className="text-blue-300 ml-6 text-xs">{item.shortcut}</span>
                        )}
                      </button>
                    )
                  ))}
                </div>
              )}
            </div>
          ))}
        </menu>

        {/* Zone droite - Authentification */}
        <aside className="ml-auto flex items-center gap-4">
          <AuthPanel />
        </aside>
      </nav>

      {/* Ligne du bas - Navigation des vues */}
      <nav className="bg-blue-950 px-5 py-3 flex items-center gap-4" style={{backgroundColor: '#172554', minHeight: '56px'}}>
        <button
          onClick={() => onViewChange?.('dashboard')}
          className={`px-5 py-3 rounded-lg transition-colors text-base ${
            currentView === 'dashboard'
              ? 'bg-blue-800 text-white'
              : 'text-white hover:bg-blue-700'
          }`}
          style={{minHeight: '44px'}}
        >
          Tableau de Bord
        </button>
        <button
          onClick={() => onViewChange?.('sources')}
          className={`px-5 py-3 rounded-lg transition-colors text-base ${
            currentView === 'sources'
              ? 'bg-blue-800 text-white'
              : 'text-white hover:bg-blue-700'
          }`}
          style={{minHeight: '44px'}}
        >
          Sources de Données
        </button>
        <button
          onClick={() => onViewChange?.('analytics')}
          className={`px-5 py-3 rounded-lg transition-colors text-base ${
            currentView === 'analytics'
              ? 'bg-blue-800 text-white'
              : 'text-white hover:bg-blue-700'
          }`}
          style={{minHeight: '44px'}}
        >
          Analyses
        </button>
        <button
          onClick={() => onViewChange?.('reports')}
          className={`px-5 py-3 rounded-lg transition-colors text-base ${
            currentView === 'reports'
              ? 'bg-blue-800 text-white'
              : 'text-white hover:bg-blue-700'
          }`}
          style={{minHeight: '44px'}}
        >
          Rapports
        </button>
        <button
          onClick={() => onViewChange?.('cleaning')}
          className={`px-5 py-3 rounded-lg transition-colors text-base ${
            currentView === 'cleaning'
              ? 'bg-blue-800 text-white'
              : 'text-white hover:bg-blue-700'
          }`}
          style={{minHeight: '44px'}}
        >
          Nettoyage
        </button>
        <button
          onClick={() => onViewChange?.('settings')}
          className={`px-5 py-3 rounded-lg transition-colors text-base ${
            currentView === 'settings'
              ? 'bg-blue-800 text-white'
              : 'text-white hover:bg-blue-700'
          }`}
          style={{minHeight: '44px'}}
        >
          Paramètres
        </button>
        <div className="ml-auto">
          <button
            onClick={() => onShowImportModal?.()}
            className="px-6 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors text-base font-medium"
            style={{minHeight: '44px'}}
          >
            Import SQL
          </button>
        </div>
      </nav>
    </header>
  );
}