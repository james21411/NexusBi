import React from 'react';
import nexusBiIcon from './ChatBox/NexusBi.png';

const LeftNav = ({ collapsed, width, currentPage, onPageChange, onToggle, onResize }) => {
  const handleNavItemClick = (page) => {
    onPageChange(page);
  };

  const handleMouseDown = (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = width;

    const handleMouseMove = (e) => {
      const dx = e.clientX - startX;
      let newWidth = Math.round(startWidth + dx);
      if (newWidth < 180) newWidth = 180;
      if (newWidth > 480) newWidth = 480;
      onResize(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.userSelect = '';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    document.body.style.userSelect = 'none';
  };

  return (
    <>
      <nav className={`left-nav ${collapsed ? 'collapsed' : ''}`} style={{ width: `${width}px` }}>
        <div id="leftResizer" className="left-resizer" onMouseDown={handleMouseDown}></div>
        <div className="nav-header d-flex justify-content-between align-items-center p-3 border-bottom">
          <div className="logo d-flex align-items-center gap-2">
            <img src={nexusBiIcon} alt="NexusBI" style={{ width: '40px', height: '40px', borderRadius: '6px' }} />
          </div>
          <button id="toggleLeftNavDesktop" className="btn btn-sm btn-outline-light" title="Réduire la navigation" onClick={onToggle}>
            <i className="fas fa-bars"></i>
          </button>
        </div>
        <div className={`nav-item ${currentPage === 'home' ? 'active' : ''}`} onClick={() => handleNavItemClick('home')}>
          <i className="fas fa-home me-2"></i>
          {!collapsed && <span className="nav-label">Accueil</span>}
        </div>
        <div className="nav-section">
          {!collapsed && <span>Contenu</span>}
        </div>
        <div className={`nav-item ${currentPage === 'workspaces' ? 'active' : ''}`} onClick={() => handleNavItemClick('workspaces')}>
          <i className="fas fa-th-large me-2"></i>
          {!collapsed && <span className="nav-label">Espaces de travail</span>}
        </div>
        <div className={`nav-item ${currentPage === 'reports' ? 'active' : ''}`} onClick={() => handleNavItemClick('reports')}>
          <i className="fas fa-file-alt me-2"></i>
          {!collapsed && <span className="nav-label">Rapports</span>}
        </div>
        <div className={`nav-item ${currentPage === 'dashboards' ? 'active' : ''}`} onClick={() => handleNavItemClick('dashboards')}>
          <i className="fas fa-tachometer-alt me-2"></i>
          {!collapsed && <span className="nav-label">Tableaux de bord</span>}
        </div>
        <div className="nav-section">
          {!collapsed && <span>Données</span>}
        </div>
        <div className={`nav-item ${currentPage === 'import' ? 'active' : ''}`} onClick={() => handleNavItemClick('import')}>
          <i className="fas fa-upload me-2"></i>
          {!collapsed && <span className="nav-label">Importer des données</span>}
        </div>
        <div className={`nav-item ${currentPage === 'sources' ? 'active' : ''}`} onClick={() => handleNavItemClick('sources')}>
          <i className="fas fa-database me-2"></i>
          {!collapsed && <span className="nav-label">Sources de données</span>}
        </div>
        <div className={`nav-item ${currentPage === 'preparation' ? 'active' : ''}`} onClick={() => handleNavItemClick('preparation')}>
          <i className="fas fa-edit me-2"></i>
          {!collapsed && <span className="nav-label">Préparation des données</span>}
        </div>
        <div className={`nav-item ${currentPage === 'modeling' ? 'active' : ''}`} onClick={() => handleNavItemClick('modeling')}>
          <i className="fas fa-sitemap me-2"></i>
          {!collapsed && <span className="nav-label">Modélisation</span>}
        </div>
        <div className="nav-section">
          {!collapsed && <span>Autres</span>}
        </div>
        <div className={`nav-item ${currentPage === 'apps' ? 'active' : ''}`} onClick={() => handleNavItemClick('apps')}>
          <i className="fas fa-layer-group me-2"></i>
          {!collapsed && <span className="nav-label">Applications</span>}
        </div>
        <div className={`nav-item ${currentPage === 'learn' ? 'active' : ''}`} onClick={() => handleNavItemClick('learn')}>
          <i className="fas fa-book me-2"></i>
          {!collapsed && <span className="nav-label">Apprendre</span>}
        </div>
        <div className={`nav-item ${currentPage === 'aide' ? 'active' : ''}`} onClick={() => handleNavItemClick('aide')}>
          <i className="fas fa-question-circle me-2"></i>
          {!collapsed && <span className="nav-label">Aide</span>}
        </div>
      </nav>

      {/* Toggle pour mobile */}
      <button className="btn btn-primary position-fixed top-0 start-0 m-3 d-lg-none" id="toggleLeftNav">
        <i className="fas fa-bars"></i>
      </button>
    </>
  );
};

export default LeftNav;