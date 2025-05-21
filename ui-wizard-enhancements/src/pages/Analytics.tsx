import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { getFlaskChartsUrl, fetchPoseProgress, fetchPoseChartData } from "@/lib/api";
import { getUserAccuracyData, getUserPracticeSessions, formatDate } from "@/lib/firestore-service";
import { useAuth } from "@/components/auth/AuthContext";
import Chart from "chart.js/auto";

const Analytics = () => {
  const bodyPartChartRef = useRef<HTMLCanvasElement | null>(null);
  const weeklyChartRef = useRef<HTMLCanvasElement | null>(null);
  const progressChartRef = useRef<HTMLCanvasElement | null>(null);
  const [selectedPose, setSelectedPose] = useState<string>("vrksana");
  const [hasFallbackData, setHasFallbackData] = useState(false);
  const { user } = useAuth();
  
  // Track chart instances so we can destroy them when needed
  const chartInstances = useRef<{
    bodyPartChart: Chart | null;
    weeklyChart: Chart | null;
    progressChart: Chart | null;
  }>({
    bodyPartChart: null,
    weeklyChart: null,
    progressChart: null
  });

  // Fetch pose progress data from Flask backend
  const { data: poseProgressData, isLoading: loadingProgress } = useQuery({
    queryKey: ['pose-progress', selectedPose],
    queryFn: async () => {
      try {
        return await fetchPoseProgress(selectedPose);
      } catch (error) {
        console.error(`Error fetching progress for ${selectedPose}:`, error);
        setHasFallbackData(true);
        return null;
      }
    },
  });

  // Fetch chart data from Flask backend
  const { data: chartData, isLoading: loadingChartData } = useQuery({
    queryKey: ['pose-chart-data', selectedPose],
    queryFn: async () => {
      try {
        return await fetchPoseChartData(selectedPose);
      } catch (error) {
        console.error(`Error fetching chart data for ${selectedPose}:`, error);
        setHasFallbackData(true);
        return null;
      }
    },
  });

  // Fetch accuracy data from Firestore (as backup)
  const { data: accuracyData, isLoading: loadingAccuracy } = useQuery({
    queryKey: ['user-accuracy', user?.id],
    queryFn: async () => {
      if (!user) throw new Error('User not authenticated');
      return await getUserAccuracyData(user.id);
    },
    enabled: !!user,
    onError: (err) => {
      console.error("Error fetching accuracy data:", err);
      setHasFallbackData(true);
    }
  });

  // Fetch practice sessions from Firestore
  const { data: practiceSessions, isLoading: loadingSessions } = useQuery({
    queryKey: ['practice-sessions', user?.id],
    queryFn: async () => {
      if (!user) throw new Error('User not authenticated');
      return await getUserPracticeSessions(user.id, 5);
    },
    enabled: !!user,
    onError: (err) => {
      console.error("Error fetching practice sessions:", err);
    }
  });

  // Create and update the body part accuracy chart
  useEffect(() => {
    if (!bodyPartChartRef.current || loadingChartData) return;
    
    if (chartInstances.current.bodyPartChart) {
      chartInstances.current.bodyPartChart.destroy();
    }
    
    // Use data from our Flask backend if available, or fallback data
    const labels = chartData?.accuracy?.labels || ['Right Arm', 'Left Arm', 'Right Leg', 'Left Leg'];
    const values = chartData?.accuracy?.values || [70, 75, 65, 80];
    
    const ctx = bodyPartChartRef.current.getContext('2d');
    if (!ctx) return;
    
    chartInstances.current.bodyPartChart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Accuracy (%)',
          data: values,
          fill: true,
          backgroundColor: 'rgba(74, 210, 149, 0.2)',
          borderColor: 'rgb(74, 210, 149)',
          pointBackgroundColor: 'rgb(74, 210, 149)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(74, 210, 149)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        elements: {
          line: { borderWidth: 3 }
        },
        scales: {
          r: {
            angleLines: { display: true },
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: { stepSize: 20 }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Body Part Accuracy',
            font: {
              size: 16
            }
          }
        }
      }
    });
    
    return () => {
      if (chartInstances.current.bodyPartChart) {
        chartInstances.current.bodyPartChart.destroy();
      }
    };
  }, [chartData, loadingChartData, selectedPose]);
  
  // Create and update the weekly practice chart
  useEffect(() => {
    if (!weeklyChartRef.current || !poseProgressData) return;
    
    if (chartInstances.current.weeklyChart) {
      chartInstances.current.weeklyChart.destroy();
    }
    
    // Create a distribution of practice time across days of the week
    // based on total practice time
    const totalPracticeTime = poseProgressData?.total_practice_time || 0;
    const weeklyData = generateWeeklyData(totalPracticeTime);
    
    const ctx = weeklyChartRef.current.getContext('2d');
    if (!ctx) return;
    
    chartInstances.current.weeklyChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        datasets: [{
          label: 'Minutes Practiced',
          data: weeklyData,
          backgroundColor: 'rgba(75, 192, 192, 0.8)',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { 
            beginAtZero: true,
            title: {
              display: true,
              text: 'Minutes'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Day of Week'
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          title: {
            display: true,
            text: 'Weekly Practice Distribution'
          }
        }
      }
    });
    
    return () => {
      if (chartInstances.current.weeklyChart) {
        chartInstances.current.weeklyChart.destroy();
      }
    };
  }, [poseProgressData, selectedPose]);
  
  // Create and update the attempts vs completions pie chart
  useEffect(() => {
    if (!progressChartRef.current || !chartData) return;
    
    if (chartInstances.current.progressChart) {
      chartInstances.current.progressChart.destroy();
    }
    
    // Use data from Flask backend or fallback
    const progressValues = chartData?.progress?.values || [5, 2];
    
    const ctx = progressChartRef.current.getContext('2d');
    if (!ctx) return;
    
    chartInstances.current.progressChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Attempts', 'Completions'],
        datasets: [{
          label: 'Count',
          data: progressValues,
          backgroundColor: [
            'rgba(54, 162, 235, 0.8)',
            'rgba(74, 210, 149, 0.8)'
          ],
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Attempts vs Completions'
          }
        }
      }
    });
    
    return () => {
      if (chartInstances.current.progressChart) {
        chartInstances.current.progressChart.destroy();
      }
    };
  }, [chartData, selectedPose]);
  
  // Handle pose selection change
  const handlePoseChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedPose(event.target.value);
  };
  
  // Generate weekly data based on total practice time
  const generateWeeklyData = (totalSeconds: number) => {
    // Convert seconds to minutes
    const totalMinutes = Math.max(1, Math.round(totalSeconds / 60));
    
    // If we have very minimal data, return a predefined pattern
    if (totalMinutes < 10) {
      return [1, 2, 1, 2, 3, 5, 5];
    }
    
    // Create a distribution with more practice on weekends
    const scale = totalMinutes / 60; // Scale factor based on total practice time
    
    return [
      Math.max(1, Math.round(7 * scale)),   // Monday
      Math.max(1, Math.round(9 * scale)),   // Tuesday
      Math.max(1, Math.round(8 * scale)),   // Wednesday
      Math.max(1, Math.round(10 * scale)),  // Thursday
      Math.max(1, Math.round(15 * scale)),  // Friday
      Math.max(1, Math.round(25 * scale)),  // Saturday
      Math.max(1, Math.round(25 * scale))   // Sunday
    ];
  };
  
  // Calculate overall metrics for display
  const calculateOverallAccuracy = () => {
    if (chartData?.accuracy?.values && chartData.accuracy.values.length > 0) {
      const sum = chartData.accuracy.values.reduce((a: number, b: number) => a + b, 0);
      return Math.round(sum / chartData.accuracy.values.length);
    }
    return 0;
  };
  
  // Get completion rate as percentage
  const getCompletionRate = () => {
    if (chartData?.progress?.values) {
      const [attempts, completions] = chartData.progress.values;
      return attempts > 0 ? Math.round((completions / attempts) * 100) : 0;
    }
    return 0;
  };
  
  // Handle redirection to Flask's charts route
  const viewDetailedAnalytics = () => {
    window.location.href = getFlaskChartsUrl();
  };

  const isLoading = loadingAccuracy || loadingSessions || loadingProgress || loadingChartData;

  return (
    <>
      <Navigation />
      
      <main className="pt-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-3xl font-serif font-bold text-yoga-charcoal mb-8 text-center">
            Your Yoga Performance Analytics
          </h1>
          
          {/* Pose selector and warning banner */}
          <div className="mb-8">
            <div className="bg-white p-4 rounded-lg shadow-sm flex flex-col sm:flex-row justify-between items-center">
              <label className="mb-2 sm:mb-0 text-yoga-charcoal font-medium">
                Select pose: 
                <select 
                  className="ml-2 p-2 border border-gray-200 rounded" 
                  value={selectedPose}
                  onChange={handlePoseChange}
                >
                  <option value="vrksana">Vrksasana (Tree Pose)</option>
                  <option value="adhomukha">Adho Mukha (Downward Dog)</option>
                  <option value="balasana">Balasana (Child's Pose)</option>
                  <option value="tadasan">Tadasana (Mountain Pose)</option>
                  <option value="trikonasana">Trikonasana (Triangle Pose)</option>
                  <option value="virabhadrasana">Virabhadrasana (Warrior Pose)</option>
                  <option value="bhujangasana">Bhujangasana (Cobra Pose)</option>
                  <option value="setubandhasana">Setubandhasana (Bridge Pose)</option>
                  <option value="uttanasana">Uttanasana (Standing Forward Bend)</option>
                  <option value="shavasana">Shavasana (Corpse Pose)</option>
                  <option value="ardhamatsyendrasana">Ardha Matsyendrasana (Half Lord of Fishes)</option>
                </select>
              </label>
              
              <button 
                onClick={viewDetailedAnalytics}
                className="mt-2 sm:mt-0 px-4 py-2 bg-yoga-green text-white rounded hover:bg-opacity-90 transition-colors"
              >
                View Classic Analytics
              </button>
            </div>
          </div>
          
          {/* Warning banner for fallback data */}
          {hasFallbackData && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 p-4 rounded-lg max-w-4xl mx-auto mb-8">
              <p className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Some data may be sample data. Continue practicing for more accurate analytics.
              </p>
            </div>
          )}
          
          {/* Progress statistics */}
          <div className="stats-container grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="stat-box bg-white p-4 rounded-lg shadow-sm text-center">
              <h3 className="text-yoga-green font-medium">Attempts</h3>
              <p className="text-3xl font-bold text-yoga-charcoal">
                {isLoading ? "..." : poseProgressData?.attempts || 0}
              </p>
            </div>
            <div className="stat-box bg-white p-4 rounded-lg shadow-sm text-center">
              <h3 className="text-yoga-green font-medium">Completions</h3>
              <p className="text-3xl font-bold text-yoga-charcoal">
                {isLoading ? "..." : poseProgressData?.completions || 0}
              </p>
            </div>
            <div className="stat-box bg-white p-4 rounded-lg shadow-sm text-center">
              <h3 className="text-yoga-green font-medium">Practice Time</h3>
              <p className="text-3xl font-bold text-yoga-charcoal">
                {isLoading ? "..." : poseProgressData?.practice_time_display || "0 min"}
              </p>
            </div>
            <div className="stat-box bg-white p-4 rounded-lg shadow-sm text-center">
              <h3 className="text-yoga-green font-medium">Best Accuracy</h3>
              <p className="text-3xl font-bold text-yoga-charcoal">
                {isLoading ? "..." : `${Math.round(chartData?.best_accuracy * 100 || 0)}%`}
              </p>
            </div>
          </div>
          
          {/* Charts container */}
          <div className="yoga-card p-0">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="spinner"></div>
                <p className="mt-4 text-yoga-slate">Loading analytics data...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
                {/* Body Part Accuracy Chart */}
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <h3 className="text-xl font-medium text-yoga-charcoal mb-2">Body Part Accuracy</h3>
                  <div className="h-64">
                    <canvas ref={bodyPartChartRef}></canvas>
                  </div>
                </div>
                
                {/* Progress Chart */}
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <h3 className="text-xl font-medium text-yoga-charcoal mb-2">Attempts vs Completions</h3>
                  <div className="h-64">
                    <canvas ref={progressChartRef}></canvas>
                  </div>
                </div>
                
                {/* Weekly Practice Distribution */}
                <div className="bg-white p-4 rounded-lg shadow-sm md:col-span-2">
                  <h3 className="text-xl font-medium text-yoga-charcoal mb-2">Weekly Practice Distribution</h3>
                  <div className="h-64">
                    <canvas ref={weeklyChartRef}></canvas>
                  </div>
                </div>
                
                {/* Performance Summary */}
                <div className="bg-white p-4 rounded-lg shadow-sm md:col-span-2">
                  <h2 className="text-xl font-medium text-yoga-charcoal mb-4">Performance Summary</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-lg font-medium text-yoga-green mb-2">Key Insights</h3>
                      <ul className="list-disc list-inside text-yoga-slate space-y-2">
                        {chartData?.accuracy?.values && (
                          <>
                            <li>Your overall accuracy is {calculateOverallAccuracy()}%</li>
                            <li>Completion rate: {getCompletionRate()}%</li>
                            <li>Total practice time: {poseProgressData?.practice_time_display || "0 min"}</li>
                          </>
                        )}
                        {poseProgressData?.last_practiced && (
                          <li>Last practiced: {poseProgressData.last_practiced}</li>
                        )}
                      </ul>
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-medium text-yoga-green mb-2">Recommendations</h3>
                      <ul className="list-disc list-inside text-yoga-slate space-y-2">
                        {chartData?.accuracy?.values && chartData.accuracy.values[0] < 70 && 
                          <li>Focus on improving your right arm positioning</li>
                        }
                        {chartData?.accuracy?.values && chartData.accuracy.values[1] < 70 && 
                          <li>Work on better left arm alignment</li>
                        }
                        {chartData?.accuracy?.values && chartData.accuracy.values[2] < 70 && 
                          <li>Practice balancing your right leg position</li>
                        }
                        {chartData?.accuracy?.values && chartData.accuracy.values[3] < 70 && 
                          <li>Pay attention to your left leg alignment</li>
                        }
                        {chartData?.accuracy?.values && chartData.accuracy.values.every(v => v >= 70) && 
                          <li>Great job! All your positions are well aligned</li>
                        }
                        <li>Continue practicing regularly for better results</li>
                        <li>Consider trying more challenging poses as you improve</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Action buttons */}
          <div className="mt-8 text-center">
            <Link to={`/practice/${selectedPose}`} className="yoga-button mr-4">
              Practice This Pose
            </Link>
            <Link to="/poses" className="yoga-button-secondary">
              Explore More Poses
            </Link>
          </div>
        </div>
      </main>
      
      <Footer />
    </>
  );
};

export default Analytics;
