import serial
import time


class ValveControlBase:

    def __init__(self, port):
        self.port = port
        self.settings = self.getEEPROMSettings()

    def reset_input_buffer(self):
        print('reset input buffer')

    def reset_output_buffer(self):
        print('reset output buffer')

    def close(self):
        print('close')

    def send(self, command):
        print(command)

        if command == b'\x07':
            return b'\x01\x00\x00\x00\r\b'
        elif command == b'\x0E':
            return b'\x00\x04\x64\xC8\x0A\x0A\r\n'

    def setRegNum(self, n):
        """Set number of 8-bit registers. 
        This will restart arduino.
        
        :param int n: number of registers
        """
        self.send(b'\x00' + int(n).to_bytes(1, 'little'))

    def setTotalPhases(self, totalPhases, totalBeforePhases, totalAfterPhases):
        """Set total phases. 

        :param int totalPhases: total number of phases
        :param int totalBeforePhases: total number of phases before cycles
        :param int totalAfterPhases: total number of phases after cycles
        """
        byte1 = int(totalPhases).to_bytes(1, 'little')
        byte2 = int(totalBeforePhases).to_bytes(1, 'little')
        byte3 = int(totalAfterPhases).to_bytes(1, 'little')
        self.send(b'\x01' + byte1 + byte2 + byte3)

    def setOperation(self, index, on=(), off=()):
        """Set operation data.
        
        :param int index: phase index in the `state` array in Arduino code
        :param list on: a list of valve numbers (int) to turn on
        :param list off: a list of valve number (int) to turn off
        """
        onBytes = 0
        for i in on:
            onBytes |= (1 << (i-1))
        offBytes = 0
        for i in off:
            offBytes |= (1 << (i-1))
        maskBytes = onBytes | offBytes
        
        data = onBytes.to_bytes(self.settings['REG_NUM'], 'big')
        mask = maskBytes.to_bytes(self.settings['REG_NUM'], 'big')
        self.send(b'\x02' + index.to_bytes(1, 'little') + data + mask)

    def setPhase(self, offset, operationIndex):
        """Copy data to ``phase` array, starting from ``offset``.
        
        :param int offset: offset in the ``phase`` array
        :param list operationIndex: a list of operation index (int)
        """
        data = b''
        for i in operationIndex:
            data += i.to_bytes(1, 'little')
        self.send(b'\x03' + offset.to_bytes(1, 'little') + data)

    def setBeforePhase(self, offset, operationIndex):
        """Copy data to ``phase` array, starting from ``offset``.
        
        :param int offset: offset in the ``beforePhase`` array
        :param list operationIndex: a list of operation index (int)
        """
        data = b''
        for i in operationIndex:
            data += i.to_bytes(1, 'little')
        self.send(b'\x04' + offset.to_bytes(1, 'little') + data)

    def setAfterPhase(self, offset, operationIndex):
        """Copy data to ``phase` array, starting from ``offset``.
        
        :param int offset: offset in the ``afterPhase`` array
        :param list operationIndex: a list of operation index (int)
        """
        data = b''
        for i in operationIndex:
            data += i.to_bytes(1, 'little')
        self.send(b'\x05' + offset.to_bytes(1, 'little') + data)

    def start(self, cycles, phaseIntervalMillis):
        """Start cycles.
        
        :param int cycles: number of cycles to run
        :param int phaseIntervalMillis: the interval in milliseconds between 
                                        different phases in a cycle. NOTE: This 
                                        is the cycle period. 
        """
        cycles = cycles.to_bytes(4, 'little')
        phaseIntervalMillis = phaseIntervalMillis.to_bytes(4, 'little')
        self.send(b'\x06' + cycles + phaseIntervalMillis)

    def stop(self):
        """Stop running cycles"""
        res = self.send(b'\x07')[:4]
        cycleCompleted = int.from_bytes(res, 'little')
        return cycleCompleted

    def controlValves(self, on=(), off=()):
        """Control vlaves manually.
        
        :param list on: a list of valve numbers (int) to turn on
        :param list off: a list of valve numbers (int) to turn off
        """
        onBytes = 0
        for i in on:
            onBytes |= (1 << (i-1))
        offBytes = 0
        for i in off:
            offBytes |= (1 << (i-1))
        maskBytes = onBytes | offBytes
        
        data = onBytes.to_bytes(self.settings['REG_NUM'], 'big')
        mask = maskBytes.to_bytes(self.settings['REG_NUM'], 'big')
        self.send(b'\x08' + data + mask)

    def clearShiftRegister(self):
        """Reset shift register outputs"""
        self.send(b'\x09')

    def clear(self):
        """Reset shift register outputs and all parameters"""
        self.send(b'\x0A')

    def updateEEPROM(self, addr, data):
        """Set the parameters in EEPROM. 
        
        :param int addr: address in EEPROM, range 0-255
        :param data bytes: the data to write onto EEPROM
        """
        self.send(b'\x0B' + int(addr).to_bytes(1, 'little') + data)

    def restart(self):
        """Restart Arduino. 
        It does not do anything to the peripheral circuits. 
        """
        self.send(b'\x0C')

    def getEEPROMSettings(self):
        """Get the settings in EEPROM.
        
        There are 6 bytes in total. 
        Byte 0: EEPROM_RESET_FLAG
        Byte 1: REG_NUM
        Byte 2: STATE_NUM
        Byte 3: PHASE_NUM
        Byte 4: BEFORE_PHASE_NUM
        Byte 5: AFTER_PHASE_NUM
        """
        res = self.send(b'\x0E')[:-2]
        return {
            'EEPROM_RESET_FLAG': res[0], 
            'REG_NUM': res[1], 
            'STATE_NUM': res[2], 
            'PHASE_NUM': res[3],
            'BEFORE_PHASE_NUM': res[4],
            'AFTER_PHASE_NUM': res[5]
        }


