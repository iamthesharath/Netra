import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import NewCase from './pages/NewCase'
import CaseDetail from './pages/CaseDetail'

function Nav() {
  const loc = useLocation()
  return (
    <nav className="bg-gray-900 border-b border-gray-800 px-6 py-0 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-8">
        <Link to="/" className="flex items-center gap-2 py-4">
          <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">N</div>
          <span className="text-white font-bold text-lg tracking-tight">Netra</span>
        </Link>
        <div className="flex items-center gap-1">
          <Link
            to="/"
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${loc.pathname === '/' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            Cases
          </Link>
          <Link
            to="/new"
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${loc.pathname === '/new' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white'}`}
          >
            New Case
          </Link>
        </div>
      </div>
      <span className="text-gray-600 text-xs">CCTV Missing Person Search</span>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-gray-100 font-sans">
        <Nav />
        <main className="max-w-5xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/new" element={<NewCase />} />
            <Route path="/cases/:id" element={<CaseDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
