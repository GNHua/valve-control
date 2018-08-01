#include <EEPROM.h>

#include "SoftReset.h"
#include "defaults.h"

#define MYPORT PORTB
#define SRCLR 8
#define dataPin 12
#define clockPin 9
#define latchPin 10
#define SRCLRBitLoc (SRCLR-8)
#define dataPinBitLoc (dataPin-8)
#define clockPinBitLoc (clockPin-8)
#define latchPinBitLoc (latchPin-8)

uint8_t regNum;    // number of registers used
char* currentState;        // keep track of shift register outputs
char* masks;
char* operations;         // 100 different operations max
uint8_t* phase;      // a list of phase describes the valve actuating sequence
uint8_t* beforePhase;
uint8_t* afterPhase;
volatile uint16_t currentPhaseIndex;        // current phase
uint8_t totalPhases;     // total number of phases
uint8_t totalBeforePhases;
uint8_t totalAfterPhases;
volatile uint32_t currentCycle = 0;
uint32_t totalCycles = 0;
bool longTimerEnabled;
uint32_t intervalMillis;
uint32_t previousMillis;

const uint8_t serStrLen = 28;   // max length of serial input string, baudrate 115200 for 2 ms
char serInStr[ serStrLen ];     // array that will hold the serial input string

void fastShiftOut(char* data, uint8_t length)
{
  // reset clock pin and latch pin
  MYPORT &= ~(1 << latchPinBitLoc);
  
  for(uint8_t i=0; i<length; i++) {
    for(int8_t j=7; j>=0; j--) {
      MYPORT &= ~(1 << clockPinBitLoc);
      
      // set data pin
      char dataBit = (data[i] >> j) & B00000001;
      // change the data pin
      MYPORT ^= (MYPORT ^ -(uint8_t)dataBit) & (1 << dataPinBitLoc);
      
      MYPORT |= (1 << clockPinBitLoc);
    }
  }
  
  // create a rising edge at latch pin
  MYPORT |= (1 << latchPinBitLoc);
}

void controlValves(char* data, char* currentState, char* mask, uint8_t length)
{
  for(uint8_t i=0; i<length; i++) {
    data[i] &= mask[i];
    currentState[i] &= ~mask[i];
    currentState[i] |= data[i];
  }
  
  fastShiftOut(currentState, length);
}

void start()
{
  // do nothing if it is already running
  if (((TIMSK1 >> OCIE1A) & B00000001) || longTimerEnabled) {
    return ;
  }

  runBeforeAfterPhase(beforePhase, totalBeforePhases);

  if (totalPhases) {
    currentPhaseIndex = 0;
    currentCycle = 0;
    if (intervalMillis <= 200) {
      float freq = 1000 / intervalMillis;
      noInterrupts();
      OCR1A = (uint16_t)(1.6e7 / 64 / freq);
      TCNT1 = 0;
      TIMSK1 |= (1 << OCIE1A);
      interrupts();
    } else {
      longTimerEnabled = true;
      previousMillis = millis();
    }
  }
}

/////////////////////////////////////////////////

// use hardware timer for interval equal to or below 200 ms
ISR(TIMER1_COMPA_vect)  // timer compare interrupt service routine
{
  controlValves(operations+phase[currentPhaseIndex]*regNum, currentState, masks+phase[currentPhaseIndex]*regNum, regNum);
  currentPhaseIndex++;

  if (currentPhaseIndex >= totalPhases) {
    currentPhaseIndex = 0;
    currentCycle++;
  }

  // disable timer compare interrupt if all cycles are done
  if (totalCycles != 0 && currentCycle >= totalCycles) {
    TIMSK1 &= ~(1 << OCIE1A);
    currentCycle = 0;
    runBeforeAfterPhase(afterPhase, totalAfterPhases);
  }
}

// use long timer for interval above 200 ms
void runLongTimer()
{
  uint32_t currentMillis = millis(); // grab current time
  if (longTimerEnabled && (uint32_t)(currentMillis - previousMillis) >= intervalMillis) {
    controlValves(operations+phase[currentPhaseIndex]*regNum, currentState, masks+phase[currentPhaseIndex]*regNum, regNum);
    currentPhaseIndex++;
    
    // save the "current" time
    previousMillis = currentMillis;
    
    if (currentPhaseIndex >= totalPhases) {
      currentPhaseIndex = 0;
      currentCycle++;
    }
    
    // disable long timer if all cycles are run
    if (totalCycles != 0 && currentCycle >= totalCycles) {
      longTimerEnabled = false;
      currentCycle = 0;
      runBeforeAfterPhase(afterPhase, totalAfterPhases);
    }
  }
}
/////////////////////////////////////////////////