class ValveControlDevice(ValveControlBase):

    def controlSingleValve(self, i, on):
        if on:
            self.controlValves(on=(i,))
        else:
            self.controlValves(off=(i,))

    def makeProgrammableCycle(self, file):
        pc = ProgrammableCycle(file)
        if pc.wrongLines:
            return pc.wrongLines
        self.programmableCycle = pc

    def uploadProgram(self):
        self.setTotalPhases(len(self.programmableCycle.phase),
                            len(self.programmableCycle.beforePhase),
                            len(self.programmableCycle.afterPhase))

        for i, op in enumerate(self.programmableCycle.operations):
            valveOn, valveOff = op
            self.setOperation(index=i, on=valveOn, off=valveOff)
            
        # reshape the phase list to a 2-d list, each row 10 items
        rowSize = 10
        temp = [self.programmableCycle.phase[i:i+rowSize] 
            for i in range(0, len(self.programmableCycle.phase), rowSize)]
        for i, phase in enumerate(temp):
            self.setPhase(i*rowSize, phase)

        temp = [self.programmableCycle.beforePhase[i:i+rowSize] 
            for i in range(0, len(self.programmableCycle.beforePhase), rowSize)]
        for i, phase in enumerate(temp):
            self.setBeforePhase(i*rowSize, phase)

        temp = [self.programmableCycle.afterPhase[i:i+rowSize] 
            for i in range(0, len(self.programmableCycle.afterPhase), rowSize)]
        for i, phase in enumerate(temp):
            self.setAfterPhase(i*rowSize, phase)

    def loadToggleValveProgram(self, valve):
        self.programmableCycle = ToggleValveCycle(valve)
        self.uploadProgram()

    def load5PhasePumpProgram(self, inputValve, DC, outputValve):
        self.programmableCycle = FivePhasePumpCycle(inputValve, DC, outputValve)
        self.uploadProgram()


class ProgrammableCycle:

    def __init__(self, file):
        self.operations = list()
        self.phase = list()
        self.beforePhase = list()
        self.afterPhase = list()
        
        self.parseFile(file)

    def parseFile(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()
            
        self.wrongLines = list()
        mode = 0
        for i, l in enumerate(lines):
            if l.isspace():
                continue
            l = l.strip().upper()
            
            if l == 'CYCLE':
                mode = 0
            elif l =='BEFORE':
                mode = 1
            elif l == 'AFTER':
                mode = 2
            else:
                try:
                    self.parseLine(l, mode)
                except ValueError:
                    self.wrongLines.append(i+1)

    def parseLine(self, line, mode):
        valveOn = list()
        valveOff = list()
        for c in line.split(','):
            c = c.strip()
            if c.startswith('ON'):
                valveOn += list(map(int, c.split()[1:]))
            elif c.startswith('OFF'):
                valveOff += list(map(int, c.split()[1:]))
            else:
                raise ValueError
        valveOn = tuple(sorted(list(set(valveOn))))
        valveOff = tuple(sorted(list(set(valveOff))))
        operation = (valveOn, valveOff)

        if operation not in self.operations:
            self.operations.append(operation)
        if mode == 0:
            self.phase.append(self.operations.index(operation))
        elif mode == 1:
            self.beforePhase.append(self.operations.index(operation))
        elif mode == 2:
            self.afterPhase.append(self.operations.index(operation))


class ToggleValveCycle:

    def __init__(self, valve):
        self.operations = [((valve,), ()), ((), (valve,))]
        self.phase = [0, 1]
        self.beforePhase = list()
        self.afterPhase = list()


class FivePhasePumpCycle:

    def __init__(self, inputValve, DC, outputValve):
        self.operations = [
            ((outputValve,), ()), 
            ((DC,), ()), 
            ((inputValve,), ()), 
            ((), (inputValve, DC)), 
            ((), (outputValve,))
        ]
        self.phase = [3, 2, 4, 1, 0]
        self.beforePhase = [0, 1, 2]
        self.afterPhase = [0]
