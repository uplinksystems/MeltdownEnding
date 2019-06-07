void setup() {
  pinMode(2, INPUT);
  pinMode(3, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  bool success = pulseIn(2, HIGH) > 100;
  digitalWrite(LED_BUILTIN, success);
  digitalWrite(3, success);
  if (success){
    delay(1000);
  }
}