void runBeforeAfterPhase(uint8_t* phase, uint8_t length)
{
  for(uint8_t i=0; i<length; i++) {
    controlValves(operations+phase[i]*regNum, currentState, masks+phase[i]*regNum, regNum);
    delay(intervalMillis);
  }
}

void stop()
{
  TIMSK1 &= ~(1 << OCIE1A);
  longTimerEnabled = false;
  runBeforeAfterPhase(afterPhase, totalAfterPhases);

  Serial.write((char*)(&currentCycle), sizeof(currentCycle));
  Serial.println();
  currentCycle = 0;
}

void clearShiftRegister()
{
  // do nothing if it is already running
  if (((TIMSK1 >> OCIE1A) & B00000001) || longTimerEnabled) {
    return ;
  }
  
  MYPORT &= ~(1 << latchPinBitLoc);
  MYPORT &= ~(1 << clockPinBitLoc);
  MYPORT &= ~(1 << SRCLRBitLoc);
  MYPORT |= (1 << clockPinBitLoc);
  MYPORT |= (1 << SRCLRBitLoc);
  MYPORT |= (1 << latchPinBitLoc);
  
  // reset currentState
  memset(currentState, 0, regNum);
}

void clear()
{
  // do nothing if it is already running
  if (((TIMSK1 >> OCIE1A) & B00000001) || longTimerEnabled) {
    return ;
  }
  
  clearShiftRegister();
  uint8_t operationNum = EEPROM.read(OPERATION_NUM_ADDR);
  uint8_t phaseNum = EEPROM.read(PHASE_NUM_ADDR);
  uint8_t beforePhaseNum = EEPROM.read(BEFORE_PHASE_NUM_ADDR);
  uint8_t afterPhaseNum = EEPROM.read(AFTER_PHASE_NUM_ADDR);
  memset(operations, 0, operationNum*regNum);
  memset(masks, 0, operationNum*regNum);
  memset(phase, 0, phaseNum);
  memset(beforePhase, 0, beforePhaseNum);
  memset(afterPhase, 0, afterPhaseNum);
  
  currentPhaseIndex = 0;        // current phase
  totalPhases = 0;              // total number of phases
  totalBeforePhases = 0;
  totalAfterPhases = 0;
  currentCycle = 0;
  totalCycles = 0;
}

