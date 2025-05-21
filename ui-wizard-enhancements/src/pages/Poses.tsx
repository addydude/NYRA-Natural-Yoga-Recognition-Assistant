import { useState } from "react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import YogaPoseCard from "@/components/YogaPoseCard";
import { Search } from "lucide-react";

const Poses = () => {
  const [searchTerm, setSearchTerm] = useState("");
  
  const poses = [
    {
      id: "vrksana",
      title: "Vrksasana",
      description: "A classic standing posture. It establishes strength and balance, and helps you feel centered.",
      imageSrc: "/static/images/vrksana.jpg"
    },
    {
      id: "adhomukha",
      title: "Adho Mukha",
      description: "It strengthens the core and improves circulation, while providing full-body stretch.",
      imageSrc: "/static/images/adho_mukha.jpeg"
    },
    {
      id: "balasana",
      title: "Balasana",
      description: "Balasana is a restful pose that can be sequenced between more challenging asanas.",
      imageSrc: "/static/images/balasana.jpg"
    },
    {
      id: "tadasan",
      title: "Tadasana",
      description: "The foundation of all standing poses. It improves posture, balance, and body awareness.",
      imageSrc: "/static/images/tadasan.jpg"
    },
    {
      id: "trikonasana",
      title: "Trikonasana",
      description: "It is a quintessential standing pose that stretches and strengthens the whole body.",
      imageSrc: "/static/images/trikonasana.jpg"
    },
    {
      id: "virabhadrasana",
      title: "Virabhadrasana",
      description: "It is a foundational yoga pose that balances flexibility and strength in true warrior fashion.",
      imageSrc: "/static/images/virabhadrasana.jpg"
    },
    {
      id: "bhujangasana",
      title: "Bhujangasana",
      description: "A gentle backbend that strengthens the spine and opens the chest.",
      imageSrc: "/static/images/bhujangasana.jpg"
    },
    {
      id: "setubandhasana",
      title: "Setu Bandhasana",
      description: "A gentle backbend that strengthens the back and opens the chest.",
      imageSrc: "/static/images/setubandhasana.png"
    },
    {
      id: "uttanasana",
      title: "Uttanasana",
      description: "A calming forward fold that stretches the entire back of the body.",
      imageSrc: "/static/images/uttanasana.png"
    },
    {
      id: "shavasana",
      title: "Shavasana",
      description: "A restorative pose that relaxes the entire body and calms the mind.",
      imageSrc: "/static/images/shavasana.png"
    },
    {
      id: "ardhamatsyendrasana",
      title: "Ardha Matsyendrasana",
      description: "A seated twist that improves spine mobility and stimulates digestion.",
      imageSrc: "/static/images/ardhamatsyendrasana.png"
    }
  ];
  
  const filteredPoses = poses.filter(pose => 
    pose.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pose.description.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <section className="bg-gradient-yoga py-20">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-white mb-6">
              NYRA - Yoga Poses
            </h1>
            <p className="text-white/90 text-xl max-w-2xl mx-auto">
              Explore our collection of yoga poses with AI-guided instructions and real-time feedback.
            </p>
          </div>
        </section>
        
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-md mx-auto mb-12">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <Search className="w-5 h-5 text-yoga-slate" />
                </div>
                <input
                  type="text"
                  className="block w-full p-4 pl-10 text-sm border border-gray-200 rounded-lg focus:ring-yoga-green focus:border-yoga-green"
                  placeholder="Search poses..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {filteredPoses.map(pose => (
                <YogaPoseCard
                  key={pose.id}
                  id={pose.id}
                  name={pose.title}
                  description={pose.description}
                  imageSrc={pose.imageSrc}
                />
              ))}
            </div>
            
            {filteredPoses.length === 0 && (
              <div className="text-center py-12">
                <h3 className="text-xl font-semibold text-yoga-charcoal mb-2">No poses found</h3>
                <p className="text-yoga-slate">Try adjusting your search term</p>
              </div>
            )}
          </div>
        </section>
        
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
            <div className="yoga-card">
              <div className="flex flex-col md:flex-row items-center">
                <div className="md:w-1/2 p-8">
                  <h2 className="text-2xl md:text-3xl font-serif font-bold text-yoga-charcoal mb-4">
                    Master Your Practice
                  </h2>
                  <p className="text-yoga-slate mb-6">
                    NYRA provides real-time feedback on your form, helping you perfect each pose safely and effectively.
                  </p>
                  <button className="yoga-button">
                    Learn How It Works
                  </button>
                </div>
                <div className="md:w-1/2 p-8 flex justify-center">
                  <img 
                    src="/lovable-uploads/ff13e84e-b54a-4277-9879-148dc4ca5e0c.png" 
                    alt="Yoga analytics" 
                    className="max-h-60 object-contain rounded-lg shadow-lg"
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

export default Poses;
