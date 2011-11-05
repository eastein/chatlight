#include "WProgram.h"
#include "HardwareSerial.h"
#include <Wire.h> 

#define USEPINS 12
#define LOWPIN 2

class Blinker
  {
public:
  Blinker()
    {
    for (int i = 0; i < USEPINS; i++)
      {
      pwm_off[i] = 30 + i * 30;
      pwm_on[i] = 20;
      pwm_state[i] = true;
      pwm_cnt[i] = pwm_on[i] + pwm_off[i];
      }
    }
    
  void step()
    {
    for (int i = 0; i < USEPINS; i++)
      {
        pwm_cnt[i]--;
        if (pwm_cnt[i] == 0)
          pwm_cnt[i] = pwm_on[i] + pwm_off[i];
        
        if (pwm_cnt[i] > pwm_off[i])
          pwm_state[i] = true;
        else
          pwm_state[i] = false;
      }
    }
uint16_t pwm_off[USEPINS];
uint16_t pwm_on[USEPINS];
uint16_t pwm_cnt[USEPINS];
bool pwm_state[USEPINS];
  };
  
Blinker pwm;

#define BUF_SIZE 32
#define MSG_SIZE 9

class CommandReceiver
  {
private:
  int used;
  char buf[BUF_SIZE];
public:
  CommandReceiver()
    {
    used = 0;
    }
  
  /*
   * preconditions: used >= shift
   */
  void consumed(int shift)
    {
      for (int i = 0; i < used - shift; i++)
        buf[i] = buf[i+shift];
        
      used -= shift;
    }
    
  void process_buffer()
    {
    /*
    header is
     :P
     MSG_SIZE of payload
     and then 1 byte that represents every preceding byte xor'd together
    */
    
    if (used >= MSG_SIZE + 3)
      { 
      bool ok = true;
      
      ok = ok && (buf[0] == ':');
      ok = ok && (buf[1] == 'P');

      char xord = buf[0] ^ buf[1];
      
      for (int i = 2; i < MSG_SIZE + 2; i++)
        {
        xord ^= buf[i];
        }
        
      ok = ok && (buf[MSG_SIZE + 2] == xord);
      
      /*
      if (ok)
      {
            delay(500);
      consumed(used);
      return;
      }
      */
      
      uint8_t ln;
      uint16_t _pwm_on;
      uint16_t _pwm_off;
      uint16_t _blink_on;
      uint16_t _blink_off;

      *((char*) (&ln)) = buf[2];
      
      ok = ok && (ln < USEPINS);

      if (ok)
        {
        *((char*)(&_pwm_on) + 1) = buf[3];
        *((char*)(&_pwm_on)) = buf[4];
        *((char*)(&_pwm_off) + 1) = buf[5];
        *((char*)(&_pwm_off)) = buf[6];
        
        pwm.pwm_on[ln]  = _pwm_on;
        pwm.pwm_off[ln] = _pwm_off;
        
        consumed(MSG_SIZE + 3);
        }
      else
        {
        consumed(1);
        if (used == 0)
          delay(2200);
        }
      }
    }
  
  void recv()
    {
    int avail = Serial.available();
    int cantake = BUF_SIZE - used;
    int take;
    
    if (avail <= cantake)
      take = avail;
    else
      take = cantake;
    
    for (int i = 0; i < take; i++)
      buf[used++] = Serial.read();
    
    process_buffer();
    }
  };

CommandReceiver cr;

void set_pins()
  {
  for (int i = 0; i < USEPINS; i++)
    {
    if (pwm.pwm_state[i])
      digitalWrite(i + LOWPIN, HIGH);
    else
      digitalWrite(i + LOWPIN, LOW);
    }
  }

void setup()
  {
  Serial.begin(115200);
  for (int i = 0; i < USEPINS; i++)
    {
    pinMode(i + LOWPIN, OUTPUT);
    }
  set_pins();
  }

void loop() {
  delay(1);

  cr.recv();
  pwm.step();
  set_pins();
}
