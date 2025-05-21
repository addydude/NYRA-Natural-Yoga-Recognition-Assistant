import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAuth } from "./AuthContext";

interface AuthModalsProps {
  isOpen: boolean;
  type: 'signin' | 'signup';
  onClose: () => void;
  onSwitch: () => void;
}

const AuthModals = ({ isOpen, type, onClose, onSwitch }: AuthModalsProps) => {
  const { login, signup } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing again
    if (error) setError(null);
  };
  
  // Format Firebase error messages to be more user-friendly
  const formatErrorMessage = (message: string): string => {
    if (message.includes('auth/invalid-credential') || message.includes('auth/invalid-email')) {
      return "Invalid email or password. Please try again.";
    } else if (message.includes('auth/email-already-in-use')) {
      return "This email is already registered. Please sign in instead.";
    } else if (message.includes('auth/weak-password')) {
      return "Password is too weak. Please use at least 6 characters.";
    } else if (message.includes('auth/too-many-requests')) {
      return "Too many failed login attempts. Please try again later.";
    } else if (message.includes('auth/user-not-found')) {
      return "No account found with this email. Please sign up first.";
    } else {
      return message;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      setIsLoading(true);
      
      // Validation checks
      if (type === 'signup') {
        if (formData.password !== formData.confirmPassword) {
          throw new Error("Passwords don't match!");
        }
        
        if (formData.password.length < 6) {
          throw new Error("Password must be at least 6 characters long");
        }
        
        if (!formData.fullName.trim()) {
          throw new Error("Name is required");
        }
      }
      
      // Attempt authentication
      if (type === 'signin') {
        await login(formData.email, formData.password);
      } else {
        await signup(formData.fullName, formData.email, formData.password);
      }
      
      // Reset form after successful auth
      setFormData({
        email: '',
        password: '',
        confirmPassword: '',
        fullName: ''
      });
      
      onClose();
    } catch (err) {
      if (err instanceof Error) {
        setError(formatErrorMessage(err.message));
      } else {
        setError('Authentication failed. Please try again.');
      }
      console.error('Authentication error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset form data when modal type changes
  const handleSwitchType = () => {
    setError(null);
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
      fullName: ''
    });
    onSwitch();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl font-serif font-bold text-yoga-charcoal">
            {type === 'signin' ? 'Sign In to Your Account' : 'Create an Account'}
          </DialogTitle>
          <DialogDescription>
            {type === 'signin' 
              ? 'Welcome back! Please enter your details.'
              : 'Join NYRA to track your yoga progress and get personalized recommendations.'}
          </DialogDescription>
        </DialogHeader>
        
        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {type === 'signup' && (
            <div className="space-y-2">
              <label htmlFor="fullName" className="text-sm font-medium text-yoga-slate">
                Full Name
              </label>
              <Input
                id="fullName"
                name="fullName"
                placeholder="Your name"
                value={formData.fullName}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>
          )}
          
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-yoga-slate">
              Email
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium text-yoga-slate">
              Password
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
            {type === 'signup' && (
              <p className="text-xs text-yoga-slate mt-1">
                Must be at least 6 characters long
              </p>
            )}
          </div>
          
          {type === 'signup' && (
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium text-yoga-slate">
                Confirm Password
              </label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>
          )}
          
          <Button 
            type="submit" 
            className="w-full yoga-button"
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : (type === 'signin' ? 'Sign In' : 'Sign Up')}
          </Button>
          
          <div className="text-center text-sm text-yoga-slate">
            {type === 'signin' ? "Don't have an account? " : "Already have an account? "}
            <button 
              type="button"
              onClick={handleSwitchType}
              className="font-medium text-yoga-green hover:underline"
              disabled={isLoading}
            >
              {type === 'signin' ? 'Sign up now' : 'Sign in instead'}
            </button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AuthModals;