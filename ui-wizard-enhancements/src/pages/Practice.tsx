import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import BreathingGuide from "@/components/BreathingGuide";
import PoseMeter from "@/components/PoseMeter";
import { Play, Pause, RefreshCcw, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { fetchYogaPose } from "@/lib/api";
import { useAuthProtected } from "@/lib/auth-utils";
import { toast } from "@/components/ui/use-toast";

const Practice = () => {
  // Get poseId from URL params, with better error handling for "undefined" string
  const { poseId } = useParams<{ poseId: string }>();
  const navigate = useNavigate();
  const [isWebcamEnabled, setIsWebcamEnabled] = useState(false);
  const [timer, setTimer] = useState(30);
  const [isPracticing, setIsPracticing] = useState(false);
  const [poseData, setPoseData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { handleProtectedAction, isAuthenticated } = useAuthProtected();
  const timerRef = useRef<number | null>(null);
  
  // Track pose status for PoseMeter
  const [isInCorrectPose, setIsInCorrectPose] = useState(false);
  const [poseCompleted, setPoseCompleted] = useState(false);
  
  // Setup websocket for real-time pose detection feedback
  const socketRef = useRef<WebSocket | null>(null);

  // Use default pose if poseId is missing or literally "undefined"
  const safePoseId = (!poseId || poseId === "undefined") ? "vrksana" : poseId;

  // Redirect if poseId is literally "undefined"
  useEffect(() => {
    if (poseId === "undefined") {
      navigate("/practice/vrksana", { replace: true });
    }
  }, [poseId, navigate]);

  // Timer functionality
  useEffect(() => {
    if (isPracticing && timer > 0) {
      timerRef.current = window.setInterval(() => {
        setTimer(prevTime => {
          if (prevTime <= 1) {
            clearInterval(timerRef.current!);
            setIsPracticing(false);
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000);
    } else if (!isPracticing && timerRef.current) {
      clearInterval(timerRef.current);
    }
    
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPracticing]);

  // Setup WebSocket connection for real-time feedback from backend
  useEffect(() => {
    if (isWebcamEnabled && !socketRef.current) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/pose_feedback`;
      
      try {
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = () => {
          console.log('WebSocket connected');
          socket.send(JSON.stringify({ pose: safePoseId }));
        };
        
        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.is_correct_pose !== undefined) {
              setIsInCorrectPose(data.is_correct_pose);
            }
            
            if (data.pose_completed) {
              setPoseCompleted(true);
              toast({
                title: "Pose Completed!",
                description: "Great job! You've held the pose correctly.",
              });
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        socket.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        socket.onclose = () => {
          console.log('WebSocket connection closed');
        };
        
        socketRef.current = socket;
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
      }
    }
    
    return () => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [isWebcamEnabled, safePoseId]);

  // Reset timer function
  const resetTimer = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setTimer(30);
    setIsPracticing(false);
  };

  // Fetch pose data when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // Try to fetch data from API
        const data = await fetchYogaPose(safePoseId);
        setPoseData(data);
      } catch (error) {
        console.error("Error fetching pose data:", error);
        // Fallback data if API fails
        setPoseData({
          title: safePoseId.charAt(0).toUpperCase() + safePoseId.slice(1) + " Asana",
          sanskrit: "Yoga Pose",
          englishName: safePoseId.charAt(0).toUpperCase() + safePoseId.slice(1) + " Pose",
          difficulty: "Intermediate",
          duration: "30 seconds",
          target: "Balance & Focus",
          instructions: [
            "Stand tall with feet together and arms by your sides",
            "Follow proper form for this pose",
            "Hold the position while breathing deeply",
            "Release gently and with control"
          ]
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [safePoseId]);

  // Handle pose completion
  const handlePoseCompletion = () => {
    setPoseCompleted(true);
    toast({
      title: "Pose Completed!",
      description: "Great job! You've held the pose correctly for the required duration.",
    });
    // Reset pose correct status after completion notification
    setTimeout(() => {
      setIsInCorrectPose(false);
    }, 2000);
  };

  // Current pose data (either from API or fallback)
  const currentPose = poseData || {
    title: "Loading...",
    sanskrit: "",
    englishName: "",
    difficulty: "",
    duration: "",
    target: "",
    instructions: []
  };

  // Function to embed video stream
  const videoUrl = `/video?pose=${safePoseId}`;
  
  // Function to navigate to analytics page
  const handleViewAnalytics = () => {
    navigate("/analytics");
  };

  // Toggle timer function
  const toggleTimer = () => {
    if (timer === 0) {
      setTimer(30);
    }
    setIsPracticing(!isPracticing);
  };

  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <section className="bg-gradient-yoga py-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-serif font-bold text-white mb-3">
              Practice {currentPose.title}
            </h1>
            <div className="flex justify-center items-center gap-3 text-white/90">
              <span className="text-xl">{currentPose.sanskrit}</span>
              <span className="w-1.5 h-1.5 bg-white/70 rounded-full"></span>
              <span className="text-xl">{currentPose.englishName}</span>
            </div>
          </div>
        </section>
        
        <section className="py-12 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Card className="p-6">
                <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-6">Current Pose</h2>
                {isLoading ? (
                  <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yoga-green"></div>
                  </div>
                ) : (
                  <>
                    <img 
                      src={poseData?.imageSrc || "/lovable-uploads/1465e798-1065-402f-b93c-3c8650e0c603.png"}
                      alt={currentPose.title}
                      className="w-full h-auto rounded-lg mb-6"
                    />
                    <div className="grid grid-cols-3 gap-4 mb-6">
                      <div className="text-center p-3 bg-yoga-mint rounded-lg">
                        <h3 className="text-sm text-yoga-charcoal font-medium mb-1">DIFFICULTY</h3>
                        <p className="text-yoga-green">{currentPose.difficulty}</p>
                      </div>
                      <div className="text-center p-3 bg-yoga-mint rounded-lg">
                        <h3 className="text-sm text-yoga-charcoal font-medium mb-1">DURATION</h3>
                        <p className="text-yoga-green">{currentPose.duration}</p>
                      </div>
                      <div className="text-center p-3 bg-yoga-mint rounded-lg">
                        <h3 className="text-sm text-yoga-charcoal font-medium mb-1">TARGET</h3>
                        <p className="text-yoga-green">{currentPose.target}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <h3 className="font-medium text-yoga-charcoal">Instructions:</h3>
                      <ol className="list-decimal list-inside space-y-2 text-yoga-slate">
                        {currentPose.instructions.map((instruction, index) => (
                          <li key={index}>{instruction}</li>
                        ))}
                      </ol>
                    </div>
                  </>
                )}
              </Card>
              
              <Card className="p-6">
                <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-6">Pose Detection</h2>
                
                {/* Breathing Guide Component */}
                {isWebcamEnabled && <BreathingGuide pose={safePoseId} />}
                
                <div className="aspect-video bg-gray-100 rounded-lg mb-6 relative">
                  {!isWebcamEnabled ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Button
                        className="yoga-button"
                        onClick={() => setIsWebcamEnabled(true)}
                      >
                        Enable Camera
                      </Button>
                    </div>
                  ) : (
                    <iframe
                      src={videoUrl}
                      className="w-full h-full object-cover rounded-lg"
                      style={{ minHeight: "650px" }}
                      allow="camera"
                      title="Yoga pose detection"
                    />
                  )}
                </div>
                
                {/* Pose Meter Component */}
                {isWebcamEnabled && (
                  <PoseMeter 
                    pose={safePoseId}
                    isInCorrectPose={isInCorrectPose}
                    onCompletion={handlePoseCompletion}
                  />
                )}
                
                <div className="flex justify-center gap-4 mb-8">
                  <Button
                    className="yoga-button-secondary"
                    onClick={toggleTimer}
                  >
                    {isPracticing ? (
                      <><Pause className="mr-2" size={20} /> Pause</>
                    ) : (
                      <><Play className="mr-2" size={20} /> Start</>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={resetTimer}
                  >
                    <RefreshCcw className="mr-2" size={20} />
                    Reset
                  </Button>
                </div>
                
                <div className="text-center mb-6">
                  <div className="text-4xl font-bold text-yoga-green mb-2">
                    {timer}s
                  </div>
                  <p className="text-yoga-slate">Time Remaining</p>
                </div>
                
                <div className="mt-8 text-center">
                  <Button
                    onClick={handleProtectedAction(handleViewAnalytics)} 
                    className="yoga-button flex items-center gap-2"
                  >
                    <BarChart3 size={18} />
                    <span>See Your Accuracy</span>
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </>
  );
};

export default Practice;