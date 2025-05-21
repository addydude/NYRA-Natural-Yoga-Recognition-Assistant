import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./components/auth/AuthContext";
import PageTransition from "./components/PageTransition";
import Index from "./pages/Index";
import Tracks from "./pages/Tracks";
import TrackDetail from "./pages/TrackDetail";
import Poses from "./pages/Poses";
import PoseDetail from "./pages/PoseDetail";
import Practice from "./pages/Practice";
import Analytics from "./pages/Analytics";
import About from "./pages/About";
import Contact from "./pages/Contact";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Wrapper component that applies the PageTransition to each route
const PageWrapper = ({ component: Component, ...rest }: { component: React.ComponentType<any> }) => {
  return (
    <PageTransition>
      <Component {...rest} />
    </PageTransition>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<PageWrapper component={Index} />} />
            <Route path="/tracks" element={<PageWrapper component={Tracks} />} />
            <Route path="/track/:trackId" element={<PageWrapper component={TrackDetail} />} />
            <Route path="/poses" element={<PageWrapper component={Poses} />} />
            <Route path="/pose/:poseId" element={<PageWrapper component={PoseDetail} />} />
            <Route path="/practice/:poseId" element={<PageWrapper component={Practice} />} />
            <Route path="/analytics" element={<PageWrapper component={Analytics} />} />
            <Route path="/about" element={<PageWrapper component={About} />} />
            <Route path="/contact" element={<PageWrapper component={Contact} />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<PageWrapper component={NotFound} />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
