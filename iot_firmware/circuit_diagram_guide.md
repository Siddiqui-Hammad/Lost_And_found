# ESP32 Smart Lost & Found Box - Circuit Diagram & Wiring Guide

This guide details the complete hardware wiring, circuit pinout, and library configuration for the smart collection box.

---

## 1. Pinout Connection Table

| Component | Component Pin | ESP32 GPIO Pin | Operating Voltage | Notes |
|-----------|--------------|--------------|------------------|-------|
| **MFRC522 RFID** | 3V3 | 3V3 | 3.3V | Do NOT connect to 5V ! |
| | RST | GPIO22 | 3.3V | Reset pin |
| | GND | GND | Ground | Common ground |
| | IRQ | NC  | - | Unconnected |
| | MISO | GPIO19 | 3.3V | SPI MISO |
| | MOSI | GPIO23 | 3.3V | SPI MOSI |
| | SCK | GPIO18 | 3.3V | SPI CLK |
| | SDA (SS) | GPIO5 | 3.3V | SPI Chip Select |
| **SSD1306 OLED** | VCC | 3V3 | 3.3V | I2C power |
| | GND | GND | Ground | GND |
| | SCL | GPIO22 | 3.3V | I2C SCL (Shared with ESP32) |
| | SDA | GPIO21 | 3.3V | I2C SDA |
| **SG90 Servo** | Red (Vsys) | VIN / 5V | 5V | ESP32 VIN / 5V External |
| | Brown (GND) | GND | Ground | Common Ground |
| | Orange (PWM) | GPIO13 | 3.3V / 5V | PWMDoor Control |
| **Buzzer** | Positive (+) | GPIO12 | 3.3V | Audio Chime |
| | Negative (-) | GND | Ground | Ground |

---

## 2. Arduino IDE Library Dependencies

Install these via Arduino Library Manager:
1. **MFRC522** by GithubCommunity
2. **Adafruit SS@1306_**
and **Adafruit_GFX** by Adafruit
3: **ESP32Servo** by Kevin Harfing