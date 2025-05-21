import React, { createContext, useState, useContext, useEffect } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  User as FirebaseUser
} from "firebase/auth";
import { auth } from "@/lib/firebase";
import { createUserProfile } from "@/lib/firestore-service";

// Define user type
interface User {
  id: string;
  email: string | null;
  name: string | null;
}

// Define auth context type
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Listen for authentication state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in, convert Firebase user to our User type
        setUser({
          id: firebaseUser.uid,
          email: firebaseUser.email,
          name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || "Yoga User"
        });
        
        // Create or update user profile in Firestore
        await createUserProfile(firebaseUser);
      } else {
        // User is signed out
        setUser(null);
      }
      setIsLoading(false);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  // Login function - sign in with Firebase
  const login = async (email: string, password: string) => {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      // Create or update user profile in Firestore
      if (result.user) {
        await createUserProfile(result.user);
      }
    } catch (error: any) {
      console.error("Login error:", error);
      throw new Error(error.message || "Failed to login");
    }
  };

  // Signup function - create new account with Firebase
  const signup = async (name: string, email: string, password: string) => {
    try {
      // Create user in Firebase
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update profile with user's name
      if (result.user) {
        await updateProfile(result.user, {
          displayName: name
        });
        
        // Create user profile in Firestore
        await createUserProfile(result.user);
        
        // Force refresh of the user object to include the updated displayName
        setUser({
          id: result.user.uid,
          email: result.user.email,
          name: name
        });
      }
    } catch (error: any) {
      console.error("Signup error:", error);
      throw new Error(error.message || "Failed to create account");
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await signOut(auth);
    } catch (error: any) {
      console.error("Logout error:", error);
      throw new Error(error.message || "Failed to logout");
    }
  };

  // Value object that will be passed to consumers
  const value = {
    user,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};