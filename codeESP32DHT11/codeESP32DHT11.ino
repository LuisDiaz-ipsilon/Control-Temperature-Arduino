#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Primero configuramos la red Wi-Fi
const char *ssid = "DESKTOPLFFD";
const char *password = "12345678";

//Direccion de la ip de la computadora desde donde se le comparte el wifi obtenida con ipconfig
const char *server = "192.168.137.1";
const int port = 5000;

#define DHTPIN 15     // Pin al que está conectado el DHT11 (pin 15)
#define DHTTYPE DHT11 // Tipo de sensor DHT que estás utilizando

DHT dht(DHTPIN, DHTTYPE);

const int ledPin = 2; // Pin del LED

WiFiClient clientwifi;
HTTPClient client;

void setup()
{
  Serial.begin(9600);
  delay(100);
  // Conectar a la red WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.println("Conectando a la red WiFi...");
  }
  Serial.println("Conectado al WiFi");

  /// Conectar a la API
  client.begin(server, port, "/insert_temperature");

  pinMode(ledPin, OUTPUT);
  dht.begin();
}

void loop()
{
  delay(15000); //15 segundos de delay para cada registro
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature))
  {
    Serial.println("Error al leer el sensor DHT11");
    return;
  }

  // Crear el cuerpo de la solicitud POST
  String postbody = "temperature="+String(temperature);
  Serial.println(postbody);

  // Realizar la solicitud POST con el formato en body
  client.addHeader("Content-Type", "application/x-www-form-urlencoded");
  int httpResponseCode = client.POST(postbody);

  // Verificar si la solicitud fue exitosa
  if (httpResponseCode > 0)
  {
    String response = client.getString();
    Serial.println("Respuesta de la API: " + response);
  }
  else
  {
    String response = client.getString();
    Serial.println(response);
    Serial.println("Fallo en la solicitud POST");
  }

  Serial.print("Humedad: ");
  Serial.print(humidity);
  Serial.print("%\t");
  Serial.print("Temperatura: ");
  Serial.print(temperature);
  Serial.println("°C");

  // Enciende el LED si la temperatura supera los 26°C
  if (temperature > 26.0)
  {
    digitalWrite(ledPin, HIGH);
  }
  else
  {
    digitalWrite(ledPin, LOW);
  }
}
