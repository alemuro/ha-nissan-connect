import enum
import datetime
import logging
import requests
from dateutil.relativedelta import relativedelta

_LOGGER = logging.getLogger(__name__)

API_VERSION = "protocol=1.0,resource=2.1"
SRP_KEY = "D5AF0E14718E662D12DBB4FE42304DF5A8E48359E22261138B40AA16CC85C76A11B43200A1EECB3C9546A262D1FBD51ACE6FCDE558C00665BBF93FF86B9F8F76AA7A53CA74F5B4DFF9A4B847295E7D82450A2078B5A28814A7A07F8BBDD34F8EEB42B0E70499087A242AA2C5BA9513C8F9D35A81B33A121EEF0A71F3F9071CCD"

class Period(enum.Enum):
    DAILY = 0
    MONTHLY = 1
    YEARLY = 2

class NissanConnectClient:
  def __init__(self, username, password):
    self._user_id = None
    self._username = username
    self._password = password
    self._bearer_token = None
    self._settings = {
      "EU": {
        "client_id": "a-ncb-prod-android",
        "client_secret": "0sAcrtwvwEXXZp5nzQhPexSRhxUVKa0d76F4uqDvxvvKFHXpo4myoJwUuV4vuNqC",
        "scope": "openid profile vehicles",
        "auth_base_url": "https://prod.eu2.auth.kamereon.org/kauth/",
        "realm": "a-ncb-prod",
        "redirect_uri": "org.kamereon.service.nci:/oauth2redirect",
        "car_adapter_base_url": "https://alliance-platform-caradapter-prod.apps.eu2.kamereon.io/car-adapter/",
        "user_adapter_base_url": "https://alliance-platform-usersadapter-prod.apps.eu2.kamereon.io/user-adapter/",
        "user_base_url": "https://nci-bff-web-prod.apps.eu2.kamereon.io/bff-web/"
      }
    }
    self._response_vehicles = None
    self._response_location = {}
    self._response_cockpit = {}
    self._response_trips = {}

  def refresh_data(self):
    self._refresh_api_token()
    user_id = self._get_user_id()

    # Get cars
    url_cars = f"{self._settings['EU']['user_base_url']}v5/users/{user_id}/cars"
    response_vehicles = requests.get(
      url_cars,
      headers={
        "Authorization": f"Bearer {self._bearer_token}"
      }
    )

    if response_vehicles.status_code == 401:
      self._bearer_token = None
      return

    self._response_vehicles = response_vehicles.json()["data"]


    for vehicle in self._response_vehicles:
      vin = vehicle["vin"]

      url_location = f"{self._settings['EU']['car_adapter_base_url']}v1/cars/{vin}/location"
      url_cockpit = f"{self._settings['EU']['car_adapter_base_url']}v1/cars/{vin}/cockpit"
      url_trips = f"{self._settings['EU']['car_adapter_base_url']}v1/cars/{vin}/trip-history?type=0&start={datetime.date.today()}&end={datetime.date.today()}"

      response_location = requests.get(
        url_location,
        headers={
          "Authorization": f"Bearer {self._bearer_token}"
        }
      )
      self._response_location[vin] = response_location.json()["data"]

      response_cockpit = requests.get(
        url_cockpit,
        headers={
          "Authorization": f"Bearer {self._bearer_token}"
        }
      )
      self._response_cockpit[vin] = response_cockpit.json()["data"]

      response_trips = requests.get(
        url_trips,
        headers={
          "Authorization": f"Bearer {self._bearer_token}"
        }
      )
      self._response_trips[vin] = response_trips.json()["data"]

  def get_vehicles(self):
    return self._response_vehicles

  def get_location(self, vin):
    return self._response_location[vin]
  
  def get_stats(self, vin):
    cockpit = self._response_cockpit[vin]["attributes"]
    trips = self._response_trips[vin]["attributes"]["summaries"][0] if len(self._response_trips[vin]["attributes"]["summaries"]) else {}
  
    return {
      "totalMileage": cockpit["totalMileage"],
      "fuelAutonomy": cockpit["fuelAutonomy"],
      "tripsNumberToday": trips["tripsNumber"] if "tripsNumber" in trips else 0, 
      "tripsDistanceToday": trips["distance"] if "distance" in trips else 0,
      "tripsDurationToday": trips["duration"] if "duration" in trips else 0,
      "tripsConsumedFuel": trips["consumedFuel"] if "consumedFuel" in trips else 0,
      "tripsCo2Saving": trips["co2Saving"] if "co2Saving" in trips else 0,
    }

  def _get_user_id(self):
    if self._user_id:
      return self._user_id

    url = f"{self._settings['EU']['user_adapter_base_url']}v1/users/current"
    req = requests.get(
      url,
      headers={
        "Authorization": f"Bearer {self._bearer_token}"
      }
    )
    req.raise_for_status()
    return req.json()["userId"]

  def _getAccessToken(self, realm, authorisationCode):
    expectedAccessTokenResponseUrl = f"{self._settings['EU']['auth_base_url']}oauth2{realm}/access_token?code={authorisationCode}&client_id={self._settings['EU']['client_id']}&client_secret={self._settings['EU']['client_secret']}&redirect_uri={self._settings['EU']['redirect_uri']}&grant_type=authorization_code"
    expectedAccessTokenResponse = requests.post(
      expectedAccessTokenResponseUrl,
      headers={
        "Content-Type": "application/x-www-form-urlencoded"
      }
    )
    expectedAccessTokenResponse.raise_for_status()
    expectedAccessTokenResponseBody = expectedAccessTokenResponse.json()
    return expectedAccessTokenResponseBody["access_token"]

  def _getAuthorisationCode(self, realm, authCookie):
    authorizeUrl = f"{self._settings['EU']['auth_base_url']}oauth2{realm}/authorize?client_id={self._settings['EU']['client_id']}&redirect_uri={self._settings['EU']['redirect_uri']}&response_type=code&scope={self._settings['EU']['scope']}&nonce=sdfdsfez&state=af0ifjsldkj"
    authorisationCode = None

    try:
      req = requests.get(
        authorizeUrl,
        headers={
          "Cookie": f'i18next=en-UK; amlbcookie=05; kauthSession="{authCookie}"'
        },
        allow_redirects=False
      )
      req.raise_for_status()
      authorisationCode = req.headers["Location"].split("=")[1].split("&")[0]
    except Exception as e:
      _LOGGER.debug(f"Error getting authorisation code: {e}")

    if not authorisationCode:
      raise Exception("Code was not returned in redirect from authorize request")
    return authorisationCode

  def _getAuthCookieAndRealm(self, authenticateUrl, API_VERSION, authId, username, password):
    maxAttemps0n401 = 10 

    for attempt in range(1, maxAttemps0n401):
      _LOGGER.debug(f"Auth cookie attempt {attempt}")
      tokenIdResponse = None
      try:
        tokenIdResponse = requests.post(
          authenticateUrl, 
          headers={
            "Accept-Api-Version": API_VERSION,
            "X-Username": "anonymous",
            "X-Password": "anonymous",
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          json={
            "authId": authId,
            "template": "",
            "stage": "LDAP1",
            "header": "Sign in",
            "callbacks": [
              {
                "type": "NameCallback",
                "output": [
                  { "name": "prompt", "value": "User Name:" }
                ],
                "input": [
                  { "name": "IDToken1", "value": username }
                ]
              },
              {
                "type": "PasswordCallback",
                "output": [
                  { "name": "prompt", "value": "Password:" }
                ],
                "input": [
                  { "name": "IDToken2", "value": password }
                ]
              }
            ]
          }
        )
      except Exception as e:
        tokenIdResponse = e.response

      if tokenIdResponse.status_code == 200:
        tokenIdResponseBody = tokenIdResponse.json()
        _LOGGER.debug(tokenIdResponse.json())
        return tokenIdResponseBody["tokenId"], tokenIdResponseBody["realm"]
      
      elif tokenIdResponse.status_code == 401 and "Session has timed out" in tokenIdResponse.text and attempt != maxAttemps0n401:
        continue
      else:
        raise Exception(f"Auth returned with status {tokenIdResponse.status_code}")

  def _getAuthId(self, authenticateUrl, API_VERSION):
    req = requests.post(
      authenticateUrl, 
      headers={
        "Accept-Api-Version": API_VERSION,
        "X-Username": "anonymous",
        "X-Password": "anonymous",
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    )
    req.raise_for_status()
    return req.json()["authId"]

  def _refresh_api_token(self):
    if self._bearer_token:
      return

    _LOGGER.debug(f"Logging in with username {self._username} and password {self._password}")
    _LOGGER.debug(f"Using settings {self._settings}")

    authenticateUrl = f"{self._settings['EU']['auth_base_url']}json/realms/root/realms/{self._settings['EU']['realm']}/authenticate"
    _LOGGER.debug(f"authenticateUrl: {authenticateUrl}")

    authId = self._getAuthId(authenticateUrl, API_VERSION)

    authCookie, realm = self._getAuthCookieAndRealm(authenticateUrl, API_VERSION, authId, self._username, self._password)
    _LOGGER.debug(f"authCookie: {authCookie}")
    _LOGGER.debug(f"realm: {realm}")

    authorisationCode = self._getAuthorisationCode(realm, authCookie)
    _LOGGER.debug(f"authorisationCode: {authorisationCode}")

    accessToken = self._getAccessToken(realm, authorisationCode)
    _LOGGER.debug(f"accessToken: {accessToken}")
    self._bearer_token = accessToken
