from hermes_python.hermes import Hermes
from hermes_python.ontology.tts import RegisterSoundMessage
from builtins import bytearray
import requests
from bs4 import BeautifulSoup

"""
Fehler mit import nur bei mir, da pip probleme hat.
"""

CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "fanrio"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
INTENT = "andreis:tellmeajocke"

class JokeTeller(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        # try:
        #     self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        # except :
        #     self.config = None

        # start listening to MQTT
        self.start_blocking()

    # --> Sub callback function
    def register_sound(self):
        with open('joke_drum', 'rb') as f:
            read_data = f.read()
        return RegisterSoundMessage("joke_drum", bytearray(read_data))



    # --> Sub callback function, one per intent
    def tellmejoke_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        

        if len(intent_message.slots) == 0:
            hermes.publish_continue_session( intent_message.session_id, 'Aus welcher Kategorie möchtest Du denn einen Witz hören?', "JokeTeller")
        elif intent_message.slots.joketype.first().value == 'egal':
            print('egal')
            page = requests.get("https://witze.at/zufallswitz")
        else:
            page = requests.get("https://witze.at/zufallswitz")
            print(intent_message.slots.joketype.first().value )


       
        soap = BeautifulSoup(page.content, 'html.parser')

        joke = soap.find('article').find('p').get_text() + ' ... [[sound:joke_drum]]'

        # action code goes here...
        print("[Received] intent: {}".format(intent_message.intent.intent_name))

        # if need to speak the execution result by tts
        hermes.publish_end_session(intent_message.site_id, joke, "JokeTeller")

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == INTENT:
            self.tellmejoke_callback(hermes, intent_message)

        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.register_sound(self.register_sound) \
             .subscribe_intent(INTENT, self.master_intent_callback)\
             .start()


if __name__ == "__main__":
    JokeTeller()
