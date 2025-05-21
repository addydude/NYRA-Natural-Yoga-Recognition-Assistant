
import { useState } from "react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import YogaTrackButton from "@/components/YogaTrackButton";

const Tracks = () => {
  const [selectedStyle, setSelectedStyle] = useState<string>("all");
  
  const styles = [
    { id: "all", name: "All Styles" },
    { id: "hatha", name: "Hatha" },
    { id: "ashtanga", name: "Ashtanga" },
    { id: "vinyasa", name: "Vinyasa" },
    { id: "yin", name: "Yin" },
    { id: "restorative", name: "Restorative" }
  ];
  
  const tracks = [
    { id: "beginners", title: "Beginners Track", style: "hatha" },
    { id: "power", title: "Power Yoga Track", style: "vinyasa" },
    { id: "immunity", title: "Immunity Booster Track", style: "hatha" },
    { id: "pregnancy", title: "Yoga in Pregnancy Track", style: "restorative" },
    { id: "cardiovascular", title: "Cardiovascular Yoga Track", style: "ashtanga" },
    { id: "migraine", title: "Yoga for Migraine Track", style: "yin" },
    { id: "asthma", title: "Yoga for Asthma Track", style: "hatha" }
  ];
  
  const filteredTracks = selectedStyle === "all" 
    ? tracks 
    : tracks.filter(track => track.style === selectedStyle);
  
  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <section className="bg-gradient-yoga py-20">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-white mb-6">
              Select What You Need!
            </h1>
            <p className="text-white/90 text-xl max-w-2xl mx-auto">
              Choose from our curated tracks designed for specific goals and experience levels.
            </p>
          </div>
        </section>
        
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-wrap gap-3 mb-10 justify-center">
              {styles.map(style => (
                <button
                  key={style.id}
                  onClick={() => setSelectedStyle(style.id)}
                  className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    selectedStyle === style.id
                      ? "bg-yoga-green text-white shadow-yoga"
                      : "bg-gray-100 text-yoga-slate hover:bg-yoga-mint"
                  }`}
                >
                  {style.name}
                </button>
              ))}
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {filteredTracks.map(track => (
                <YogaTrackButton
                  key={track.id}
                  title={track.title}
                  to={`/track/${track.id}`}
                />
              ))}
            </div>
          </div>
        </section>
        
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
            <div className="yoga-card overflow-hidden">
              <div className="flex flex-col md:flex-row">
                <div className="md:w-1/2 p-8">
                  <h2 className="text-2xl md:text-3xl font-serif font-bold text-yoga-charcoal mb-4">
                    Not Sure Where to Start?
                  </h2>
                  <p className="text-yoga-slate mb-6">
                    Our AI can analyze your goals, experience level, and physical condition to recommend the perfect track for you.
                  </p>
                  <button className="yoga-button">
                    Get Personalized Recommendation
                  </button>
                </div>
                <div className="md:w-1/2 bg-gradient-yoga flex items-center justify-center p-8">
                  <img 
                    src="/lovable-uploads/d520de82-eecf-48d7-8478-81d72e9596b4.png" 
                    alt="Yoga pose" 
                    className="max-h-60 object-contain"
                  />
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

export default Tracks;
