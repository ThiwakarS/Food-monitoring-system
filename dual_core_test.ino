#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <SimpleDHT.h>
#include <OneButton.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <DallasTemperature.h>
#include <OneWire.h>


int cnt = 0,flg = 0;
int btn_pin = 12;
unsigned long long int lastInterrupt;
boolean trigger = false;
double longi = 0;
double latit = 0;
int temp = 0;
int humi = 0;
float dstemp = 0;
int dspin = 25;
unsigned long long int inte = 0,prev = 0,curr,prevv = 0,dsprev = 0;
unsigned long long int http_prev = 0;
unsigned int Air_quality = 0;
int Air_Qual = 34;
int pinDHT11 = 27;
static const int RXPin = 16, TXPin = 17;
static const uint32_t GPSBaud = 9600;

const char* ssid = "iPhone 16 pro Max";
const char* password = "Thiw1234";

TaskHandle_t Task;


char latii[50];
char longii[50];
OneWire one(dspin);
DallasTemperature dssensor(&one);
SimpleDHT11 dht11(pinDHT11);
TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);
HTTPClient http;



void IRAM_ATTR trig()
{
  if(millis() - lastInterrupt > 300)
  {
    trigger = true;
    lastInterrupt = millis();
  }   
}

LiquidCrystal_I2C lcd(0x27,16,2);

void disp()
{
  // serial.println(a+b)
  cnt +=1;
  delay(100);
  if(cnt == 1)
  {
    lcd.clear();
    flg =1 ;
    lcd.display();
    lcd.backlight();
    lcd.setCursor(0,0);
    lcd.print("LOG: ");
    lcd.print(longi,5);
    lcd.setCursor(0,1);
    lcd.print("LAT: ");
    lcd.print(latit,5);
  }
  else if(cnt == 2)
  {
    lcd.clear();
    lcd.backlight();
    lcd.display();
    lcd.setCursor(0,0);
    lcd.print("Temp: ");
    lcd.print(temp);
    lcd.print(" ^C");
    lcd.setCursor(0,1);
    lcd.print("Humidity: ");
    lcd.print(humi);
    lcd.print(" H");
    
  }
  else if(cnt == 4)
  {
    lcd.clear();
    lcd.backlight();
    lcd.display();
    lcd.setCursor(0,0);
    lcd.print("Gas Percentage:");
    lcd.setCursor(0,1);
    lcd.print(Air_quality);
    lcd.print(" ppm");
  }
  else if(cnt == 3)
  {
    lcd.clear();
    lcd.backlight();
    lcd.display();
    lcd.setCursor(0,0);
    lcd.print("DSTemp: ");
    lcd.print(dstemp);
    lcd.print(" ^C");
  }
  else
  {
    lcd.clear();
    digitalWrite(26,LOW);
    lcd.noDisplay();
    lcd.noBacklight();
    flg = 0;
    cnt = 0;
  }
  prev = millis() - 50;
  Serial.println("\n\nBUTTON PRESSED\n\n");
  
}

// **************************************************************************
// ****************************** VOID SETUP ********************************
// **************************************************************************
void setup() {
  Serial.begin(115200);
  pinMode(2,OUTPUT);
  lcd.init();
  dssensor.begin();
  dssensor.setResolution(12);
//  btn.attachClick(disp);
  pinMode(Air_Qual,INPUT);
  ss.begin(GPSBaud);


  pinMode(btn_pin,INPUT_PULLUP);
  
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  // Perform a POST request to update the variable
  
  http.begin("http://192.168.168.72:8080/update"); // Replace with the server IP address and port
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");

  

  http.end();

  attachInterrupt(12, trig, FALLING);

  xTaskCreatePinnedToCore(
                  Taskcode,   /* Task function. */
                  "Task2",     /* name of task. */
                  10000,       /* Stack size of task */
                  NULL,        /* parameter of the task */
                  1,           /* priority of the task */
                  &Task,      /* Task handle to keep track of created task */
                  0);          /* pin task to core 1 */
  delay(500); 
  
}


// *************************************************************************
// ****************************** VOID LOOP ********************************
// *************************************************************************

