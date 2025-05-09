from flask import current_app
import requests
from flask_babel import _


def translate(text, source_language, dest_language):
    # Taken as a mix between the Azure sample code:
    # https://portal.azure.com/#@chchrismullergmail.onmicrosoft.com/resource/subscriptions/68b27028-995e-46ae-8b61-4af497b033b5/resourceGroups/microblog-translator/providers/Microsoft.CognitiveServices/accounts/microblog-cm/overview
    # ...and the tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiv-ajax

    # Add your key and endpoint
    key = current_app.config["MS_TRANSLATOR_KEY"]
    if not key:
        return _("Error: the translation service is not configured.")

    endpoint = "https://api.cognitive.microsofttranslator.com"
    path = "/translate"
    constructed_url = endpoint + path

    params = {
        "api-version": "3.0",
        "from": source_language,
        "to": dest_language,
    }

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        # location required if you're using a multi-service or regional (not global) resource.
        "Ocp-Apim-Subscription-Region": current_app.config["MS_TRANSLATOR_LOCATION"],
    }

    # You can pass more than one object in body.
    body = [{"text": text}]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)

    if request.status_code != 200:
        return _("Error: the translation service failed.")
    response = request.json()
    return response[0]["translations"][0]["text"]
