
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

interface YogaTrackButtonProps {
  title: string;
  to: string;
}

const YogaTrackButton = ({ title, to }: YogaTrackButtonProps) => {
  return (
    <Link to={to} className="group">
      <div className="yoga-track-button group flex items-center justify-between">
        <span>{title}</span>
        <ArrowRight size={20} className="transition-transform duration-300 group-hover:translate-x-1" />
      </div>
    </Link>
  );
};

export default YogaTrackButton;
