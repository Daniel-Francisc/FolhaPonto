import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { NavLink } from 'react-router-dom'
import Home from '../paginas/Principal'
import Second from '../paginas/Secundaria'
import './AppRoutes.css'

function AppRoutes() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/second" element={<Second />} />
          </Routes>
        </main>

        <nav className="bottom-nav">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? 'nav-link active' : 'nav-link'
            }
          >
            <span className="nav-icon">🏠</span>
            <span className="nav-label">Home</span>
          </NavLink>

          <NavLink
            to="/second"
            className={({ isActive }) =>
              isActive ? 'nav-link active' : 'nav-link'
            }
          >
            <span className="nav-icon">📄</span>
            <span className="nav-label">Segunda</span>
          </NavLink>
        </nav>
      </div>
    </BrowserRouter>
  )
}

export default AppRoutes