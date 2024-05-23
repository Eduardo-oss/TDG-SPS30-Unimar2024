#include <WiFi.h>
#include <HTTPClient.h>

// Serial Port connections for PM2.5 Sensor
#define RXD2 16 // To sensor TXD
#define TXD2 17 // To sensor RXD

struct pms5003data {
  uint16_t framelen;
  uint16_t pm10_standard, pm25_standard, pm100_standard;
  uint16_t pm10_env, pm25_env, pm100_env;
  uint16_t particles_03um, particles_05um, particles_10um, particles_25um, particles_50um, particles_100um;
  uint16_t unused;
  uint16_t checksum;
};

struct pms5003data data;

boolean readPMSdata(Stream *s) {
  if (!s->available()) {
    return false;
  }

  if (s->peek() != 0x42) {
    s->read();
    return false;
  }

  if (s->available() < 32) {
    return false;
  }

  uint8_t buffer[32];
  uint16_t sum = 0;
  s->readBytes(buffer, 32);

  for (uint8_t i = 0; i < 30; i++) {
    sum += buffer[i];
  }

  uint16_t buffer_u16[15];
  for (uint8_t i = 0; i < 15; i++) {
    buffer_u16[i] = buffer[2 + i * 2 + 1];
    buffer_u16[i] += (buffer[2 + i * 2] << 8);
  }

  memcpy((void *)&data, (void *)buffer_u16, 30);

  if (sum != data.checksum) {
    Serial.println("Checksum failure");
    return false;
  }
  return true;
}

const char *ssid = "une4geduardo";
const char *password = "colombia2022";

void setup() {
  Serial.begin(115200);
  Serial.println("Initializing...");

  // Set up UART connection for PM2.5 Sensor
  Serial1.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Serial.println("UART connection established with PM2.5 Sensor");

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  
  if (readPMSdata(&Serial1)) {
    Serial.println("Data received from PM2.5 Sensor");
    Serial.println("---------------------------------------");
    Serial.println("Concentration Units (standard)");
    Serial.print("PM 1.0: "); Serial.print(data.pm10_standard);
    Serial.print("\t\tPM 2.5: "); Serial.print(data.pm25_standard);
    Serial.print("\t\tPM 10: "); Serial.println(data.pm100_standard);
    Serial.println("---------------------------------------");
    Serial.println("Concentration Units (environmental)");
    Serial.print("PM 1.0: "); Serial.print(data.pm10_env);
    Serial.print("\t\tPM 2.5: "); Serial.print(data.pm25_env);
    Serial.print("\t\tPM 10: "); Serial.println(data.pm100_env);
    Serial.println("---------------------------------------");
    Serial.print("Particles > 0.3um / 0.1L air: "); Serial.println(data.particles_03um);
    Serial.print("Particles > 0.5um / 0.1L air: "); Serial.println(data.particles_05um);
    Serial.print("Particles > 1.0um / 0.1L air: "); Serial.println(data.particles_10um);
    Serial.print("Particles > 2.5um / 0.1L air: "); Serial.println(data.particles_25um);
    Serial.print("Particles > 5.0um / 0.1L air: "); Serial.println(data.particles_50um);
    Serial.print("Particles > 10.0 um / 0.1L air: "); Serial.println(data.particles_100um);
    Serial.println("---------------------------------------");

    
  }

  HTTPClient http;
    http.begin("http://192.168.0.2/upload.php");
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String postData = "&pm10=" + String(data.pm10_env) +
                      "&pm25=" + String(data.pm25_env) +
                      "&pm10_s=" + String(data.pm10_standard) +
                      "&pm25_s=" + String(data.pm25_standard);

    Serial.print("Sending data to server: ");
    Serial.println(postData);

    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error on sending post. HTTP Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();

  //delay(10000); // Wait 30 seconds before next reading
}
