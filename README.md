# Smart Fridge Monitoring System
<img width="423" height="173" alt="Screenshot 2025-07-22 alle 13 33 49" src="https://github.com/user-attachments/assets/2022d39e-989e-4a09-a6a4-2ab1f0d278f8" />

A comprehensive IoT solution for monitoring and managing smart refrigerators with real-time sensor data collection, web dashboard, and Telegram bot integration.

## 🚀 Features

### Core Functionality
- **Real-time Monitoring**: Continuous tracking of temperature, humidity, door status, and power consumption
- **Multi-sensor Support**: Internal/external temperature and humidity sensors
- **Door Status Detection**: Monitor fridge door open/close events with automatic alerts
- **Power Consumption Tracking**: Monitor energy usage patterns
- **Alarm System**: Visual and audible alerts for temperature anomalies and extended door opening

### Smart Features
- **Predictive Analytics**: ML-powered user behavior prediction using Random Forest algorithm
- **Telegram Bot Integration**: Real-time notifications and remote monitoring via Telegram
- **Web Dashboard**: Comprehensive web interface for data visualization and management
- **Multi-user Support**: Role-based access control for operators and customers
- **Historical Data**: Complete sensor data history with graphical representation

### Alert System
- **Temperature Alarms**: Automatic alerts when temperature exceeds safe ranges
- **Door Alerts**: Buzzer activation after 10 seconds of door being open
- **Real-time Notifications**: Instant Telegram notifications for out-of-range values
- **LED Indicators**: Visual feedback system on Arduino hardware

## 🏗️ System Architecture

```
┌─────────────────┐    Serial     ┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Arduino UNO   │ ──────────►   │  Python Bridge  │ ──────────────► │ Django Backend  │
│   (Sensors)     │               │  (Data Parser)  │                 │ (Web Server)    │
└─────────────────┘               └─────────────────┘                 └─────────────────┘
                                                                              │
                                                                              │ API Calls
                                                                              ▼
┌─────────────────┐                                                   ┌─────────────────┐
│  Web Dashboard  │                                                   │  Telegram Bot   │
│   (Frontend)    │ ◄─────────────────────────────────────────────── │   (Notifications)│
└─────────────────┘                                                   └─────────────────┘
```

## 📁 Project Structure

```
smart-fridge-system/
├── bot/
│   └── bot.py                 # Telegram bot implementation
├── codes/
│   ├── Arduino/
│   │   └── all_sensors/
│   │       └── all_sensors.ino # Arduino sensor code
│   └── bridge_Serial_HTTP.py   # Serial to HTTP bridge
├── config/
│   └── main/
│       ├── urls.py            # Django URL routing
│       ├── views.py           # Django views and API endpoints
│       └── models.py          # Database models (implied)
└── README.md                  # This file
```

## 🔧 Hardware Requirements

### Arduino Components
- **Arduino UNO** (or compatible microcontroller)
- **2x DHT11 sensors** (internal and external temperature/humidity)
- **Push button** (door status sensor)
- **Buzzer** (alarm system)
- **LED** (status indicator)
- **Potentiometer** (power consumption simulation)
- **Resistors and connecting wires**

### Connections
- DHT11 Internal: Pin 5
- DHT11 External: Pin 6
- Door Button: Pin 2
- Buzzer: Pin 9
- LED: Pin 10
- Potentiometer: Analog Pin A0

## 💻 Software Requirements

### Backend Dependencies
- Python 3.8+
- Django 4.x
- pandas
- scikit-learn
- joblib
- requests
- pyserial

### Arduino Libraries
- SimpleDHT (for DHT11 sensors)

### Telegram Bot Dependencies
- python-telegram-bot

## 🛠️ Installation & Setup

### 1. Hardware Setup
1. Connect all sensors to Arduino according to the pin configuration
2. Upload `codes/Arduino/all_sensors/all_sensors.ino` to your Arduino
3. Connect Arduino to your computer via USB

### 2. Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd smart-fridge-system

# Install Python dependencies
pip install django pandas scikit-learn joblib requests pyserial python-telegram-bot

# Set up Django
cd config
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

# Start Django server
python manage.py runserver
```

### 3. Configuration
Create a `config.ini` file in the bridge directory:
```ini
[DJANGO]
Url = http://127.0.0.1:8000/api/
X-AIO-Key = your-api-key

[Serial]
UseDescription = true
PortDescription = arduino
PortName = COM3

