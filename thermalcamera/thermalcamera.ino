#include <Wire.h>
#include "Adafruit_MLX90640.h"

Adafruit_MLX90640 mlx;

float frame[32 * 24];

void setup() {
  Serial.begin(115200);

  Wire.begin();
  Wire.setClock(400000);

  if (!mlx.begin()) {
    Serial.println("MLX90640 nao encontrado");
    while (1);
  }

  mlx.setMode(MLX90640_CHESS);
  mlx.setResolution(MLX90640_ADC_18BIT);
  mlx.setRefreshRate(MLX90640_8_HZ);

  Serial.println("MLX90640 iniciado");
}

void loop() {

  if (mlx.getFrame(frame) != 0) {
    Serial.println("Erro ao capturar frame");
    return;
  }

  for (int y = 0; y < 24; y++) {

    for (int x = 0; x < 32; x++) {

      int index = y * 32 + x;

      Serial.print(frame[index], 2);

      if (x < 31)
        Serial.print(",");
    }

    Serial.println();
  }

  Serial.println("FRAME_END");

  delay(100);
}