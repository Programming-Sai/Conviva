import os
import time
import fitz
import random
import datetime
import subprocess
from typing import Tuple
from File_Chat import FileChat
from dotenv import load_dotenv
from transformers import pipeline
from Youtube_Downloader import YoutubeDownloader, say
from concurrent.futures import ThreadPoolExecutor



class Functionalities:
    def __init__(self, speak: bool, say_function):
        """
        Initialize the Functionalities class.

        Args:
            speak (bool): Flag indicating whether to use speech.
            say_function (callable): Function to handle speaking text.
        """
        self.speak = speak
        self.say = say_function

    def open_cmd(self, prompt: str) -> Tuple[str, str]:
        """
        Open the command terminal.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: An empty string and a message indicating the terminal was opened.
        """
        subprocess.run(["open", "-a", "Terminal"])
        return "", f"{random.choice(['Terminal', 'Command Prompt', 'Cmd'])} Opened"

    def search_google(self, prompt: str) -> Tuple[str, str]:
        """
        Search for a query on Google.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: Empty strings if successful, otherwise error messages.
        """
        try:
            query = prompt[(prompt.index("-p"))+3:] if "-p" in prompt else "Google"
            import pywhatkit as kit
            kit.search(query)
            return "", ''
        except Exception as e:
            time.sleep(2)
            return random.choice([
                " Sorry There Seems To Be Problem",
                " I Think You Do Not Have Internet Connection At The Moment"
            ]), random.choice([
                " Sorry There Seems To Be Problem",
                " I Think You Do Not Have Internet Connection At The Moment"
            ])

    def play_video(self, prompt: str) -> Tuple[str, str]:
        """
        Play a video on YouTube.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: Empty strings if successful, otherwise error messages.
        """
        try:
            video = prompt[(prompt.index("-p"))+3:] if "-p" in prompt else "Youtube"
            import pywhatkit as kit
            kit.playonyt(video), f'Playing {video}'
            return '', ''
        except Exception as e:
            time.sleep(2)
            return random.choice([
                " Sorry There Seems To Be Problem",
                " I Think You Do Not Have Internet Connection At The Moment"
            ]), random.choice([
                " Sorry There Seems To Be Problem",
                " I Think You Do Not Have Internet Connection At The Moment"
            ])

    def wikipedia_search(self, prompt: str) -> Tuple[str, str]:
        """
        Perform a search on Wikipedia.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: The search result and the same result for speaking, or error messages.
        """
        query = prompt[(prompt.index("-p"))+3:] if "-p" in prompt else "Wikipedia"
        try:
            sentences = int(query[0])
        except ValueError:
            sentences = 2

        try:
            import wikipedia
            result = wikipedia.summary(query, sentences=sentences)
            return result, result
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError, Exception) as e:
            time.sleep(2)
            return random.choice([
                f" Sorry There Seems To Be Problem",
                f" I Think You Do Not Have Internet Connection At The Moment"
            ]), random.choice([
                " Sorry There Seems To Be Problem",
                " I Think You Do Not Have Internet Connection At The Moment"
            ])

    def tell_time(self, prompt: str) -> Tuple[str, str]:
        """
        Tell the current time and/or date.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: The time and/or date for printing and speaking.
        """
        current_date_time = datetime.datetime.now()
        if 'time' in prompt and 'date' in prompt:
            ctime = current_date_time.strftime("%I:%M %p")
            ctime = str(int(ctime[:2])) + ctime[2:]
            ctime_say = ctime.replace(':', ' ')
            print_result = "\nToday's Date and Time is " + current_date_time.strftime(" %dth of %B %Y") + " " + ctime
            say_result = "\nToday's Date and Time is " + current_date_time.strftime(" %dth of %B %Y") + " " + ctime_say
            return print_result, say_result

        elif 'time' in prompt:
            ctime = current_date_time.strftime("%I:%M %p")
            ctime = str(int(ctime[:2])) + ctime[2:]
            ctime_say = ctime.replace(':', ' ')

            return "\nThe Time is " + ctime, "\nThe Time is " + ctime_say
        elif 'date' in prompt:
            cdate = current_date_time.strftime(" the %dth of %B %Y")
            return "\nToday's Date is " + cdate, "\nToday's Date is " + cdate

    def summarize_text(self, prompt: str) -> Tuple[str, str]:
        """
        Summarize the given text.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: The summarized text for printing and speaking, or error messages.
        """
        os.environ['TOKENIZERS_PARALLELISM'] = False
        model_name = "sshleifer/distilbart-cnn-12-6"
        model_revision = "a4f8f3e"
        summarisation = pipeline("summarization", model=model_name, revision=model_revision)

        article = prompt[(prompt.index("-p"))+3:] if "-p" in prompt else "What Should I Summarize? \033[1m(Add flag `-p` to specify)"
        try:
            summary = summarisation(article, max_length=250, min_length=100, do_sample=False)[0]['summary_text']
            return summary, summary
        except Exception as e:
            time.sleep(2)
            return random.choice([
                f" Sorry There Seems To Be Problem",
                f" I Think You Do Not Have Internet Connection At The Moment"
            ]), random.choice([
                f" Sorry There Seems To Be Problem",
                f" I Think You Do Not Have Internet Connection At The Moment"
            ])

    def chat_with_files(self, prompt: str) -> Tuple[str, str]:
        """
        Chat with files.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: The result of the file chat process for printing and speaking.
        """
        instruction = {"query": (prompt[(prompt.index("-p"))+3:] if "-p" in prompt else "Youtube")}
        try:
            result = FileChat().process_response(instruction)
            return result, result
        except:
            return '', ""

    def youtube(self, prompt: str) -> Tuple[str, str]:
        """
        Use the YouTube downloader functionality.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: Empty strings.
        """
        YoutubeDownloader(self.speak, self.say).mini_youtube()
        return "", ""

    def repeat(self, prompt: str) -> Tuple[str, str]:
        """
        Repeat the given text.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: Empty strings for printing and speaking.
        """
        self.speak = True
        self.say(self.speak, prompt[(prompt.index("-p"))+3:] if '-p' in prompt else 'What Exactly do i repeat for you')
        self.speak = False
        return '', ''

    def text_summary(self, file_path: str = None) -> Tuple[str, str]:
        """
        Summarize the text from a file.

        Args:
            file_path (str, optional): The path to the file to summarize. Defaults to 'summary_input_text.txt'.

        Returns:
            Tuple[str, str]: The summarized text for printing and speaking, or error messages.
        """
        def summarize_chunk(chunk: str) -> str:
            try:
                return summarisation(chunk, max_length=max(int(len(chunk) / 4), 50), min_length=int(len(chunk)/4), do_sample=False)[0]['summary_text']
            except Exception as e:
                return random.choice([
                    f"Sorry, there seems to be a problem",
                    f"I think you do not have an internet connection at the moment"
                ])

        def extract_text_from_pdf(pdf_path: str) -> str:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            return text

        # Read text from file
        if file_path is None:
            file_path = 'summary_input_text.txt'
        if file_path.lower().endswith('.pdf'):
            try:
                article = extract_text_from_pdf(file_path)
            except Exception as e:
                return f"Failed to extract text from PDF: {str(e)}", ""
        else:
            try:
                with open(file_path, 'r') as sit:
                    article = sit.read()
            except Exception as e:
                return f"Failed to read text file: {str(e)}", ""

        os.environ['TOKENIZERS_PARALLELISM'] = 'False'
        model_name = "sshleifer/distilbart-cnn-12-6"
        model_revision = "a4f8f3e"
        summarisation = pipeline("summarization", model=model_name, revision=model_revision)


        if len(article) > 500:
            chunks = [article[i:i+500] for i in range(0, len(article), 500)]
        else:
            chunks = [article]

        print(len(chunks))

        with ThreadPoolExecutor(max_workers=4) as executor:
            chunk_results = list(executor.map(summarize_chunk, chunks))

        summary = " ".join(chunk_results)

        with open(os.path.join(os.getcwd(), 'Persistence Documents', 'summary_result.txt'), 'w') as sr:
            sr.write(summary)

        return summary, summary



