import React, { useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { 
  LayoutDashboard, 
  ShoppingBag, 
  ShoppingBasket, 
  LogOut, 
  Menu, 
  X, 
  User, 
  Sparkles 
} from 'lucide-react';

const adminLinks = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Pedidos', path: '/orders', icon: ShoppingBag },
  { name: 'Productos', path: '/products', icon: ShoppingBasket },
];

const AdminLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-background/50 flex flex-col md:flex-row relative">
      {/* Mobile Top Navigation */}
      <div className="md:hidden flex items-center justify-between p-4 bg-card border-b border-border z-30 sticky top-0">
        <div className="flex items-center gap-2 font-bold text-foreground">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground">
            <Sparkles className="h-4.5 w-4.5" />
          </div>
          <span style={{ fontFamily: 'Playfair Display, serif' }}>Nutra Blue</span>
        </div>
        <button 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-1 rounded-md text-muted-foreground hover:text-foreground focus:outline-none"
        >
          {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-card border-r border-border p-6 flex flex-col justify-between transition-transform duration-200 ease-in-out
        md:translate-x-0 md:sticky md:h-screen md:top-0
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="space-y-8">
          <div className="hidden md:flex items-center gap-2.5 font-bold text-2xl text-foreground">
            <div className="w-9 h-9 bg-primary rounded-xl flex items-center justify-center text-primary-foreground shadow-md shadow-primary/20">
              <Sparkles className="h-5 w-5" />
            </div>
            <span style={{ fontFamily: 'Playfair Display, serif' }}>Nutra Blue</span>
          </div>

          <div className="p-3 bg-muted/40 rounded-xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <User className="h-5 w-5" />
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold truncate">{currentUser?.email || 'Administrador'}</p>
              <span className="text-xs text-muted-foreground">Admin</span>
            </div>
          </div>

          <nav className="space-y-1">
            {adminLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150
                    ${isActive 
                      ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/15' 
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'}
                  `}
                >
                  <Icon className="h-4.5 w-4.5" />
                  {link.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="pt-4 border-t border-border">
          <Button 
            variant="ghost" 
            className="w-full justify-start text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-xl h-10 px-3"
            onClick={handleLogout}
          >
            <LogOut className="h-4.5 w-4.5 mr-3" />
            Cerrar Sesión
          </Button>
        </div>
      </aside>

      {/* Overlay background for mobile menu */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/40 z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        ></div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full overflow-x-hidden">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
