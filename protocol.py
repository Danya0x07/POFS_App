from enum import Enum
from collections import namedtuple


class CommandType(Enum):
    SET_FLAP = 'G'
    SET_FILTER = 'F'
    WAIT = 'W'
    LOADING_MODE = 'L'
    SAVE_PROGRAM = 'P'
    EXECUTE_PROGRAM = 'E'
    RESET = 'R'
    CALIBRATE = 'C'
    SAVE_CALIBRATION = 'S'
    PRINT_CALIBRATION = 'H'
    EMERGENCY = 'Y'


class FlapStatus(Enum):
    CLOSED = '0'
    OPENED = '1'


class FilterState(Enum):
    NONE = '0'
    FS1 = '1'
    FS2 = '2'
    FS3 = '3'
    FS4 = '4'


class MotorID(Enum):
    S0 = '0'
    S1 = '1'
    S2 = '2'
    S3 = '3'
    S4 = '4'


LoopData = namedtuple('LoopData', 'beginMark endMark numRepetitions')
CalibrationData = namedtuple('CalibrationData', 'motorID openedAngle closedAngle')


class CommandTypeBadError(ValueError):
    pass


class CommandFormatError(ValueError):
    pass


class CommandValueError(ValueError):
    pass


class Command:
    def __init__(self, cmdtype: CommandType, arg=None):
        self.type = cmdtype
        self.arg = arg
    
    def __str__(self):
        string = str(self.type.value)
        if self.type == CommandType.SET_FLAP or self.type == CommandType.SET_FILTER:
            string += f',{str(self.arg.value)}'
        elif self.type == CommandType.WAIT:
            string += f',{str(self.arg)}'
        elif self.type == CommandType.SAVE_PROGRAM:
            loop_data = self.arg
            string += f',{loop_data.beginMark},{loop_data.endMark},{loop_data.numRepetitions}'
        elif self.type == CommandType.CALIBRATE:
            calib_data = self.arg
            string += f',{calib_data.motorID.value},{calib_data.openedAngle},{calib_data.closedAngle}'
        else:
            assert self.arg is None
        string += '\n'
        return string
    
    def __repr__(self):
        return str(self)
    
    @classmethod
    def from_str(cls, string):
        if string[-1] != '\n':
            raise CommandFormatError(string)
        string = string[:-1]
        parts = string.split(',')

        if parts[0] not in (e.value for e in CommandType):
            raise CommandTypeBadError(parts[0])
        
        cmdtype = CommandType(parts[0])
        cmdarg = None

        if cmdtype == CommandType.SAVE_PROGRAM:
            if len(parts) != 4:
                raise CommandFormatError(string)
            for part in parts[1:]:
                if not part.isnumeric():
                    raise CommandFormatError(f'{string}: {part}')
            args = list(map(int, parts[1:]))
            args = list(map(abs, args))
            loop_data = LoopData(beginMark=args[0], endMark=args[1], numRepetitions=args[2])
            if loop_data.beginMark > loop_data.endMark:
                raise CommandValueError(str(loop_data))
            cmdarg = loop_data
        elif cmdtype == CommandType.CALIBRATE:
            if len(parts) != 4:
                raise CommandFormatError(string)
            for part in parts[1:]:
                if not part.isnumeric():
                    raise CommandFormatError(f'{string}: {part}')
            if parts[1] not in (e.value for e in MotorID):
                raise CommandValueError(f'{string}: {parts[1]}')
            motor_id = MotorID(parts[1])
            opened_angle = abs(int(parts[2]))
            closed_angle = abs(int(parts[3]))
            if opened_angle > 180 or closed_angle > 180:
                raise CommandValueError(f'angles: {opened_angle}, {closed_angle}')
            calib_data = CalibrationData(motorID=motor_id, openedAngle=opened_angle, closedAngle=closed_angle)
            cmdarg = calib_data
        elif cmdtype == CommandType.SET_FLAP:
            cmdarg = parts[1]
            if cmdarg not in (e.value for e in FlapStatus):
                raise CommandValueError(f'{string}: {cmdarg}')
            cmdarg = FlapStatus(cmdarg)
        elif cmdtype == CommandType.SET_FILTER:
            cmdarg = parts[1]
            if cmdarg not in (e.value for e in FilterState):
                raise CommandValueError(f'{string}: {cmdarg}')
            cmdarg = FilterState(cmdarg)
        elif cmdtype == CommandType.WAIT:
            if not parts[1].isnumeric():
                raise CommandFormatError(parts[1])
            cmdarg = abs(int(parts[1]))
        else:
            if len(parts) != 1:
                raise CommandFormatError(string)
        
        return cls(cmdtype, cmdarg)


