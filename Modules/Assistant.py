import re
import os
import json
import random
from typing import Dict, Any, List, Tuple, Union
from .Functionalities import Functionalities
from Youtube_Downloader import say


def load_intents() -> Dict[str, Any]:
    """
    Load intents from a JSON file.

    This function reads the 'intents.json' file and parses its contents into a Python dictionary.

    Returns:
        Dict[str, Any]: A dictionary representing the JSON content.
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Json', 'intents.json')
    with open(file_path, 'r') as file:        
        return json.loads(file.read())

class Assistant:
    def __init__(self, intent: List[Dict[str, Any]], speak: bool, say_function, intent_mapping: Dict[str, callable] = None):
        """
        Initialize the Assistant.

        Args:
            intent (List[Dict[str, Any]]): List of intents loaded from the JSON file.
            speak (bool): Flag indicating whether the assistant should speak responses.
            say_function (callable): Function to handle speaking text.
            intent_mapping (Dict[str, callable], optional): Mapping of intent tags to their respective functions.
        """
        self.intent = intent
        self.intent_mapping = intent_mapping
        self.speak = speak
        self.say = say_function

        # Greet the user with a random response from the first intent
        self.say(self.speak, random.choice(self.intent[0]['responses']))

    def get_response(self, prompt: str) -> Tuple[str, Union[str, Tuple[str, str]], str]:
        """
        Generate a response based on the given prompt.

        This method analyzes the prompt to determine the best matching intent and returns an appropriate response.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, Union[str, Tuple[str, str]], str]: A tuple containing the response, any additional information, and the tag of the identified intent.
        """
        parameters = ''
        if '-p' in prompt:
            prompt, parameters = prompt.split('-p')

        split_msg = re.split(r'\s+|[,;?!.]\s*', prompt.lower())
        score_list = []
        for response in self.intent:
            response_score = 0
            required_score = 0
            required_words = response['required-words']
            if required_words:
                for word in split_msg:
                    if word in required_words:
                        required_score += 1
            if required_score == len(required_words):
                for word in split_msg:
                    if word in response['patterns']:
                        response_score += 1
            score_list.append(response_score + required_score)

        best_response = max(score_list)
        required_index = score_list.index(best_response)
        response_index = score_list.index(best_response)

        intent_clashes = [index for index, val in enumerate(score_list) if val == max(score_list)]
        sentence_for_clashes = [self.intent[val]["verb"] for val in intent_clashes]
        sentence = " or ".join(sentence_for_clashes)

        if len(intent_clashes) > 1 and len(intent_clashes) < 3:
            sentence = f"Do you want {sentence}"
            return sentence, ("", sentence), ""
        if prompt == "":
            return "", '', 'empty'
        if best_response != 0:
            add_ons = self.intents_function_mapping(self.intent[required_index]["tag"], f'{prompt} -p {parameters}')
            return random.choice(self.intent[response_index]['responses']), add_ons, self.intent[required_index]["tag"]

        return random.choice(self.intent[-1]['responses']), '', 'unknown'

    def intents_function_mapping(self, tag: str, *args, **kwargs) -> str:
        """
        Map the given tag to its corresponding function and execute it.

        Args:
            tag (str): The intent tag.
            *args: Additional positional arguments for the function.
            **kwargs: Additional keyword arguments for the function.

        Returns:
            str: The result of the function execution or an error message.
        """
        for mapping in self.intent_mapping:
            if tag == mapping:
                try:
                    return self.intent_mapping[mapping](*args, **kwargs)
                except Exception as e:
                    return f"Sorry, your prompt is giving me an error: {e}", f"Sorry, your prompt is giving me an error: {e}"

    def chatbot(self):
        """
        Run the chatbot, interacting with the user through the console.

        This method continually prompts the user for input, processes it, and provides responses until the user exits.
        """
        while True:
            prompt = input('\n\033[92mYou:\033[0m ')
            if prompt.lower() == 'x':
                break
            else:
                response, add_ons, tag = self.get_response(prompt)
                print_add_ons, say_add_ons = add_ons or ("", "")
                print('\033[94mBot:\033[0m ', "\033[93m" + response + print_add_ons + "\033[0m")
                self.say(self.speak, response + say_add_ons)


if __name__ == '__main__':
    speak = input('\nWould You Like Me To Interact With You With Speech As Well? (Y/n) ').lower()
    speak = speak == 'y'

    functionality = Functionalities(speak, say)

    intent = load_intents()

    intent_function_mappings = {
        "open-cmd": functionality.open_cmd,
        "search-google": functionality.search_google,
        "play-youtube-video": functionality.play_video,
        "wikipedia-search": functionality.wikipedia_search,
        "time-telling": functionality.tell_time,
        "summarizer": functionality.summarize_text,
        "mini-youtube": functionality.youtube,
        "file-chat": functionality.chat_with_files,
        "repeat": functionality.repeat
    }

    Assistant(intent, speak, say, intent_mapping=intent_function_mappings).chatbot()
