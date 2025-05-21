import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import AuthModals from "./auth/AuthModals";
import { useAuth } from "./auth/AuthContext";
import { User, LogOut } from "lucide-react";

const Navigation = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const [authModal, setAuthModal] = useState<{
    isOpen: boolean;
    type: 'signin' | 'signup';
  }>({
    isOpen: false,
    type: 'signin',
  });
  
  const openAuthModal = (type: 'signin' | 'signup') => {
    setAuthModal({
      isOpen: true,
      type,
    });
  };
  
  const closeAuthModal = () => {
    setAuthModal({
      ...authModal,
      isOpen: false,
    });
  };
  
  const switchAuthType = () => {
    setAuthModal({
      ...authModal,
      type: authModal.type === 'signin' ? 'signup' : 'signin',
    });
  };
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="w-full border-b border-gray-100 bg-white/95 backdrop-blur-sm fixed top-0 left-0 right-0 z-50 shadow-nav">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-yoga-green font-serif text-2xl font-bold">NYRA</span>
            </Link>
            <nav className="ml-10 hidden space-x-4 md:flex">
              <Link to="/" className={`nav-link ${isActive('/') ? 'nav-link-active' : ''}`}>
                Home
              </Link>
              <Link to="/tracks" className={`nav-link ${isActive('/tracks') ? 'nav-link-active' : ''}`}>
                Tracks
              </Link>
              <Link to="/poses" className={`nav-link ${isActive('/poses') ? 'nav-link-active' : ''}`}>
                Poses
              </Link>
              <Link to="/about" className={`nav-link ${isActive('/about') ? 'nav-link-active' : ''}`}>
                About
              </Link>
              <Link to="/contact" className={`nav-link ${isActive('/contact') ? 'nav-link-active' : ''}`}>
                Contact
              </Link>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <div className="hidden md:flex items-center space-x-2 text-yoga-slate">
                  <User size={18} className="text-yoga-green" />
                  <span>Welcome, {user?.name}</span>
                </div>
                <Button 
                  variant="outline" 
                  className="hidden md:inline-flex"
                  onClick={logout}
                >
                  <LogOut size={16} className="mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button 
                  variant="outline" 
                  className="hidden md:inline-flex"
                  onClick={() => openAuthModal('signin')}
                >
                  Sign In
                </Button>
                <Button 
                  className="yoga-button hidden md:inline-flex"
                  onClick={() => openAuthModal('signup')}
                >
                  Sign Up
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Auth modals */}
      <AuthModals
        isOpen={authModal.isOpen}
        type={authModal.type}
        onClose={closeAuthModal}
        onSwitch={switchAuthType}
      />
    </header>
  );
};

export default Navigation;