[TELEGRAM]
Url = your-telegram-bot-url
```

### 4. Telegram Bot Setup
1. Create a new bot using [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Update `BOT_TOKEN` in both `bot/bot.py` and `config/main/views.py`
4. Start the bot:
```bash
cd bot
python bot.py
```

### 5. Start the Bridge
```bash
cd codes
python bridge_Serial_HTTP.py
```

## 🎮 Usage

### Web Dashboard
1. Navigate to `http://127.0.0.1:8000`
2. Register/login to access the dashboard
3. Register a new fridge (operators) or add existing fridge (customers)
4. View real-time data, charts, and alarm history

### Telegram Bot Commands
- `/start <fridge_id>` - Subscribe to fridge notifications
- `/status <fridge_id>` - Get current sensor readings
- `/behaviour <fridge_id>` - Get behavior prediction
- `/help` - Show available commands
- `/stop` - Unsubscribe from notifications

### Natural Language Processing
The bot supports natural language commands using XLM-RoBERTa for intent classification:
- "How is my fridge doing?" → Status command
- "Stop sending me alerts" → Stop command
- "I need help" → Help command
- "How am I behaving?" → Behaviour prediction

## 🤖 Machine Learning Features

### Behavior Prediction Model
The system uses a Random Forest classifier to predict user behavior based on:
- **External Temperature**: Environmental conditions
- **Internal Temperature Variation**: Temperature changes during door opening
- **Door Open Time**: Duration the fridge door remains open

### Prediction Categories
- **0 (Good)**: "You are acting on the right track"
- **2 (Medium)**: "You are doing well, but you can do better"  
- **1 (Bad)**: "You are acting irresponsibly"

## 📊 API Endpoints

### Data Collection
- `POST /data/` - Receive sensor data from bridge
- `GET /data/alarm/<pk>/` - Check alarm status for bridge

### Telegram Integration
- `POST /api/store_chat_id/` - Register Telegram user
- `GET /api/get_least_recent_data/` - Get latest sensor data
- `GET /api/data/predict/<pk>/` - Get behavior prediction

### Web Dashboard
- `GET /chart-data/<pk>/` - Get chart data for visualization
- `GET /alarmshistory/<pk>/` - Get alarm history

## ⚙️ Configuration

### Sensor Thresholds
```python
ACCEPTABLE_RANGES = {
    'int_temp': (0, 10),      # °C
    'ext_temp': (0, 35),      # °C  
    'int_hum': (20, 70),      # %
    'power_consumption': (0, 1000),  # W
}
```

### Arduino Settings
- **Data transmission interval**: 5 seconds
- **Temperature reading interval**: 2 seconds
- **Door open alarm threshold**: 10 seconds
- **Arduino ID**: Configurable unique identifier

## 🔒 Security Features

- **User Authentication**: Django's built-in authentication system
- **Role-based Access**: Separate permissions for operators and customers
- **API Authorization**: X-AIO-Key header validation
- **Fridge Association**: Secret number verification for fridge registration
- **Telegram User Verification**: Chat ID and fridge ID validation

## 📈 Monitoring & Alerts

### Automatic Notifications
- **Temperature Exceeding Limits**: When internal temperature > 5°C and door closed
- **Door Left Open**: Visual and audible alerts after 10 seconds
- **Out-of-Range Values**: Telegram notifications for any sensor reading outside acceptable ranges
- **System Status**: Real-time LED feedback on Arduino

### Data Visualization
- **Real-time Charts**: Temperature, humidity, and power consumption graphs
- **Historical Trends**: 10-point moving data visualization
- **Alarm History**: Complete log of all triggered alarms

## 🐛 Troubleshooting

### Common Issues

**Arduino not detected:**
- Check USB connection and drivers
- Verify correct port in `config.ini`
- Ensure Arduino IDE can communicate with device

**Serial communication errors:**
- Verify baud rate (9600) matches in all components
- Check for interference or loose connections
- Monitor serial output for data format consistency

**Django server errors:**
- Verify all dependencies are installed
- Check database migrations are up to date
- Ensure correct Django settings

**Telegram bot not responding:**
- Verify bot token is correct
- Check internet connectivity
- Ensure bot is started and running

**Missing sensor data:**
- Check sensor wiring and power supply
- Verify DHT11 sensors are functional
- Monitor Arduino serial output for sensor readings

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Development Team** - Initial work and system architecture
- **Contributors** - Various improvements and bug fixes

## 🙏 Acknowledgments

- Arduino community for sensor libraries
- Django framework for robust web backend
- Telegram Bot API for seamless messaging integration
- Hugging Face for NLP model hosting
- scikit-learn for machine learning capabilities

---

**Note**: This system is designed for educational and demonstration purposes. For production use, consider additional security measures, error handling, and scalability improvements.
