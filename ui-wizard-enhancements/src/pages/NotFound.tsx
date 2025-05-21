import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { Home } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <div className="min-h-[70vh] flex items-center justify-center">
          <div className="text-center max-w-lg px-4">
            <h1 className="text-6xl font-serif font-bold text-yoga-charcoal mb-4">404</h1>
            <div className="w-24 h-1 bg-yoga-green mx-auto mb-6"></div>
            <p className="text-2xl text-yoga-slate mb-8">
              Oops! This page has gone into deep meditation and can't be found.
            </p>
            <Link to="/" className="yoga-button inline-flex items-center">
              <Home className="mr-2" size={18} />
              Return to Home
            </Link>
          </div>
        </div>
      </main>
      
      <Footer />
    </>
  );
};

export default NotFound;
