import { Link } from "react-router-dom";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { ArrowDown, ArrowRight, Play } from "lucide-react";

const Index = () => {
  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        {/* Hero Section */}
        <section className="relative bg-white overflow-hidden">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div className="space-y-6 animate-fade-in">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-serif font-bold text-yoga-charcoal leading-tight">
                  NYRA: Natural <span className="text-yoga-green">Yoga</span> Recognition Assistant
                </h1>
                <p className="text-lg text-yoga-slate max-w-lg">
                  Enhance your yoga practice with AI-powered pose recognition and real-time feedback to perfect your form and deepen your practice.
                </p>
                <div className="flex flex-wrap gap-4 pt-2">
                  <Link to="/tracks" className="yoga-button">
                    Let's Start
                  </Link>
                  <Link to="/poses" className="yoga-button-secondary">
                    Explore Poses
                  </Link>
                </div>
              </div>
              
              <div className="relative animate-fade-in" style={{ animationDelay: "0.2s" }}>
                <div className="relative z-10 animate-float">
                  <img 
                    src="/Yoga.png"
                    alt="Yoga pose illustration" 
                    className="mx-auto max-w-full"
                  />
                </div>
                <div className="absolute inset-0 bg-gradient-mint rounded-full blur-3xl opacity-30 -z-10 animate-pulse-gentle"></div>
              </div>
            </div>
            
            <div className="flex justify-center mt-16">
              <button 
                onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                className="flex flex-col items-center text-yoga-slate hover:text-yoga-green transition-colors"
              >
                <span className="mb-2">Scroll Down</span>
                <ArrowDown className="animate-bounce" />
              </button>
            </div>
          </div>
        </section>
        
        {/* Yoga Styles Section */}
        <section id="features" className="bg-gray-50 py-20">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl md:text-4xl font-serif font-bold text-yoga-charcoal mb-4">
                Explore Different Yoga Styles
              </h2>
              <p className="text-yoga-slate text-lg">
                NYRA supports various yoga styles to help you find the perfect practice for your needs and goals.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
              <div className="yoga-card hover:border-yoga-green-light hover:border flex items-start space-x-4 p-6">
                <div className="bg-yoga-mint p-4 rounded-full">
                  <Play className="text-yoga-green" size={24} />
                </div>
                <div>
                  <h3 className="text-xl font-serif font-semibold text-yoga-charcoal mb-2">Ashtanga Yoga</h3>
                  <p className="text-yoga-slate">
                    A rigorous style of yoga that follows a specific sequence of postures linked by breath. This practice builds strength, flexibility and stamina.
                  </p>
                </div>
              </div>
              
              <div className="yoga-card hover:border-yoga-green-light hover:border flex items-start space-x-4 p-6">
                <div className="bg-yoga-mint p-4 rounded-full">
                  <Play className="text-yoga-green" size={24} />
                </div>
                <div>
                  <h3 className="text-xl font-serif font-semibold text-yoga-charcoal mb-2">Hatha Yoga</h3>
                  <p className="text-yoga-slate">
                    A gentle introduction to basic yoga postures. You'll learn foundational poses in a slower-paced environment with detailed guidance.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="text-center">
              <Link to="/tracks" className="yoga-button inline-flex items-center">
                <span>View All Tracks</span>
                <ArrowRight className="ml-2" size={18} />
              </Link>
            </div>
          </div>
        </section>
        
        {/* How It Works Section */}
        <section className="py-20 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl md:text-4xl font-serif font-bold text-yoga-charcoal mb-4">
                How NYRA Works
              </h2>
              <p className="text-yoga-slate text-lg">
                Our AI-powered system provides real-time feedback to help you perfect your yoga practice.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center space-y-4">
                <div className="bg-yoga-mint w-16 h-16 rounded-full flex items-center justify-center mx-auto">
                  <span className="text-yoga-green text-xl font-bold">1</span>
                </div>
                <h3 className="text-xl font-serif font-semibold text-yoga-charcoal">Choose Your Track</h3>
                <p className="text-yoga-slate">
                  Select from various yoga styles and difficulty levels tailored to your experience.
                </p>
              </div>
              
              <div className="text-center space-y-4">
                <div className="bg-yoga-mint w-16 h-16 rounded-full flex items-center justify-center mx-auto">
                  <span className="text-yoga-green text-xl font-bold">2</span>
                </div>
                <h3 className="text-xl font-serif font-semibold text-yoga-charcoal">Practice with AI Guidance</h3>
                <p className="text-yoga-slate">
                  Follow along with our instructor while our AI analyzes your form in real-time.
                </p>
              </div>
              
              <div className="text-center space-y-4">
                <div className="bg-yoga-mint w-16 h-16 rounded-full flex items-center justify-center mx-auto">
                  <span className="text-yoga-green text-xl font-bold">3</span>
                </div>
                <h3 className="text-xl font-serif font-semibold text-yoga-charcoal">Receive Feedback</h3>
                <p className="text-yoga-slate">
                  Get personalized adjustments and track your progress over time with detailed analytics.
                </p>
              </div>
            </div>
          </div>
        </section>
        
        {/* CTA Section */}
        <section className="bg-gradient-yoga py-20">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-white mb-6">
              Ready to Transform Your Yoga Practice?
            </h2>
            <p className="text-white/90 text-lg max-w-2xl mx-auto mb-8">
              Join thousands of yoga enthusiasts who have improved their practice with NYRA's intelligent guidance.
            </p>
            <Link to="/tracks" className="inline-flex items-center justify-center rounded-full px-8 py-3 text-base font-medium
                     bg-white text-yoga-green hover:bg-gray-50 shadow-lg transition-all duration-200">
              Get Started Now
            </Link>
          </div>
        </section>
      </main>
      
      <Footer />
    </>
  );
};

export default Index;
