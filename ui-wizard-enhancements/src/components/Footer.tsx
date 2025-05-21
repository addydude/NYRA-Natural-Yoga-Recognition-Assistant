
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-100 py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <h3 className="text-xl font-serif font-bold text-yoga-green">NYRA</h3>
            <p className="text-yoga-slate max-w-xs">
              Natural Yoga Recognition Assistant - Improving your yoga practice with AI-powered pose recognition and personalized feedback.
            </p>
          </div>
          
          <div>
            <h4 className="font-medium text-yoga-charcoal mb-4">Yoga Styles</h4>
            <ul className="space-y-2">
              <li><Link to="/tracks?style=hatha" className="text-yoga-slate hover:text-yoga-green transition-colors">Hatha Yoga</Link></li>
              <li><Link to="/tracks?style=ashtanga" className="text-yoga-slate hover:text-yoga-green transition-colors">Ashtanga Yoga</Link></li>
              <li><Link to="/tracks?style=vinyasa" className="text-yoga-slate hover:text-yoga-green transition-colors">Vinyasa Flow</Link></li>
              <li><Link to="/tracks?style=yin" className="text-yoga-slate hover:text-yoga-green transition-colors">Yin Yoga</Link></li>
              <li><Link to="/tracks?style=restorative" className="text-yoga-slate hover:text-yoga-green transition-colors">Restorative Yoga</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-yoga-charcoal mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li><Link to="/" className="text-yoga-slate hover:text-yoga-green transition-colors">Home</Link></li>
              <li><Link to="/tracks" className="text-yoga-slate hover:text-yoga-green transition-colors">Tracks</Link></li>
              <li><Link to="/poses" className="text-yoga-slate hover:text-yoga-green transition-colors">Yoga Poses</Link></li>
              <li><Link to="/about" className="text-yoga-slate hover:text-yoga-green transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="text-yoga-slate hover:text-yoga-green transition-colors">Contact</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-yoga-charcoal mb-4">Connect</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-yoga-slate hover:text-yoga-green transition-colors">Twitter</a></li>
              <li><a href="#" className="text-yoga-slate hover:text-yoga-green transition-colors">Instagram</a></li>
              <li><a href="#" className="text-yoga-slate hover:text-yoga-green transition-colors">YouTube</a></li>
              <li><a href="#" className="text-yoga-slate hover:text-yoga-green transition-colors">Facebook</a></li>
            </ul>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-gray-200 flex flex-col md:flex-row justify-between items-center">
          <p className="text-yoga-slate text-sm">&copy; {new Date().getFullYear()} NYRA. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link to="/privacy" className="text-yoga-slate text-sm hover:text-yoga-green transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="text-yoga-slate text-sm hover:text-yoga-green transition-colors">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
