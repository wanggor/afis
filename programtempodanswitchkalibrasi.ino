#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoJson.h>

//SSID and Password to your ESP Access Point
const char* ssid = "ESIM 1.0";
const char* password = "merdeka45";
ESP8266WebServer server(80); //Server on port 80
#define USE_SERIAL Serial
int lampu = D1;
int gantiwarna=0;
//#define PIN_OUT1      lampu
//#define PIN_OUT      LED_BUILTIN
#define PIN_OUT      lampu
#define nyala    250
#define mati    250
#define nyalalama    750
#define matispace    250

const char *cobakata;
char kalibrasi;
char gantimode;
char gantilampu;
static const struct {const char letter, *code;} MorseMap[] =
{
  { 'A', ".-" },
  { 'B', "-..." },
  { 'C', "-.-." },
  { 'D', "-.." },
  { 'E', "." },
  { 'F', "..-." },
  { 'G', "--." },
  { 'H', "...." },
  { 'I', ".." },
  { 'J', ".---" },
  { 'K', ".-.-" },
  { 'L', ".-.." },
  { 'M', "--" },
  { 'N', "-." },
  { 'O', "---" },
  { 'P', ".--." },
  { 'Q', "--.-" },
  { 'R', ".-." },
  { 'S', "..." },
  { 'T', "-" },
  { 'U', "..-" },
  { 'V', "...-" },
  { 'W', ".--" },
  { 'X', "-..-" },
  { 'Y', "-.--" },
  { 'Z', "--.." },
  { ' ', "     " }, //Gap between word, seven units 
    
  { '1', ".----" },
  { '2', "..---" },
  { '3', "...--" },
  { '4', "....-" },
  { '5', "....." },
  { '6', "-...." },
  { '7', "--..." },
  { '8', "---.." },
  { '9', "----." },
  { '0', "-----" },
    
  { '.', "·–·–·–" },
  { ',', "--..--" },
  { '?', "..--.." },
  { '!', "-.-.--" },
  { ':', "---..." },
  { ';', "-.-.-." },
  { '(', "-.--." },
  { ')', "-.--.-" },
  { '"', ".-..-." },
  { '@', ".--.-." },
  { '&', ".-..." },
};

String encode(const char *string)
{
  size_t i, j;
  String morseWord = "";
  
  for( i = 0; string[i]; ++i )
  {
    for( j = 0; j < sizeof MorseMap / sizeof *MorseMap; ++j )
    {
      if( toupper(string[i+3]) == MorseMap[j].letter )
      {
        morseWord += MorseMap[j].code;
        break;
      }
    }
    morseWord += " "; //Add tailing space to seperate the chars
  }

  return morseWord;  
}

String decode(String morse)
{
  String msg = "";
  
  int lastPos = 0;
  int pos = morse.indexOf(' ');
  while( lastPos <= morse.lastIndexOf(' ') )
  {    
    for( int i = 0; i < sizeof MorseMap / sizeof *MorseMap; ++i )
    {
      if( morse.substring(lastPos, pos) == MorseMap[i].code )
      {
        msg += MorseMap[i].letter;
      }
    }

    lastPos = pos+1;
    pos = morse.indexOf(' ', lastPos);
    
    // Handle white-spaces between words (7 spaces)
    while( morse[lastPos] == ' ' && morse[pos+1] == ' ' )
    {
      pos ++;
    }
  }

  return msg;
}

 int nyalaa,matii,nyalalamaa, matispacee;
 int ab=0;
void handleText() {
  String message = "";
    String messagebaru = "";
  for (uint8_t i=0; i<server.args(); i++){
    message += server.argName(i) ;

  }

    
    cobakata=message.c_str();
    kalibrasi=cobakata[0];
    gantimode=cobakata[1];
    gantilampu=cobakata[2];
    
  // 
//

//////////
//int nyalaa,matii,nyalalamaa, matispacee;
  if (gantimode=='1')
  {
//    #define nyala    250
//#define mati    250
//#define nyalalama    750
//#define matispace    250
  nyalaa=nyala; 
  matii=mati;
  nyalalamaa=nyalalama;
  matispacee=matispace;
   Serial.print("lambat");
   
  }
  else if (gantimode=='2')
  {
      nyalaa=nyala-125; 
  matii=mati-125;
  nyalalamaa=nyalalama-375;
  matispacee=matispace-125;
   Serial.print("sedang");    
  }
    else if (gantimode=='3')
  {
 
   nyalaa=nyala-125-63; 
  matii=mati-125-63;
  nyalalamaa=nyalalama-375-188;
  matispacee=matispace-125-63;
   Serial.print("cepat");  
  }
  Serial.println(nyalaa);   

 if (gantilampu=='1')
  {

   Serial.print("putih");
   
  }
  else if (gantilampu=='2')
  {

   Serial.print("kuning");    
  }
///////////////////////////////////////////////   
    String morseWord = encode(message.c_str());

   server.send(200, "text/plain", message);
if(kalibrasi=='1')
{
             digitalWrite( PIN_OUT, HIGH );
//        delay( 1000 );
//        digitalWrite( PIN_OUT, LOW );
//        delay( 1000);

}
else{
for(int i=0; i<=morseWord.length(); i++)
  {
   
      Serial.println(morseWord[i]);
    switch( morseWord[i] )
    
    {
      
      case '.': //dit
    
        digitalWrite( PIN_OUT, HIGH );
        delay( nyalaa );
        digitalWrite( PIN_OUT, LOW );
        delay( matii);
          
        break;

      case '-': //dah
//      Serial.println(morseWord[i]);
        digitalWrite( PIN_OUT, HIGH );
        delay( nyalalamaa );
        digitalWrite( PIN_OUT, LOW );
        delay( matii );
          
        break;

      case ' ': //gap
//      Serial.println(morseWord[i]);
        delay( matispacee );

break;
     
    }
  
//  http://192.168.4.1/text?data=HelloWorld.

}
}

 ////////////////////////////


}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("");
  WiFi.mode(WIFI_AP);           //Only Access point
  WiFi.softAP(ssid, password);  //Start HOTspot removing password will disable security
 
  IPAddress myIP = WiFi.softAPIP(); //Get IP address
  Serial.print("HotSpt IP:");
  Serial.println(myIP);
 
//  server.on("/", handleRoot); 
  server.on("/text", handleText); //Which routine to handle at root location
 
  server.begin();                  //Start server
  Serial.println("HTTP server started");
  pinMode(lampu,OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);     // Initialize the LED_BUILTIN pin as an output
}

void loop() {
  // put your main code here, to run repeatedly:
  server.handleClient();
}
