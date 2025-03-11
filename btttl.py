import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS={"BT_1":21, "BT_2": 26, "BT_3": 20, "BT_4": 19}
RLS={"RELAY_1":16, "RELAY_2": 12, "LED":13}


def pull_up_bts():
	for pin in BTS.values():
		GPIO.setup (pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	for pin in RLS.values():
		GPIO.setup(pin, GPIO.OUT)


LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def lcd_init():
	for pin in LCD_PINS.values():
		GPIO.setup(pin, GPIO.OUT)
	for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
		lcd_byte(byte, LCD_CMD)


def lcd_clear():
	lcd_byte(0x01, LCD_CMD)


def lcd_byte(bits, mode):
	GPIO.output(LCD_PINS['RS'], mode)
	for bit_num in range(4):
		GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << (4 + bit_num)) != 0)

	time.sleep(E_DELAY)
	GPIO.output(LCD_PINS['E'], True)
	time.sleep(E_PULSE)
	GPIO.output(LCD_PINS['E'], False)
	time.sleep(E_DELAY)

	for bit_num in range(4):
		GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << bit_num) != 0)

	time.sleep(E_DELAY)
	GPIO.output(LCD_PINS['E'], True)
	time.sleep(E_PULSE)
	GPIO.output(LCD_PINS['E'], False)
	time.sleep(E_DELAY)


def	lcd_display_string(message, line):
	lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
	for char in message:
		lcd_byte(ord(char), LCD_CHR)


def on_button1_pressed():
    start_time = time.time()
    global password
	
    while GPIO.input(BTS['BT_1']) == GPIO.LOW:  # Giữ vòng lặp khi nút đang bấm
        elapsed_time = time.time() - start_time
        if elapsed_time >= 0.5:
            for i in range(1, 10):
                lcd_display_string(f"{i}", 1)
                time.sleep(0.25)
                
                if GPIO.input(BTS['BT_1']) == GPIO.HIGH:
                    lcd_display_string(f"{i}", 1)
                    password += str(i)
                    time.sleep(0.5)
                    break		
            
            return  

def check_password(password):
	if password == "999":
		GPIO.output(RLS["RELAY_1"], GPIO.HIGH)
		lcd_clear()
		lcd_display_string("thanh cong", 1)
		time.sleep(1)
		return 0
	else:
		GPIO.output(RLS["RELAY_2"], GPIO.HIGH)
		lcd_clear()
		lcd_display_string("khong thanh cong", 1)
		time.sleep(1)
		return 1


def disable_button():
    GPIO.setup(BTS['BT_1'], GPIO.OUT)
    GPIO.output(BTS['BT_1'], GPIO.HIGH)  

def main():
	lcd_init()
	pull_up_bts()
	GPIO.output(LCD_PINS['BL'], True)
	global password
	password = ""
	check = 0
	while True:
		if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
			on_button1_pressed()
			time.sleep(0.25)
		if len(password) == 3:
			lcd_display_string("***", 1)
			check += check_password(password)
			password = ""
			lcd_clear()
			
		if check == 2:
			lcd_clear()
			lcd_display_string("!sai 2 lan!", 1)
			time.sleep(1)
			disable_button()


try:
	main()
except KeyboardInterrupt:
	lcd_clear()
	GPIO.cleanup()