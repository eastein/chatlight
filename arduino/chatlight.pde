#define USEPINS 12
#define LOWPIN 2

uint16_t pwm_off[USEPINS];
uint16_t pwm_on[USEPINS];
uint16_t pwm_cnt[USEPINS];
bool pwm_state[USEPINS];

void set_pins()
  {
  for (int i = 0; i < USEPINS; i++)
    {
    if (pwm_state[i])
      digitalWrite(i + LOWPIN, HIGH);
    else
      digitalWrite(i + LOWPIN, LOW);
    }
  }

void setup()
  {
  for (int i = 0; i < USEPINS; i++)
    {
    pinMode(i + LOWPIN, OUTPUT);

    pwm_off[i] = 30 + i * 30;
    pwm_on[i] = 20;
    pwm_state[i] = true;
    pwm_cnt[i] = pwm_on[i] + pwm_off[i];
    }
  set_pins();
  }

void loop() {
  delay(1);
  for (int i = 0; i < USEPINS; i++)
    {
      pwm_cnt[i]--;
      if (pwm_cnt[i] == 0)
        pwm_cnt[i] = pwm_on[i] + pwm_off[i];
        
      if (pwm_cnt[i] > pwm_on[i])
        pwm_state[i] = true;
      else
        pwm_state[i] = false;
    }
  set_pins();
}
