
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { Link } from "react-router-dom";

const About = () => {
  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <section className="bg-gradient-yoga py-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-serif font-bold text-white mb-3">
              About NYRA
            </h1>
            <p className="text-white/90 text-xl max-w-2xl mx-auto">
              Your AI-powered yoga companion for a better practice
            </p>
          </div>
        </section>
        
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
            <div className="prose prose-lg mx-auto">
              <p className="lead text-yoga-charcoal">
                Natural Yoga Recognition Assistant (NYRA) is a cutting-edge platform that uses artificial intelligence to help yoga practitioners of all levels improve their form and deepen their practice.
              </p>
              
              <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mt-8 mb-4">Our Mission</h2>
              <p>
                Our mission is to make quality yoga instruction accessible to everyone, everywhere. By combining traditional yoga wisdom with modern technology, we provide personalized guidance that adapts to your unique body and practice level.
              </p>
              
              <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mt-8 mb-4">How NYRA Works</h2>
              <p>
                NYRA uses computer vision technology to analyze your yoga poses in real-time. Our AI engine compares your form with that of expert practitioners, identifying areas for improvement and providing immediate feedback to help you adjust your posture.
              </p>
              
              <div className="my-8 p-6 bg-yoga-mint rounded-xl">
                <h3 className="text-xl font-semibold text-yoga-green mb-3">Key Features</h3>
                <ul className="space-y-2">
                  <li>Real-time pose analysis and feedback</li>
                  <li>Personalized practice recommendations</li>
                  <li>Progress tracking and analytics</li>
                  <li>Comprehensive library of yoga poses and sequences</li>
                  <li>Specialized tracks for different health goals</li>
                </ul>
              </div>
              
              <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mt-8 mb-4">Our Team</h2>
              <p>
                NYRA was created by a dedicated team of yoga instructors, AI specialists, and health professionals united by a passion for wellness and technology. Our diverse backgrounds ensure that NYRA delivers both technical excellence and authentic yoga guidance.
              </p>
              
              <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mt-8 mb-4">Join Our Community</h2>
              <p>
                Whether you're a beginner or an experienced yogi, NYRA adapts to your level and helps you achieve your personal goals. Join our growing community of practitioners who are using technology to enhance their yoga journey.
              </p>
              
              <div className="mt-8 text-center">
                <Link to="/tracks" className="yoga-button">
                  Explore NYRA
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </>
  );
};

export default About;
