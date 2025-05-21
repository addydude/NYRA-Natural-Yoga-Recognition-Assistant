import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { Play, Info, BarChart3, Award, LockIcon } from "lucide-react";
import { fetchYogaPose, getVideoStreamUrl } from "@/lib/api";
import { breathingPatterns } from "@/types/api";
import { useState, useEffect, useRef } from "react";
import { useAuthProtected } from "@/lib/auth-utils";

const PoseDetail = () => {
  const { poseId = "vrksana" } = useParams<{ poseId: string }>();
  const navigate = useNavigate();
  const [breathing, setBreathing] = useState<'inhale' | 'exhale'>('inhale');
  const { handleProtectedAction, isAuthenticated } = useAuthProtected();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  
  // Fetch pose data from API
  const { data: pose, isLoading, error } = useQuery({
    queryKey: ['pose', poseId],
    queryFn: () => fetchYogaPose(poseId),
    // Fallback to hardcoded data if API fails
    onError: (err) => {
      console.error("Error fetching pose data:", err);
    }
  });

  // Set up breathing cycle with pose-specific timing
  useEffect(() => {
    const pattern = breathingPatterns[poseId as keyof typeof breathingPatterns] || 
                    breathingPatterns.vrksana;
    
    const inhaleDuration = pattern.totalCycle * pattern.inhaleRatio * 1000;
    const exhaleDuration = pattern.totalCycle * (1 - pattern.inhaleRatio) * 1000;
    
    // Start with inhale
    setBreathing('inhale');
    
    // Setup alternating inhale/exhale cycle
    const inhaleTimeout = setTimeout(() => {
      setBreathing('exhale');
      
      const interval = setInterval(() => {
        setBreathing(prev => prev === 'inhale' ? 'exhale' : 'inhale');
      }, inhaleDuration + exhaleDuration);
      
      return () => clearInterval(interval);
    }, inhaleDuration);
    
    return () => clearTimeout(inhaleTimeout);
  }, [poseId]);

  // Fallback data if API fetch fails
  const fallbackPose = {
    id: poseId,
    name: poseId.charAt(0).toUpperCase() + poseId.slice(1),
    sanskritName: "Asana",
    englishName: "Yoga Pose",
    description: "A yoga pose that helps improve flexibility, strength, and balance.",
    benefits: [
      "Improves overall flexibility",
      "Strengthens muscles",
      "Enhances balance",
      "Reduces stress",
      "Promotes mindfulness"
    ],
    instructions: [
      "Begin in a comfortable position",
      "Follow the instructor's guidance",
      "Move with your breath",
      "Hold the pose for the recommended duration",
      "Release gently and mindfully"
    ],
    cautions: [
      "Listen to your body",
      "Avoid positions that cause pain",
      "Consult with a healthcare provider if you have concerns"
    ],
    imageSrc: "/lovable-uploads/c126367f-f26e-435e-8f48-62728675defa.png",
    gifName: poseId === "vrksana" ? "gif3.gif" : `${poseId}.jpg`
  };
  
  // Use API data if available, otherwise fallback
  const poseData = pose || fallbackPose;
  const videoUrl = getVideoStreamUrl(poseId);
  
  // Function to handle starting the practice
  const handleStartPractice = () => {
    // Navigate to the React practice page instead of the Flask endpoint
    navigate(`/practice/${poseId}`);
  };
  
  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <section className="bg-gradient-yoga py-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-serif font-bold text-white mb-3">
              {poseData.name} Asana
            </h1>
            <div className="flex justify-center items-center gap-3 text-white/90">
              <span className="text-xl">{poseData.sanskritName}</span>
              <span className="w-1.5 h-1.5 bg-white/70 rounded-full"></span>
              <span className="text-xl">{poseData.englishName}</span>
            </div>
          </div>
        </section>
        
        <section className="py-12 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              <div>
                <img 
                  src={poseData.imageSrc.startsWith('/') 
                    ? poseData.imageSrc 
                    : `/static/images/${poseData.gifName || `${poseId}.jpg`}`}
                  alt={poseData.name} 
                  className="w-full h-auto object-cover rounded-xl shadow-lg"
                  onError={(e) => {
                    // Enhanced fallback mechanism with multiple fallback options
                    const target = e.target as HTMLImageElement;
                    const currentSrc = target.src;
                    
                    console.log(`Image load failed for: ${currentSrc}`);
                    
                    // Try different fallbacks in sequence
                    if (currentSrc.includes('/lovable-uploads/')) {
                      // First fallback: Try with the gifName
                      if (poseData.gifName) {
                        target.src = `/static/images/${poseData.gifName}`;
                      } else {
                        target.src = `/static/images/${poseId}.jpg`;
                      }
                    } else if (currentSrc.includes(`/${poseData.gifName}`)) {
                      // Second fallback: Try with poseId.jpg
                      target.src = `/static/images/${poseId}.jpg`;
                    } else if (currentSrc.includes(`/${poseId}.jpg`)) {
                      // Third fallback: Try with poseId.png
                      target.src = `/static/images/${poseId}.png`;
                    } else if (!currentSrc.includes('placeholder.jpg')) {
                      // Final fallback: Use generic placeholder
                      target.src = `/static/images/placeholder.jpg`;
                    }
                  }}
                />
                
                <div className="mt-8 flex flex-wrap gap-3">
                  <button 
                    onClick={handleProtectedAction(handleStartPractice)} 
                    className={`yoga-button flex items-center gap-2 ${!isAuthenticated ? 'relative' : ''}`}
                  >
                    {isAuthenticated ? (
                      <>
                        <Play size={18} />
                        <span>Start Practice</span>
                      </>
                    ) : (
                      <>
                        <LockIcon size={18} />
                        <span>Sign In to Practice</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
              
              <div className="space-y-8">
                <div>
                  <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-3 flex items-center">
                    <Info className="mr-2 text-yoga-green" size={24} />
                    About this Pose
                  </h2>
                  <p className="text-yoga-slate">{poseData.description}</p>
                </div>
                
                <div>
                  <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-3 flex items-center">
                    <Award className="mr-2 text-yoga-green" size={24} />
                    Benefits
                  </h2>
                  <ul className="list-disc list-inside text-yoga-slate space-y-2">
                    {poseData.benefits.map((benefit, index) => (
                      <li key={index}>{benefit}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-3 flex items-center">
                    <BarChart3 className="mr-2 text-yoga-green" size={24} />
                    How to Practice
                  </h2>
                  <ol className="list-decimal list-inside text-yoga-slate space-y-2">
                    {poseData.instructions.map((instruction, index) => (
                      <li key={index}>{instruction}</li>
                    ))}
                  </ol>
                </div>
                
                <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                  <h3 className="text-lg font-medium text-red-800 mb-2">Cautions</h3>
                  <ul className="list-disc list-inside text-red-700 space-y-1">
                    {poseData.cautions.map((caution, index) => (
                      <li key={index}>{caution}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </>
  );
};

export default PoseDetail;
