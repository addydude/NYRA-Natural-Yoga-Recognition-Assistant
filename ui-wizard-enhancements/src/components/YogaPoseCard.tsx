import { Link } from "react-router-dom";
import { Play, LockIcon } from "lucide-react";
import { useAuthProtected } from "@/lib/auth-utils";

interface YogaPoseCardProps {
  id: string;
  name: string;
  englishName?: string;
  description?: string;
  imageSrc: string;
}

const YogaPoseCard = ({ id, name, englishName, description, imageSrc }: YogaPoseCardProps) => {
  const { isAuthenticated } = useAuthProtected();
  
  const title = name || "Yoga Pose";
  const desc = description || (englishName ? `Also known as ${englishName}` : "A traditional yoga posture");
  
  return (
    <Link to={`/pose/${id}`} className="block">
      <div className="yoga-pose-card group">
        <div className="relative overflow-hidden rounded-xl mb-4">
          <img 
            src={imageSrc.startsWith('/') ? imageSrc : `/static/images/${id}.jpg`}
            alt={title} 
            className="w-full h-56 object-cover transition-transform duration-300 group-hover:scale-105"
            onError={(e) => {
              // Enhanced fallback mechanism with dynamic placeholder
              const target = e.target as HTMLImageElement;
              const currentSrc = target.src;
              
              // Try different extensions first
              if (currentSrc.includes(`/${id}.jpg`)) {
                // Try PNG if JPG fails
                target.src = `/static/images/${id}.png`;
              } else if (currentSrc.includes(`/${id}.png`)) {
                // Try GIF if PNG fails
                target.src = `/static/images/${id}.gif`;
              } else if (currentSrc.includes(`/${id}.gif`)) {
                // If specific pose GIFs fail, try common alternatives
                if (id === 'vrksana') {
                  target.src = `/static/images/gif3.gif`;
                } else if (id === 'tadasan') {
                  target.src = `/static/images/Tad-asan.gif`;
                } else {
                  // Use the dynamic placeholder with pose name for better user experience
                  target.src = `/static/images/placeholder/${id}.jpg`;
                }
              } else if (!currentSrc.includes('placeholder')) {
                // Final fallback - dynamic placeholder
                target.src = `/static/images/placeholder/${id}.jpg`;
              }
            }}
          />
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-yoga-green/20">
            <div className="bg-yoga-green text-white p-3 rounded-full">
              {isAuthenticated ? <Play size={20} /> : <LockIcon size={20} />}
            </div>
          </div>
        </div>
        <h3 className="text-xl font-serif font-semibold text-yoga-charcoal group-hover:text-yoga-green transition-colors">
          {title}
        </h3>
        <p className="mt-2 text-yoga-slate line-clamp-3">
          {desc}
        </p>
        <div className="mt-4 flex items-center text-yoga-green font-medium">
          {isAuthenticated ? (
            <>
              <span>Start Practice</span>
              <svg 
                className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </>
          ) : (
            <>
              <LockIcon size={16} className="mr-2" />
              <span>Sign in to practice</span>
            </>
          )}
        </div>
      </div>
    </Link>
  );
};

export default YogaPoseCard;
