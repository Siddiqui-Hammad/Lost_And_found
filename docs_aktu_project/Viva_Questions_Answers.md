# AKTU Mini Project Viva Questions & Answers

## Question 1: Where is IoT in your project?
**Answer:** "Our ESP32-based Smart Collection Box serves as the IoT hardware unit. When a found item is deposited, the MQRC522 RFID reader digitally registers the item's temporary tag UID, while the ESP32 automatically attaches the box's physical location zone and timestamp before sending it over Wi-Fi to our FastAPI server. It also controls an SG90 Servo door lock and SS@1306 OLED display."

---

## Question 2: Where is AI in your project?
**Answer:** "AI is used in our Semantic Matching Engine. It uses TF-IDF word embeddings and Cosine Similarity to understand the meaning of the descriptions (e.g. 'Boat airdopes white' and 'white wireless earbuds'). It then applies a weighted multi-attribute formula across Category, Color, Brand, Location, and Time to generate a precise Match Score."

---

## Question 3: Why doesn't the AI directly return the item to the student?
**Answer:** "To prevent fraudulent claims and errors. The AI excels at discovery and pointing out possibilities, but the final approval requires human proctor verification. The student must answer private identification questions (such as inner contents, markings, or wallpaper) before the proctor marks the item as RETURNED."

---

## Question 4: How does ESP32 communicate with FastAPI?
**Answer:** "Via Wi-Fi using HTTP POST requests with JSON payloads to the `/api/iot/deposit` subroute."

---

## Question 5: What is the prototype cost?
**Answer:** "Approximately ₰850 – ‰1,200, making it highly affordable for campus-wide deployment."