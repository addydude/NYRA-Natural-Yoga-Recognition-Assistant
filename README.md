<div align="center">
   <img alt="Logo" src="https://user-images.githubusercontent.com/90816300/174459628-275795d3-8ef7-4248-af3f-6dd82859299a.png" />
</div>

<h1 align="center">
NYRA - Natural Yoga Recognition Assistant
</h1>

<p align="center">
  Your personal AI yoga trainer to keep you fit and healthy
</p>

<div align="center">
  <a href="#about">About</a> •
  <a href="#features">Features</a> •
  <a href="#uses">Uses</a> •
  <a href="#tech-stack-used">Tech Stack</a> •
  <a href="#installation">Installation</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#contributing">Contributing</a>
</div>

## About

**NYRA** (Natural Yoga Recognition Assistant) is an AI-powered yoga assistant that helps users perform yoga poses correctly and track their progress. 

Yoga is a great form of exercise with benefits including improved flexibility, strength, and reduced stress and anxiety. Research has shown that yoga can help improve metabolism, heart rate, and respiration. 

However, without proper knowledge about correct posture, people may suffer from acute pain and long-standing chronic problems. NYRA solves this by providing real-time guidance through an AI assistant that ensures users maintain proper form during their yoga practice.

## Features

- 🧘 **Real-time Posture Guidance**: Guides users to perform asanas correctly through AI voice assistant and webcam tracking
- 📊 **Progress Tracking**: Shows accuracy data for each asana in the form of graphs and charts
- ⏱️ **Pose Timer**: Tracks how long a user can hold a specific pose
- 📈 **Usage Analytics**: Keeps track of time invested and provides visual representation of progress
- 🎨 **Engaging Interface**: Designed to inspire consistency and regular practice
- 👥 **Future Feature**: Invite friends for yoga challenges and friendly competitions

## Uses

- 🏠 **Solo Practice**: Ideal for people who live alone and don't want to compromise on their health
- 🔄 **Consistency Builder**: Rewards system helps maintain regular practice
- 🏫 **Learning Environments**: Can be used to build dedicated yoga learning spaces
- 🩺 **Health Monitoring**: Track progress and improvements in flexibility and form

## Tech Stack Used

### Front-End
- HTML5
- CSS3
- JavaScript

### Back-End
- Python 3.10+
- Flask web framework
- OpenCV for computer vision
- Mediapipe for pose detection
- TensorFlow Hub for AI models
- Matplotlib for data visualization

## Installation

### Prerequisites
- Python 3.10 or higher
- Webcam

### Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/nyra.git
   cd nyra
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application
   ```bash
   python app.py
   ```

6. Open your browser and go to `http://127.0.0.1:5000`

For Python 3.12 users, please refer to [PYTHON312.md](./PYTHON312.md) for specific instructions.

## Screenshots

<div align="center">
  <h3>Home Screen</h3>
  <img src="./assets/screenshots/homepage.png" alt="Home Screen" width="80%">
  <br><br>
  
  <h3>Pose Detection</h3>
  <img src="./assets/screenshots/yoga1.png" alt="Pose Detection" width="80%">
  <br><br>
  
  <h3>Progress Analytics</h3>
  <img src="./assets/screenshots/yoga2.png" alt="Progress Analytics" width="80%">
  <br><br>
  
  <h3>Yoga Asanas</h3>
  <img src="./assets/screenshots/pg2.png" alt="Yoga Asanas" width="80%">
  <img src="./assets/screenshots/pg3.png" alt="Yoga Asanas" width="80%">
</div>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<p align="center">
  Made with ❤️ by Aditya Singh
</p>