class ResponseType(Enum):
    PARSING_OK = 'o'
    PARSING_ERR = 'p'
    DISPATCH_ERR = 'd'
    EXEC_FINISH = 'f'
    CALIB_DATA = 'c'


class ResponseTypeBadError(ValueError):
    pass


class ResponseFormatError(ValueError):
    pass


class ResponseValueError(ValueError):
    pass


Response = namedtuple('Response', 'type data')


def parse_response(string):
    if string[-1] != '\n':
        raise ResponseFormatError(string)
    string = string[:-1]
    parts = string.split(',')

    if parts[0] not in (e.value for e in ResponseType):
        raise ResponseTypeBadError(string)
    
    type_ = ResponseType(parts[0])
    data = None

    if type_ == ResponseType.EXEC_FINISH:
        if len(parts) < 2:
            raise ResponseFormatError(str(parts))
        try:
            command = Command.from_str(','.join(parts[1:]) + '\n')
        except (CommandTypeBadError, CommandFormatError, CommandValueError) as e:
            raise ResponseValueError(f'{string}: {str(e)}')
        else:
            data = command
    elif type_ == ResponseType.CALIB_DATA:
        if len(parts) != 6:
            raise ResponseFormatError(str(parts))
        data = []
        for i in range(1, len(parts)):
            part = parts[i]
            
            subparts = part.split(' ')
            if len(subparts) != 2:
                raise ResponseFormatError(part)
            if not all(subpart.isnumeric() for subpart in subparts):
                raise ResponseValueError(part)
            motor_id = i - 1
            opened_angle = abs(int(subparts[0]))
            closed_angle = abs(int(subparts[1]))
            if opened_angle > 180 or closed_angle > 180:
                raise ResponseValueError(f'angles: {opened_angle}, {closed_angle}')
            calib_data = CalibrationData(motorID=motor_id, openedAngle=opened_angle, closedAngle=closed_angle)
            data.append(calib_data)
    
    return Response(type=type_, data=data)


if __name__ == '__main__':
    print(Command.from_str('G,0\n'), end='')
    print(Command.from_str('G,1\n'), end='')
    print(Command.from_str('F,0\n'), end='')
    print(Command.from_str('F,1\n'), end='')
    print(Command.from_str('F,2\n'), end='')
    print(Command.from_str('F,3\n'), end='')
    print(Command.from_str('F,4\n'), end='')
    print(Command.from_str('W,500000\n'), end='')
    print(Command.from_str('L\n'), end='')
    print(Command.from_str('E\n'), end='')
    print(Command.from_str('R\n'), end='')
    print(Command.from_str('S\n'), end='')
    print(Command.from_str('H\n'), end='')
    print(Command.from_str('Y\n'), end='')
    print(Command.from_str('P,3,6,5\n'), end='')
    print(Command.from_str('C,2,30,160\n'), end='')

    print(parse_response('o\n')._asdict())
    print(parse_response('p\n')._asdict())
    print(parse_response('d\n')._asdict())
    print(parse_response('f,F,3\n')._asdict())
    print(parse_response('f,C,2,3,160\n')._asdict())
    print(parse_response('c,0 180,0 180,10 170,20 170,30 150\n')._asdict())
    print('------------------\n')

    calibration = parse_response('c,0 180,0 180,10 170,20 170,30 150\n')._asdict()['data']
    calibration = [c._asdict() for c in calibration]
    print(calibration, '\n')

    print([CalibrationData(**c) for c in calibration], '\n')

    import json
    print(json.dumps([str(c) for c in [
        Command.from_str('G,0\n'),
        Command.from_str('F,2\n'),
        Command.from_str('W,500000\n'),
        Command.from_str('E\n'),
        Command.from_str('P,3,6,5\n')
    ]], indent=4))