void loop() {    

  // button pin 12
  if (trigger == true)
  {
      trigger = false;
      disp();
  }


  curr = millis();
  inte = millis();


  // Auto off after 10sec for display
  if((curr - prev >=10000) and flg == 1) 
  {
    lcd.clear();
    lcd.noBacklight();
    lcd.noDisplay();
    flg = 0;
    cnt = 0;
    prev = curr;
  }


  //ds18b20sensor
  if((curr - dsprev >= 1000))
  {
    dssensor.requestTemperatures();
    dstemp = dssensor.getTempCByIndex(0);
    dsprev = curr;
    Serial.print("DSTEMP: ");
    Serial.println(dstemp);
  }



  // GPS sensor 
  while (ss.available() > 0)
    if (gps.encode(ss.read()))
    {
      displayInfo();
      break;
    }

  
  // DHT 11 sensor
  byte temperature = 0;
  byte humidity = 0;
  int err = SimpleDHTErrSuccess;
  if(inte - prevv >= 700)
  {
    if ((err = dht11.read(&temperature, &humidity, NULL)) == SimpleDHTErrSuccess) 
   {
     Serial.print("\n\nDHT11: ");
     temp = (int)temperature;
     Serial.print((int)temperature); 
     Serial.print(" ^C, ");
     humi = (int)humidity;
     Serial.print((int)humidity);
     Serial.println(" H\n\n");
   }

    else
   {
     temp = 0;
     humi = 0;
     Serial.println("DHT error");
   }  



   //Airquality Sensor
  Air_quality = analogRead(Air_Qual);
  Air_quality = ((Air_quality * 100)/ 4500);
  Serial.print(Air_quality);
  Serial.print(" %");
  Serial.println();
  prevv = millis();
 }


}


// showing info on display
void displayInfo()
{
  Serial.print(F("Location: ")); 
  if (gps.location.isValid())
  {
    Serial.print(gps.location.lat(), 6);
    Serial.print(F(","));
    Serial.print(gps.location.lng(), 6);
    longi = gps.location.lat();
    latit = gps.location.lng();
  }
  else
  {
    Serial.print(F("INVALID"));
    longi = 0;
    latit = 0;
  }

 Serial.print(F("  Date/Time: "));
 if (gps.date.isValid())
 {
   Serial.print(gps.date.month());
   Serial.print(F("/"));
   Serial.print(gps.date.day());
   Serial.print(F("/"));
   Serial.print(gps.date.year());
 }
 else
 {
   Serial.print(F("INVALID"));
 }

 Serial.print(F(" "));
 if (gps.time.isValid())
 {
   if (gps.time.hour() < 10) Serial.print(F("0"));
   Serial.print(gps.time.hour());
   Serial.print(F(":"));
   if (gps.time.minute() < 10) Serial.print(F("0"));
   Serial.print(gps.time.minute());
   Serial.print(F(":"));
   if (gps.time.second() < 10) Serial.print(F("0"));
   Serial.print(gps.time.second());
   Serial.print(F("."));
   if (gps.time.centisecond() < 10) Serial.print(F("0"));
   Serial.print(gps.time.centisecond());
 }
 else
 {
   Serial.print(F("INVALID"));
 }

  Serial.println();
}

void Taskcode( void * pvParameters ){

  Serial.print("Task running on core ");
  Serial.println(xPortGetCoreID());

  for(;;)
  {
    // wifi connection
    if(WiFi.status() == WL_CONNECTED && (millis() - http_prev >= 5000)){
        
        http_prev = millis();
        digitalWrite(2,HIGH);
        
        dtostrf(latit, 17,17,latii);
        
        dtostrf(longi,17,17, longii);

        
        String payload = String(dstemp) + " " + String(temp)+ " " +
        String(humi) + " " + String(Air_quality)+ " (" + 
        longii + "," + latii +")"; // Replace with the desired payload

        
        int httpResponseCode = http.POST(payload);

        
        if (httpResponseCode == HTTP_CODE_OK) {
          Serial.println("Variable updated successfully");
        } else {
          Serial.print("Error updating variable. HTTP response code: ");
          Serial.println(httpResponseCode);
        }
    }

    else if(WiFi.status() != WL_CONNECTED)
    {
        digitalWrite(2,LOW);
    }
    delay(1000);
  }
}
