import { useParams, Link, Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import YogaPoseCard from "@/components/YogaPoseCard";
import { fetchYogaPoses } from "@/lib/api";
import { ArrowLeft, LockIcon } from "lucide-react";
import { useAuthProtected } from "@/lib/auth-utils";

// Define track data with associated poses
const trackData = {
  beginners: {
    title: "Beginners Track",
    description: "Perfect for those who are new to yoga. Build strength, flexibility and confidence with these fundamental poses.",
    poses: ["tadasana", "vrksana", "balasana"],
    style: "hatha",
    duration: "4 weeks",
    level: "Beginner"
  },
  power: {
    title: "Power Yoga Track",
    description: "An energetic practice that builds strength, flexibility and endurance while providing a full-body workout.",
    poses: ["virabhadrasana", "adhomukha", "trikonasana"],
    style: "vinyasa",
    duration: "6 weeks",
    level: "Intermediate"
  },
  immunity: {
    title: "Immunity Booster Track",
    description: "Strengthen your immune system with these specific poses designed to improve circulation and reduce stress.",
    poses: ["adhomukha", "balasana", "tadasana"],
    style: "hatha",
    duration: "3 weeks",
    level: "All levels"
  },
  pregnancy: {
    title: "Yoga in Pregnancy Track",
    description: "Safe and gentle poses designed specifically for expectant mothers to relieve discomfort and prepare for childbirth.",
    poses: ["balasana", "tadasana", "trikonasana"],
    style: "restorative",
    duration: "Trimester-based",
    level: "All levels"
  },
  cardiovascular: {
    title: "Cardiovascular Yoga Track",
    description: "Improve heart health and circulation with this dynamic sequence of poses that keeps your heart rate elevated.",
    poses: ["virabhadrasana", "trikonasana", "adhomukha"],
    style: "ashtanga",
    duration: "8 weeks",
    level: "Intermediate to Advanced"
  },
  migraine: {
    title: "Yoga for Migraine Track",
    description: "Find relief from headaches and migraines with these gentle poses that focus on relaxation and stress reduction.",
    poses: ["balasana", "tadasana", "vrksana"],
    style: "yin",
    duration: "4 weeks",
    level: "All levels"
  },
  asthma: {
    title: "Yoga for Asthma Track",
    description: "Improve breathing capacity and lung function with poses focused on opening the chest and encouraging deeper breathing.",
    poses: ["tadasana", "adhomukha", "virabhadrasana"],
    style: "hatha",
    duration: "6 weeks",
    level: "All levels"
  }
};

const TrackDetail = () => {
  const { trackId } = useParams<{ trackId: string }>();
  const { handleProtectedAction, isAuthenticated } = useAuthProtected();
  
  // Get track data
  const track = trackId ? trackData[trackId as keyof typeof trackData] : undefined;
  
  // Fetch all poses
  const { data: allPoses, isLoading: posesLoading } = useQuery({
    queryKey: ['poses'],
    queryFn: fetchYogaPoses
  });
  
  // If invalid track ID, redirect to tracks page
  if (!track) {
    return <Navigate to="/tracks" />;
  }
  
  // Filter poses for this track
  const trackPoses = allPoses?.filter(pose => 
    track.poses.includes(pose.id)
  ) || [];

  // Function to handle starting a sequence practice
  const handleStartSequence = () => {
    // In a real app, this would navigate to a sequence page or start the sequence
    window.location.href = `/index?pose=${track.poses[0]}&track=${trackId}`;
  };
  
  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <section className="bg-gradient-yoga py-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col items-center text-center">
              <Link to="/tracks" className="self-start flex items-center text-white/80 hover:text-white mb-6">
                <ArrowLeft className="mr-2" size={18} />
                Back to Tracks
              </Link>
              
              <h1 className="text-3xl md:text-4xl font-serif font-bold text-white mb-4">
                {track.title}
              </h1>
              
              <div className="flex flex-wrap gap-3 justify-center mb-4">
                <div className="px-3 py-1 bg-white/20 text-white rounded-full text-sm">
                  {track.style.charAt(0).toUpperCase() + track.style.slice(1)} Style
                </div>
                <div className="px-3 py-1 bg-white/20 text-white rounded-full text-sm">
                  {track.duration}
                </div>
                <div className="px-3 py-1 bg-white/20 text-white rounded-full text-sm">
                  {track.level}
                </div>
              </div>
              
              <p className="text-white/90 max-w-2xl">
                {track.description}
              </p>
            </div>
          </div>
        </section>
        
        <section className="py-12 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-8 text-center">
              Poses in This Track
            </h2>
            
            {posesLoading ? (
              <div className="text-center py-12">
                <div className="spinner"></div>
                <p className="mt-4 text-yoga-slate">Loading poses...</p>
              </div>
            ) : trackPoses.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {trackPoses.map(pose => (
                  <YogaPoseCard 
                    key={pose.id}
                    id={pose.id}
                    name={pose.name}
                    englishName={pose.englishName}
                    imageSrc={pose.imageSrc}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                <p className="text-yoga-slate">No poses found for this track.</p>
              </div>
            )}
          </div>
        </section>
        
        <section className="py-12 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
            <div className="yoga-card p-8">
              <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-4">
                How to Follow This Track
              </h2>
              <div className="space-y-4">
                <p className="text-yoga-slate">
                  This track is designed to be followed over {track.duration}. Start by practicing each pose individually to familiarize yourself with the proper form and technique.
                </p>
                <p className="text-yoga-slate">
                  Once comfortable, combine the poses into a sequence, holding each for 5-10 breaths. Practice 3-4 times per week for best results.
                </p>
                <p className="text-yoga-slate">
                  Click on any pose above to see detailed instructions and try it with NYRA's AI guidance.
                </p>
                <div className="pt-4">
                  <button 
                    onClick={handleProtectedAction(handleStartSequence)} 
                    className="yoga-button flex items-center gap-2 mx-auto"
                  >
                    {isAuthenticated ? (
                      "Start Full Sequence Practice"
                    ) : (
                      <>
                        <LockIcon size={16} />
                        <span>Sign In to Start Practice</span>
                      </>
                    )}
                  </button>
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

export default TrackDetail;