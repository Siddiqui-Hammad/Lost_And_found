# TRACE AI — ESP32 Smart Box Pinout & Circuit Guide

## 1. Bill of Materials (BOM) & Budget

| Component | Specification | Estimated Cost (INR) |
|---|---|---|
| **Micro-controller** | ESP32-WROOM-32 NodeMCU Development Board | ₹380 |
| **RFID Reader** | MFRC-522 13.56 MHz RFID Module + S50 Tag/Card | ₹120 |
| **Display** | 0.96" I2C OLED (SSD1306, 128×64) | ₹140 |
| **Actuator** | TowerPro SG90 9g Micro Servo Motor | ₹90 |
| **Buzzer** | 5V Active Piezo Buzzer | ₹20 |
| **Power Supply** | 5V 2A Micro-USB Adapter / Power Bank | ₹150 |
| **Enclosure** | Acrylic / 3D Printed / MDF Smart Drop Box | ₹250 |
| **Total** | | **~₹1,150 INR** |

---

## 2. Wiring & Pin Connections

### A. MFRC-522 RFID Module (SPI Interface)
| MFRC-522 Pin | ESP32 GPIO Pin | Description |
|---|---|---|
| **VCC** | **3.3V** (Do NOT connect to 5V) | Power supply |
| **RST** | **GPIO 22** | Reset line |
| **GND** | **GND** | Ground |
| **MISO** | **GPIO 19** | SPI Master In Slave Out |
| **MOSI** | **GPIO 23** | SPI Master Out Slave In |
| **SCK** | **GPIO 18** | SPI Clock |
| **SDA (SS)** | **GPIO 21** | SPI Slave Select |

### B. SSD1306 0.96" OLED Display (I2C Interface)
| OLED Pin | ESP32 GPIO Pin | Description |
|---|---|---|
| **VCC** | **3.3V** or **5V** | Power supply |
| **GND** | **GND** | Ground |
| **SCL** | **GPIO 22** (Shared I2C Clock) | Clock |
| **SDA** | **GPIO 21** (Shared I2C Data) | Data |

### C. SG90 Servo Motor (PWM Control)
| Servo Wire | ESP32 Pin | Description |
|---|---|---|
| **Brown / Black** | **GND** | Ground |
| **Red** | **VIN (5V)** | Motor Power |
| **Orange / Yellow** | **GPIO 13** | PWM Signal Pin |

### D. Active Buzzer
| Buzzer Pin | ESP32 Pin | Description |
|---|---|---|
| **Positive (+)** | **GPIO 14** | Tone Signal |
| **Negative (-)** | **GND** | Ground |
