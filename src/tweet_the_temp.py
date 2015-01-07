import read_temp

model = 11
pin = 7

while True:
  read_temp model pin
  sleep(100)
