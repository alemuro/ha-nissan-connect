import os
from dotenv import load_dotenv
from custom_components.nissan_connect.NissanConnect import NissanConnectClient

def main():
  username = os.getenv('NISSAN_USERNAME')
  password = os.getenv('NISSAN_PASSWORD')
  vin = os.getenv('VIN')

  nc = NissanConnectClient(username, password)
  # nc.login(username, password)
  print(nc.get_vehicles())
  # nc.get_location("vin")
  # nc.get_statistic_monthly("vin")
  # nc.get_cockpit("vin")

if __name__ == "__main__":
  load_dotenv()
  main()