void setup()
{
  uint8_t flag = EEPROM.read(VERSION_ADDR);
  if (flag != VERSION) {
    EEPROM.update(VERSION_ADDR, (byte)VERSION);
    EEPROM.update(REG_NUM_ADDR, (byte)REG_NUM);
    EEPROM.update(OPERATION_NUM_ADDR, (byte)OPERATION_NUM);
    EEPROM.update(PHASE_NUM_ADDR, (byte)(PHASE_NUM));
    EEPROM.update(BEFORE_PHASE_NUM_ADDR, (byte)(BEFORE_PHASE_NUM));
    EEPROM.update(AFTER_PHASE_NUM_ADDR, (byte)(AFTER_PHASE_NUM));
  }
  
  pinMode(SRCLR, OUTPUT);
  MYPORT |= (1 << SRCLRBitLoc);
  
  pinMode(dataPin,  OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(latchPin, OUTPUT);
  
  // initialize timer1 
  noInterrupts();     // disable all interrupts
  TCCR1A = 0;
  TCCR1B = 0;
  TCCR1B |= (1 << WGM12);                 // CTC mode
  TCCR1B |= (1 << CS11) | (1 << CS10);    // 64 prescaler 
  TIMSK1 &= ~(1 << OCIE1A);               // disable timer compare interrupt
  interrupts();                           // enable all interrupts
  
  longTimerEnabled = false;

  regNum = EEPROM.read(REG_NUM_ADDR);
  uint8_t operationNum = EEPROM.read(OPERATION_NUM_ADDR);
  uint8_t phaseNum = EEPROM.read(PHASE_NUM_ADDR);
  uint8_t beforePhaseNum = EEPROM.read(BEFORE_PHASE_NUM_ADDR);
  uint8_t afterPhaseNum = EEPROM.read(AFTER_PHASE_NUM_ADDR);
  currentState = (char*)malloc(regNum);
  masks = (char*)malloc(operationNum*regNum);
  operations = (char*)malloc(operationNum*regNum);
  phase = (uint8_t*)malloc(phaseNum); 
  beforePhase = (uint8_t*)malloc(beforePhaseNum);
  afterPhase = (uint8_t*)malloc(afterPhaseNum);
  clear();
  
  Serial.begin(115200);
  delay(2000); //To allow time for serial port to begin
}

void loop()
{
  GetSerialInput();
  runLongTimer();
}

void GetSerialInput() {
  uint8_t strSize = readSerialString();
  if (strSize) {
    switch (serInStr[0]) {
      case 0x00: // send the number of shift registers
      {
        // byte 1: regNum
        if (regNum != EEPROM.read(REG_NUM_ADDR)) {
          EEPROM.update(REG_NUM_ADDR, serInStr[1]);
          regNum = EEPROM.read(REG_NUM_ADDR);
          soft_restart();
        }
        break;
      }
      case 0x01: // send the total phase number in one cycle
        // byte 1: totalPhases
        // byte 2: totalBeforePhases
        // byte 3: totalAfterPhases
        memcpy(&totalPhases, serInStr+1, sizeof(totalPhases));
        memcpy(&totalBeforePhases, serInStr+2, sizeof(totalBeforePhases));
        memcpy(&totalAfterPhases, serInStr+3, sizeof(totalAfterPhases));
        break;
      case 0x02: // send data in `operations`
      {
        // byte 1: offset in `operations`
        // byte 2-(2+regNum): data
        // byte (2+regNum)-(2+regNum*2): mask
        uint8_t i = serInStr[1];
        memcpy(operations+i*regNum, serInStr+2, regNum);
        memcpy(masks+i*regNum, serInStr+2+regNum, regNum);
        break;
      }
      case 0x03: // send data in `phase`
      {
        // byte 1: offset in `phase`; byte 2-?: data
        uint8_t i = serInStr[1];
        memcpy(phase+i, serInStr+2, strSize-2);
        break;
      }
      case 0x04: // send data in `beforePhase`
      {
        // byte 1: offset in `beforePhase`; byte 2-?: data
        uint8_t i = serInStr[1];
        memcpy(beforePhase+i, serInStr+2, strSize-2);
        break;
      }
      case 0x05: // send data in `afterPhase`
      {
        // byte 1: offset in `afterPhase`; byte 2-?: data
        uint8_t i = serInStr[1];
        memcpy(afterPhase+i, serInStr+2, strSize-2);
        break;
      }
      case 0x06: // start
      {
        // byte 1-4: totalCycles; byte 5-8: intervalMillis
        memcpy(&totalCycles, serInStr+1, sizeof(totalCycles));
        memcpy(&intervalMillis, serInStr+1+sizeof(totalCycles), sizeof(intervalMillis));
        start();
        break;
      }
      case 0x07: // stop
        stop();
        break;
      case 0x08: // control valves
      {
        // byte 1-(1+regNum): valve controls 
        // byte (1+regNum)-(1+regNum*2): mask
        controlValves(serInStr+1, currentState, serInStr+1+regNum, regNum);
        break;
      }
      case 0x09: // clear shift register outputs
      {
        clearShiftRegister();
        break;
      }
      case 0x0A:
      {
        clear();
        break;
      }
      case 0x0B:
      {
        uint8_t addr = serInStr[1];
        for(uint8_t i=2; i<strSize; i++) {
          EEPROM.update(addr, serInStr[i]);
          addr++;
        }
        soft_restart();
        break;
      }
      case 0x0C:
      {
        soft_restart();
        break;
      }
      case 0x0D:
      {
        Serial.write(currentState, regNum);
        Serial.write((char*)(&totalCycles), sizeof(totalCycles));
        Serial.write((char*)(&currentCycle), sizeof(currentCycle));
        Serial.println();
        break;
      }
      case 0x0E:
      {
        for(uint8_t i=0; i<256; i++) {
          byte res = EEPROM.read(i);
          if (res == 0xFF) {
            break;
          } else {
            Serial.write(res);
          }
        }
        Serial.println();
        break;
      }
      default:
        break;
    }
  }
}

uint8_t readSerialString() {
  if(!Serial.available()) {
    return 0;
  }
  delay(2);  // wait a little for serial data
  memset( serInStr, 0, sizeof(serInStr) ); // set it all to zero (look up Arduino memset function)
  uint8_t i = 0;
  while(Serial.available() && i<serStrLen ) {
    serInStr[i] = Serial.read();   // FIXME: doesn't check buffer overrun
    i++;
  }
  Serial.write(serInStr, i);
  Serial.println();
  return i;  // return number of chars read
} //readSerialString


