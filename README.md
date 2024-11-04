# Green Energy-Efficient IoT Network for Environmental Monitoring

## Overview
This project focuses on creating an eco-friendly, energy-efficient IoT network for environmental monitoring using a Raspberry Pi and various sensors. The goal is to reduce the environmental impact of IoT devices while providing real-time, reliable data for assessing environmental conditions.

## Features
- **Real-time Monitoring**: Provides up-to-date data on temperature, humidity, soil moisture, rain detection, air quality, and light intensity.
- **Energy Efficiency**: Designed to minimize energy consumption and reduce the carbon footprint.
- **Remote Accessibility**: Data can be accessed remotely, offering insights into otherwise hard-to-reach environments.

## Hardware Components
- Raspberry Pi 3
- DHT11 Temperature and Humidity Sensor
- Soil Moisture Sensor
- Rain Sensor
- MQ Gas Sensor (for CO, LPG, and Smoke detection)
- BH1750 Light Sensor
- Additional wiring and power components

## Software
The project uses Python for data collection, processing, and transmission to Azure IoT Hub and a custom REST API.

### Main Libraries Used
- `Adafruit_DHT`: To interact with the DHT11 sensor.
- `smbus` and `spidev`: For interfacing with sensors via I2C and SPI.
- `azure.iot.device`: For connecting and sending data to Azure IoT Hub.
- `aiohttp`: For asynchronous HTTP requests.

## Installation
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Azure IoT Hub**: Add your IoT Hub connection string in the `CONNECTION_STRING` variable in the code.

## Usage
1. **Run the Script**:
    ```bash
    python main.py
    ```

2. The script will initialize sensors and periodically send data to both the Azure IoT Hub and the REST API endpoint.

## Future Improvements
- **Enhanced Energy Optimization**: Additional optimizations to further reduce power consumption.
- **Extended Sensor Range**: Integrate more sensors to cover additional environmental parameters.
- **Enhanced Data Visualization**: Develop a dedicated dashboard for better real-time data analysis.
  

## Contact
Feel free to reach out if you have questions or suggestions!

- **Name**: Zehra Grbovic
- **LinkedIn**: linkedin.com/in/zehra-grbović
