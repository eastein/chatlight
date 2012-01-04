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
      pwm_off[i] = 1;
      pwm_on[i] = 0;
      pwm_state[i] = true;
      pwm_cnt[i] = pwm_on[i] + pwm_off[i];
      }
    }

  void comprehend(int i)
    {
    if (pwm_cnt[i] > pwm_off[i])
      pwm_state[i] = true;
    else
      pwm_state[i] = false;
    }
    
  void step()
    {
    for (int i = 0; i < USEPINS; i++)
      {
        pwm_cnt[i]--;
        if (pwm_cnt[i] == 0)
          pwm_cnt[i] = pwm_on[i] + pwm_off[i];

        comprehend(i);
      }
    }
    
  void transition(int i, uint16_t on, uint16_t off)
    {
    if (pwm_cnt[i] > pwm_off[i])
      {
      /* stay on for the shortest time possible without making this state duration (from now)
      less than the minimum of the previous pwm_on and the new pwm_on */
      uint16_t continue_for = min(pwm_cnt[i] - pwm_off[i], on);
      pwm_cnt[i] = off + continue_for;
      }
    else
      {
      pwm_cnt[i] = min(pwm_cnt[i], off);
      }
      
    pwm_on[i] = on;
    pwm_off[i] = off;
    comprehend(i);
    }
    
uint16_t pwm_off[USEPINS];
uint16_t pwm_on[USEPINS];
uint16_t pwm_cnt[USEPINS];
bool pwm_state[USEPINS];
  };
  
Blinker pwm;
Blinker bln;

#define BUF_SIZE 64
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
    
    // keep going until there definitely isn't enough data to read.
    while (used >= MSG_SIZE + 3)
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
        
        *((char*)(&_blink_on) + 1) = buf[7];
        *((char*)(&_blink_on)) = buf[8];
        *((char*)(&_blink_off) + 1) = buf[9];
        *((char*)(&_blink_off)) = buf[10];

        pwm.transition(ln, _pwm_on, _pwm_off);
        bln.transition(ln, _blink_on, _blink_off);

        consumed(MSG_SIZE + 3);
        }
      else
        {
        // throw away a byte to re-align
        consumed(1);
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
    if (pwm.pwm_state[i] && bln.pwm_state[i])
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
    digitalWrite(i + LOWPIN, LOW);
    }
  
  for (int i = 1; i <= 6; i++)
    {
    pwm.transition(i, 1, 12);
    bln.transition(i, 1000, 5000);
    }

  bln.pwm_cnt[6] = 1;

  bln.pwm_cnt[3] = 1001;
  bln.pwm_cnt[5] = 2001;
  bln.pwm_cnt[4] = 3001;
  bln.pwm_cnt[1] = 4001;
  bln.pwm_cnt[2] = 5001;

  for (int i = 1; i <= 6; i++)
    bln.comprehend(i);
  
  set_pins();
  }

void loop() {
  delay(1);

  cr.recv();
  pwm.step();
  bln.step();
  set_pins();
}
