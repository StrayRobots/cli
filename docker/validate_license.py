import requests
import json
import os

def validate_license():
  validation = {}
  try:
    validation = requests.post(
      "https://api.keygen.sh/v1/accounts/strayrobots-io/licenses/actions/validate-key",
      headers={
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
      },
      data=json.dumps({
        "meta": {
          "key": os.environ['STRAY_LICENSE_KEY']
        }
      })
    ).json()
  finally:
    if not validation.get("meta", {}).get("valid", False):
      print("Could not validate license key, please contact hello@strayrobots.io for help.")
      exit(1)

  

if __name__ == "__main__":
    validate_license()