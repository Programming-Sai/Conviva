# **Conviva Technical Documentation**

--- 

### Table of Contents
1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Dependencies](#3-major-dependencies)
4. [Project Structure](#4-project-structure)
5. [Usage](#5-usage)
6. [Features](#6-features)
7. [Configuration](#8-configuration)
8. [Documentation](#7-documentation)
9. [Support and Contributions](#9-support-and-contributions)
10. [License](#10-license)

---

### 1. Introduction
Conviva is a Python-based application designed to provide users with a versatile platform for engaging in semi-intelligent conversations with a chatbot, downloading YouTube videos and performing text summarisation as well as communication with text-based files. This technical documentation provides insights into the application's architecture, dependencies, features, and usage instructions.

### 2. Installation
To install Conviva, follow these steps:
- Clone the repository to your local machine and navigate to the project directory:

```bash 
 git clone  https://github.com/Programming-Sai/Conviva.git

 cd Conviva
```
- Install the required dependencies using 

```bash
 pip install -r requirements.txt
```
- Execute `conviva.py` to launch the application.

---


### 3. Major Dependencies
Conviva relies on the following dependencies:
- Python 3.10
- Tkinter (for GUI)
- Requests (for HTTP requests)
- Pillow (for image processing)
- PyPDF2 (for PDF file manipulation)
- Pyttsx3 (for text-to-speech conversion) (For Windows Users.)
- FFMPEG (for video/audio processing)
- Langchain (for file communication)
- yt-dlp (for Youtube interactions)
- Others (specified in requirements.txt)...


#### To install FFMPEG Follow these depending on your system.

```bash
sudo apt-get install ffmpeg # for linux
```


```bash
brew install ffmpeg # for macOS
```


```bash
choco install ffmpeg # for windows
```

---

### 4. Project Structure

<br>

```graphql

./Conviva/*
    ├─ Conviva/db - # Stores the results from the text based file ingestion for file communication.
    ├─ Conviva/Documents - # Holds the files that can be used for file communication.
    ├─ Conviva/Downloads - # Holds all downloaded content from the mini-youtube.
    ├─ Conviva/Models/*
    |  ├─ ModelOffloader
    |  └─ LaMini - # Holds the MBZUAI/LaMini-T5-738M model
    |  
    ├─ Conviva/Modules/* - # Holds All imported modules
    |  ├─ __init__.py - # package initializer
    |  ├─ FileChat.py - # source code for file communication
    |  ├─ Assistant.py - # source code for semi-intelligent chatbot.
    |  ├─ Functionalities.py - # source code for chatbot actions.
    |  └─ Youtube_Downlloader.py - # source code for youtube operatoins.
    |
    ├─ Conviva/Images - # Holds All images used in the program.
    ├─ Conviva/Json/* - # holds all json files 
    |  ├─ intents.json - # houses the possible intents for using the chatbot
    |  ├─ ai_config.json - # allows for persistence of the first page when starting the program.
    |  └─ summary_results.json - # stores the result of a youtube search.
    |  
    ├─ Conviva/Screenshots - # Holds All screen shots used in the markdown files.
    ├─ Conviva/Persistence Documents - # Holds files that needs to be accessed later on.
    ├─ Conviva/Sound - # Allows to text to speech
    |
    |
    ├─ Conviva/conviva.py - # main source code and entry point.
    ├─ Conviva/README.md 
    ├─ Conviva/LISCENCE.txt 
    ├─ Conviva/requirements.txt
    ├─ Conviva/User-Manual.md
    └─ Conviva/Technical-Documentation.md

```


---

### 5. Usage
To use Conviva, follow these steps:
- Launch the application by executing the `conviva.py` script.
- Use the GUI interface to navigate between different features.
- Refer to the [user manual](./User-Manual.md) or help section for detailed instructions on using specific functionalities.

### 6. Features
Conviva offers the following key features:
- Chatbot Conversation: Engage in semi-intelligent conversations with the chatbot.
- YouTube: Download YouTube videos with download options.
- Text Ingestion: Manage text-based files, including PDF and TXT files.

<sup><sub> [Refer To The User Manual For Extensive Explanation About The Features.](./User-Manual.md) </sub><sup>

### 7. Documentation
Comprehensive documentation, including [user manual](./User-Manual.md), [technical documentation](#conviva-technical-documentation), and code comments, is provided to guide users and developers through the application's functionalities and codebase.

---

### 8. Configuration
<br>

> [!NOTE]
> Provide your huggingface api key in a `.env` file.

If you come across this error:

```bash

Exception in Tkinter callback
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/tkinter/__init__.py", line 1921, in __call__
    return self.func(*args)
  File "/Users/mac/Desktop/Ai/conviva.py", line 1342, in <lambda>
    help_menu.add_command(label='Open Documentation', command=lambda: DocumentationPanel(self.parent))
  File "/Users/mac/Desktop/Ai/conviva.py", line 1849, in __init__
    self.open_file()
  File "/Users/mac/Desktop/Ai/conviva.py", line 1865, in open_file
    self.display_html(html_content_with_style)
  File "/Users/mac/Desktop/Ai/conviva.py", line 1877, in display_html
    self.html_label.set_html(html_content)
  File "/Users/mac/.conviva-venv/lib/python3.10/site-packages/tkhtmlview/__init__.py", line 133, in set_html
    super().set_html(*args, **kwargs)
  File "/Users/mac/.conviva-venv/lib/python3.10/site-packages/tkhtmlview/__init__.py", line 92, in set_html
    self.html_parser.w_set_html(self, html, strip=strip)
  File "/Users/mac/.conviva-venv/lib/python3.10/site-packages/tkhtmlview/html_parser.py", line 749, in w_set_html
    self.feed(html)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/html/parser.py", line 110, in feed
    self.goahead(0)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/html/parser.py", line 170, in goahead
    k = self.parse_starttag(i)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/html/parser.py", line 344, in parse_starttag
    self.handle_starttag(tag, attrs)
  File "/Users/mac/.conviva-venv/lib/python3.10/site-packages/tkhtmlview/html_parser.py", line 563, in handle_starttag
    image = image.resize((width, height) , Image.ANTIALIAS)
AttributeError: module 'PIL.Image' has no attribute 'ANTIALIAS'

```

Open `/Users/mac/.conviva-venv/lib/python3.10/site-packages/tkhtmlview/html_parser.py` go to `line 562, in handle_starttag`
and change this line:

```python
    image = image.resize((width, height) , Image.ANTIALIAS)
```

To: 
```python
    image = image.resize((width, height), Image.Resampling.LANCZOS)
```
---


### 9. Support and Contributions
For support or contributions, please refer to the project's GitHub repository:
- Repository: [Conviva GitHub Repository](https://github.com/Programming-Sai/Conviva.git)
- Issues: Report issues or suggest enhancements via the repository's issue tracker.
- Pull Requests: Contribute code improvements or new features by submitting pull requests.

### 10. License
Conviva is licensed under the ---. See the `LICENSE` file for more details.

#### To verify liscencing... run:

```bash
pip-licenses > licenses.txt

pipdeptree > dependency_tree.txt
```
---