import os
import re
import sys
import time
import json
import fitz  
import random
import librosa
import logging
import requests
import threading
import markdown2 
import webbrowser
import subprocess
import tkinter as tk
from io import BytesIO
import sounddevice as sd
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import filedialog
from tkhtmlview import HTMLLabel 
from typing import Any, List, Dict


sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules'))


logging.basicConfig(
    filename='conviva_app.log',  # Log file name
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)











class Conviva(ctk.CTk):
    """
    A class to create and manage the AI application interface.

    Attributes:
        PRIMARY_COLOR (str): Primary color for the interface.
        SECONDARY_COLOR (str): Secondary color for the interface.
        TERTIARY_COLOR (str): Tertiary color for the interface.
        AUXILIARY_COLOR (str): Auxiliary color for the interface.
        LESSER_COLOR (str): Lesser color for the interface.
        splash (SplashScreen): The splash screen displayed at the start.
        id (int): General purpose id counter.
        end (int): End index for certain operations.
        start (int): Start index for certain operations.
        arc_id (int): Arc id for graphical elements.
        text_id (int): Text id for text elements.
        loading_id (int): Loading id for loading operations.
        listbox_id (int): Listbox id for listbox elements.
        loading (bool): Flag to indicate if loading is in progress.
        ingestion_id (int): Ingestion id for ingestion operations.
        loading_line (int): Loading line index for loading operations.
        ingesting (bool): Flag to indicate if ingestion is in progress.
        current_page_idx (int): Index of the current page being displayed.
        page_frame (tk.Frame): Frame to hold the current page's content.
        size (tuple): The size of the application window.
        border_color (str): Color of the window border.
        window_title (str): Title of the window.
        border_frame_color_change (bool): Flag to indicate if the border frame color should change.
        text_based_preview_frame (ctk.CTkFrame): Frame for text-based preview.
        pdf_preview_canvas (tk.Canvas): Canvas for PDF preview.
        page_loader (tk.Label): Label to indicate page loading.
        text_preview_textbox (tk.Text): Textbox for text preview.
        listbox_suggestions (tk.Listbox): Listbox for suggestions.
        bg_image (ImageTk.PhotoImage): Background image for the application.
        pages (list): List of page functions.
        page_commands (list): List of page command functions.
        status_label (ctk.CTkLabel): Label to display status messages.
        functionality (Functionalities): Functionalities instance for various operations.
        intent (dict): Dictionary of intents.
        intent_function_mappings (dict): Mapping of intents to their corresponding functions.
    """
    
    def __init__(self, title: str, size: tuple):
        """
        Initialize the Conviva class.

        Args:
            title (str): The title of the application window.
            size (tuple): The size of the application window.
        """
        super().__init__()

        # Define the primary colors for the application
        self.PRIMARY_COLOR = "#29174a"
        self.SECONDARY_COLOR = "#16082f"
        self.TERTIARY_COLOR = "#212052"
        self.AUXILIARY_COLOR = "#413468"
        self.LESSER_COLOR = "#5376a7"

        # Set initial geometry to 0x0 to be invisible initially
        self.geometry("0x0")

        # Show splash screen
        self.splash = SplashScreen(self)

        # Import necessary modules and classes
        global FileChat, YoutubeDownloader, Assistant, Functionalities, say, load_intents
        from Modules.File_Chat import FileChat
        from Modules.Youtube_Downloader import YoutubeDownloader
        from Modules.Assistant import Assistant, say, load_intents
        from Modules.Functionalities import Functionalities
        # Deiconify the window and wait for splash screen
        self.deiconify()
        time.sleep(8)
        self.splash.destroy()

        # Load configuration data
        config_data = self.get_config_data()

        # Initialize attributes for various operations
        self.id = 0
        self.end = 6
        self.start = 0
        self.arc_id = 0
        self.text_id = 0
        self.loading_id = 1
        self.listbox_id = 2
        self.loading = False
        self.ingestion_id = 0
        self.loading_line = 0
        self.ingesting = False
        self.current_page_idx = config_data.get('starting-page-index') if config_data.get('starting-page-index') is not None else 0 

        # Create the main page frame
        self.page_frame = tk.Frame(self, background=self.TERTIARY_COLOR)
        self.page_frame.pack(fill='both', expand=True)

        # Set the appearance mode to dark
        ctk.set_appearance_mode('dark')

        # Set the window size, title, and attributes
        self.size = size
        self.border_color = ''
        self.window_title = title
        self.resizable(False, False)
        self.title(self.window_title)
        self.attributes('-alpha', 0.8)
        self.border_frame_color_change = False
        self.minsize(self.size[0], self.size[1])
        self.maxsize(self.size[0], self.size[1])
        self.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.winfo_screenwidth()/2)-int(self.size[0]/2)}+{int(self.winfo_screenheight()/2)-int(self.size[1]/2)-50}")

        # Create frames and widgets for various previews and functionalities
        self.text_based_preview_frame = ctk.CTkFrame(self, width=int(self.size[0]/2), height=int(self.size[1])-20, fg_color=self.TERTIARY_COLOR, border_width=5)
        self.pdf_preview_canvas = tk.Canvas(self.text_based_preview_frame, bg='red', highlightthickness=0)
        self.page_loader = tk.Label(self, text='Loading...', background=self.SECONDARY_COLOR, pady=20)

        self.text_preview_textbox = tk.Text(self.text_based_preview_frame, wrap='word')
        self.text_preview_textbox.config(yscrollcommand=None, xscrollcommand=None, highlightbackground=self.cget("background"))

        self.listbox_suggestions = tk.Listbox(self, background=self.SECONDARY_COLOR, height=0)

        # Bind escape key to quit the application
        self.bind('<Escape>', lambda event : self.quit())

        # Set the background image
        self.bg_image = ImageTk.PhotoImage(file=os.path.join(os.getcwd(), 'Images', 'background.jpg'))

        # Define pages and corresponding commands
        self.pages = [self.ai_conversation_page, self.chat_conversation_page, self.text_ingestion_page, self.mini_youtube_page]
        self.page_commands = [self.ai_page, self.chat_page, self.ingestion_page, self.youtube_page]

        # Status label for displaying messages
        self.status_label = ctk.CTkLabel(self, text="", font=('Arial Black', 15), fg_color=self.AUXILIARY_COLOR, corner_radius=100, width=300, pady=5)
        
        # Initialize functionalities and intents
        self.functionality = Functionalities(False, say)
        self.intent = load_intents()
        self.intent_function_mappings = {
            "open-cmd": self.functionality.open_cmd,
            "search-google": self.functionality.search_google,
            "play-youtube-video": self.functionality.play_video,
            "wikipedia-search": self.functionality.wikipedia_search,
            "time-telling": self.functionality.tell_time,
            "summarizer": self.functionality.text_summary,
            "mini-youtube": self.youtube_page,
            "file-chat": self.functionality.chat_with_files,
            "repeat": self.functionality.repeat
        }

        # Load the initial page
        self.load_page()
        
        # Initialize the menu bar
        MenuBarEntries(self)
        
        # Start the main loop
        self.mainloop()
    
    def get_config_data(self) -> dict:
        """
        Get configuration data from the config file.

        Returns:
            dict: Configuration data as a dictionary.
        """
        try:
            with open(os.path.join(os.getcwd(), "Json", "ai_config.json"), 'r') as acj:
                return json.load(acj)
        except:
            return {}

    def load_page(self) -> None:
        """
        Load the current page based on the current page index.

        Returns:
            None
        """
        self.pages[self.current_page_idx]()
        self.page_loader.pack_forget()

    def ai_page(self, e: tk.Event = None) -> None:
        """
        Load the AI conversation page.

        Args:
            e (tk.Event, optional): Event that triggered the method. Defaults to None.

        Returns:
            None
        """
        self.clear_page_frame()
        self.current_page_idx = 0
        self.page_loader = tk.Label(self.page_frame, text='Loading...', background=self.SECONDARY_COLOR, pady=20, font=("Arial Black", 20))
        self.page_loader.pack(expand=True, fill='x')      
        self.load_page()

    def clear_page_frame(self) -> None:
        """
        Clear all widgets from the page frame.

        Returns:
            None
        """
        for child in self.page_frame.winfo_children():
            child.destroy()

    def chat_page(self, e: tk.Event = None) -> None:
        """
        Load the chat conversation page.

        Args:
            e (tk.Event, optional): Event that triggered the method. Defaults to None.

        Returns:
            None
        """
        self.clear_page_frame()
        self.current_page_idx = 1
        self.page_loader = tk.Label(self.page_frame, text='Loading...', background=self.SECONDARY_COLOR, pady=20, font=("Arial Black", 20))
        self.page_loader.pack(expand=True, fill='x')  
        self.load_page()

    def youtube_page(self, e: tk.Event = None) -> None:
        """
        Load the mini YouTube page.

        Args:
            e (tk.Event, optional): Event that triggered the method. Defaults to None.

        Returns:
            None
        """
        self.clear_page_frame()
        self.current_page_idx = 3
        self.page_loader = tk.Label(self.page_frame, text='Loading...', background=self.SECONDARY_COLOR, pady=20, font=("Arial Black", 20))
        self.page_loader.pack(expand=True, fill='x')
        self.load_page()

    def ingestion_page(self, e: tk.Event = None) -> None:
        """
        Load the text ingestion page.

        Args:
            e (tk.Event, optional): Event that triggered the method. Defaults to None.

        Returns:
            None
        """
        self.clear_page_frame()
        self.current_page_idx = 2
        self.page_loader = tk.Label(self.page_frame, text='Loading...', background=self.SECONDARY_COLOR, pady=20, font=("Arial Black", 20))
        self.page_loader.pack(expand=True, fill='x')   
        self.load_page()






    def ai_conversation_page(self) -> None:
        """
        Load the AI conversation page.

        Returns:
            None
        """
        self.canvas = tk.Canvas(self.page_frame, width=self.size[0], height=self.size[1], highlightthickness=0)
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image)

        # Create and pack a Pulser widget in the center of the canvas
        self.pulser = Pulser(self, corner_radius=200, border_width=2, border_color=self.LESSER_COLOR).pack_frame()
        self.canvas.create_window(int(self.size[0]/2), int(self.size[1]/2)-50, anchor='center', window=self.pulser)
                                  
        # Create a floating button list with page commands
        FloatingButtonList(self, orientation='vertical', functions=self.page_commands)

        # Create a search bar for AI conversation input
        self.search_bar_1 = ctk.CTkEntry(self, fg_color=self.SECONDARY_COLOR, border_color=self.LESSER_COLOR, width=600, height=50, corner_radius=200, placeholder_text_color='white', placeholder_text='Message Conviva...')
        self.search_bar_1.bind("<Return>", self.get_ai_prompt)
        self.canvas.create_window(int(self.size[0]/2), 540, anchor='center', window=self.search_bar_1)
        
        # Pack the canvas to make it visible
        self.canvas.pack(expand=True, fill='both')

    def get_ai_prompt(self, e: tk.Event) -> str:
        """
        Handle the return key event to get the AI prompt from the search bar.

        Args:
            e (tk.Event): The event that triggered the method.

        Returns:
            str: The text entered in the search bar.
        """
        text = self.search_bar_1.get()
        with open(os.path.join(os.getcwd(), "Persistence Documents", "conversation_history.txt"), 'a') as ch:
            ch.write(f"\t\t\t{text}\n")

        # Get AI response based on the input text
        response, add_ons, tag = Assistant(self.intent, False, say, intent_mapping=self.intent_function_mappings).get_response(text)
        
        # Process additional response elements if any
        print_add_ons, say_add_ons = add_ons or ("", "")
        response = response + print_add_ons
        
        # Display the response using the Pulser widget
        self.pulser.speech(response)
        with open(os.path.join(os.getcwd(), "Persistence Documents", "conversation_history.txt"), 'a') as ch:
            ch.write(f"{response}\n\n")
        # Clear the search bar after processing
        self.search_bar_1.delete(0, tk.END)
        return text

    def chat_conversation_page(self) -> None:
        """
        Load the chat conversation page.

        Returns:
            None
        """
        self.canvas = tk.Canvas(self.page_frame, width=self.size[0], height=self.size[1], highlightthickness=0)
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image)
        
        # Create a floating button list with page commands
        FloatingButtonList(self, orientation='vertical', functions=self.page_commands)
        
        # Initialize chat bar and  chat interface
        self.chat = ChatBar(self)
        frame = ctk.CTkFrame(self)
        ChatInterFace(frame, self, self.chat)
        
        # Create windows for chat bar and interface
        self.canvas.create_window(int(self.size[0]/2), 548, anchor='center', window=self.chat)
        self.canvas.create_window(int(self.size[0]/2), int(self.size[1]/2)+5, anchor='center', window=frame)
        
        # Pack the canvas to make it visible
        self.canvas.pack(expand=True, fill='both')

    def text_ingestion_page(self) -> None:
        """
        Load the text ingestion page.

        Returns:
            None
        """
        self.canvas = tk.Canvas(self.page_frame, width=self.size[0], height=self.size[1], highlightthickness=0)
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image)

        # Create a frame for text-based preview
        self.text_based_preview_frame = ctk.CTkFrame(self, width=int(self.size[0]/2), height=int(self.size[1])-20, fg_color=self.TERTIARY_COLOR, border_width=5)
        self.pdf_preview_canvas = tk.Canvas(self.text_based_preview_frame, bg='red', highlightthickness=0)
        self.text_based_preview_frame.propagate(False)

        # Create a floating button list with page commands
        FloatingButtonList(self, orientation='vertical', functions=self.page_commands)
        
        # Bind double-click event to open text-based file
        self.text_based_preview_frame.bind("<Double-Button-1>", self.open_text_based_file)
        
        # Start border animation and place label
        self.animate_frame_border()
        self.place_label()
        
        # Create a window for the text-based preview frame
        self.canvas.create_window(10, 10, anchor='nw', window=self.text_based_preview_frame)
        
        # Pack the canvas to make it visible
        self.canvas.pack(expand=True, fill='both')






    def animate_frame_border(self) -> None:
        """
        Animate the border color of the text-based preview frame.

        This method toggles the border color between LESSER_COLOR and TERTIARY_COLOR
        every 500 milliseconds.
        """
        self.border_frame_color_change = not self.border_frame_color_change
        if self.border_frame_color_change:
            self.border_color = self.LESSER_COLOR
        else:
            self.border_color = self.TERTIARY_COLOR
        self.text_based_preview_frame.configure(border_color=self.border_color)
        self.border_animation_id = self.after(500, self.animate_frame_border)

    def disable_scroll(self, event: tk.Event) -> None:
        """
        Disable scrolling for the text preview textbox.

        Args:
            event (tk.Event): The event that triggered the method.
        """
        pass
        # return "break"

    def truncate_title(self, title: str) -> str:
        """
        Truncate the file title if it exceeds 25 characters.

        Args:
            title (str): The title of the file.

        Returns:
            str: The truncated title.
        """
        if len(title) <= 25:
            return title
        else:
            return (title[:25-7]+"...pdf") if title.endswith('pdf') else (title[:25-7]+"...txt")

    def call_ingest(self, file_path: str) -> None:
        """
        Call the ingestion process for the given file.

        Args:
            file_path (str): The path of the file to ingest.
        """
        self.status_label.configure(text="Ingesting...")
        self.update_idletasks()  
        self.status_label.place(x=int(self.size[0]/2)+260, y=450, anchor='center')
        self.after(100, self.ingest_and_cleanup, file_path)

    def clear_ingested_database(self) -> None:
        """
        Clear the ingested database after user confirmation.

        This method prompts the user for confirmation before clearing the database.
        """
        if messagebox.askyesno('Clear Database?', 'Are You Sure That You Want To Clear The Database?'):
            FileChat().clear_database()
            logging.info("Database cleared")

    def open_summarizer(self, file_path: str) -> None:
        """
        Open the summarizer panel for the given file.

        Args:
            file_path (str): The path of the file to summarize.
        """
        SummarizerPanel(self, file_path=file_path)

    def open_text_based_file(self, e: tk.Event = None) -> None:
        """
        Open a file dialog to select and preview a text-based file.

        Args:
            e (tk.Event, optional): The event that triggered the method. Defaults to None.
        """
        if self.ingesting:
            Toast(self, 'Sorry, Can\'t Open New File While Ingesting Previous', offset=(200, 200))
        else:
            global FileChat, YoutubeDownloader, Assistant, Functionalities, say, load_intents
            try:
                self.filename = filedialog.askopenfilename(
                    initialdir=os.path.join(os.getcwd(), "Documents"), 
                    title='Select A File', 
                    filetypes=(("All Files", "*"), ("Text Files", "*.txt"), ("PDF Files", "*.pdf"))
                )
                if self.filename:
                    self.render_text_based_file_preview(self.filename)
            except Exception as e:
                print(f"Error: {e}")

    def ingest_and_cleanup(self, file_path: str) -> None:
        """
        Ingest the given file and update the UI upon completion.

        Args:
            file_path (str): The path of the file to ingest.
        """
        try:
            print("Ingestion Started")
            FileChat().basic_ingest(file_path)
            print("Ingestion Ended")
        except Exception as e:
            print(f"Ingestion failed: {e}")
            self.status_label.configure(text="Ingestion Failed")
            logging.error(f"Error ingesting{os.path.basename(file_path)}")
        else:
            self.status_label.configure(text="Ingestion Complete")
            print("Ingestion Complete")
            logging.info(f"{os.path.basename(file_path)} has been ingested")
        finally:
            self.after(4000, self.status_label.place_forget)
            self.ingestion_button.configure(state='normal')

        # FileChat().basic_ingest(file_path)

    def format_file_size(self, size_in_bytes: int) -> str:
        """
        Format the file size from bytes to a readable format.

        Args:
            size_in_bytes (int): The size of the file in bytes.

        Returns:
            str: The formatted file size.
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        factor = 1024
        for unit in units:
            if size_in_bytes < factor:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= factor

    def render_text_based_file_preview(self, file_path: str) -> None:
        """
        Render a preview of the selected text-based file.

        Args:
            file_path (str): The path of the file to preview.
        """
        self.text = ''
        self.opening_message.pack_forget()
        self.after_cancel(self.border_animation_id)
        self.canvas.delete(self.text_id)
        self.text_preview_textbox.pack_forget()
        self.pdf_preview_canvas.pack_forget()

        if file_path.endswith('pdf'):
            # Load and display the first page of the PDF
            preview = fitz.open(file_path).load_page(0).get_pixmap()
            img = ImageTk.PhotoImage(
                Image.frombytes("RGB", [preview.width, preview.height], preview.samples)
                .resize((int(self.size[0]/2), int(self.size[1])-20))
            )
            self.id = self.pdf_preview_canvas.create_image(0, 0, anchor='nw', image=img)
            self.pdf_preview_canvas.image = img
            self.pdf_preview_canvas.pack(fill='both', expand=True)

            file_data = self.extract_info_from_text_based_file(file_path)
            self.text = f"Title:  {self.truncate_title(file_data.get('title'))}\n\n\n\nSize:  {file_data.get('size')}\n\n\n\nNumber of Pages: {file_data.get('no-pages')}"
            self.text_id = self.canvas.create_text(int(self.size[0]/2)+100, 150, anchor='nw', text=self.text, font=('Arial', 20))

        elif file_path.endswith('txt'):
            # Load and display the text content of the file
            self.text_preview_textbox.pack_forget()
            self.text_preview_textbox = tk.Text(self.text_based_preview_frame, wrap='word')
            self.text_preview_textbox.config(padx=10, pady=20)
            self.text_preview_textbox.bind("<MouseWheel>", self.disable_scroll)

            try:
                with open(file_path, 'r') as preview_text:
                    preview_lines = preview_text.readlines()
                    for line in preview_lines:
                        self.text_preview_textbox.insert('end', line)
                    self.text_preview_textbox.configure(state='disabled', borderwidth=0)
            except:
                pass

            self.text_preview_textbox.pack(expand=True, fill='both')
            self.text = f"Title:  {self.truncate_title(os.path.basename(file_path))}\n\n\n\nSize:  {self.format_file_size(os.path.getsize(file_path))}\n\n\n\nNumber of Lines:  {len(preview_lines)}"
            self.text_id = self.canvas.create_text(int(self.size[0]/2)+100, 150, anchor='nw', text=self.text, font=('Arial', 20))

        # Create and place buttons for summarizing, ingesting, and clearing the database
        self.summarize_button = ctk.CTkButton(
            self, text='Summarize Text', command=lambda: self.open_summarizer(file_path), 
            fg_color=self.LESSER_COLOR, corner_radius=20, hover_color=self.SECONDARY_COLOR
        )
        self.ingestion_button = ctk.CTkButton(
            self, text='Ingest File?', command=lambda: self.call_ingest(file_path), 
            fg_color=self.LESSER_COLOR, corner_radius=20, hover_color=self.SECONDARY_COLOR
        )
        self.close_button = ctk.CTkButton(
            self, text='Clear Database', command=self.clear_ingested_database, 
            fg_color=self.LESSER_COLOR, corner_radius=20, hover_color=self.SECONDARY_COLOR
        )

        # Place buttons on the canvas
        self.canvas.create_window(int(self.size[0]/2)+100, 3.6*int(self.size[1]/4)-10, anchor='nw', window=ctk.CTkButton(
            self, text='Select New File?', command=self.open_text_based_file, 
            fg_color=self.LESSER_COLOR, corner_radius=20, hover_color=self.SECONDARY_COLOR
        ))
        self.canvas.create_window(int(self.size[0]/2)+100, 3.6*int(self.size[1]/4)+25, anchor='nw', window=self.summarize_button)
        self.canvas.create_window(int(self.size[0]/2)+300, 3.6*int(self.size[1]/4)+25, anchor='nw', window=self.close_button)
        self.canvas.create_window(int(self.size[0]/2)+300, 3.6*int(self.size[1]/4)-10, anchor='nw', window=self.ingestion_button)

    def extract_info_from_text_based_file(self, file_path: str) -> dict:
        """
        Extract metadata from a text-based file.

        Args:
            file_path (str): The path of the file to extract information from.

        Returns:
            dict: A dictionary containing the title, size, and number of pages of the file.
        """
        metadata = {}
        try:
            with fitz.open(file_path) as pdf_file:
                metadata["title"] = os.path.basename(file_path)
                metadata["size"] = self.format_file_size(os.path.getsize(file_path))
                metadata["no-pages"] = pdf_file.page_count
        except Exception as e:
            print("Error:", e)
        return metadata



    def mini_youtube_page(self) -> None:
        """
        Setup the mini YouTube page UI components.

        This method initializes the search bar, fetches initial search results,
        and places navigation buttons and other UI elements on the canvas.
        """
        self.canvas = tk.Canvas(self.page_frame, width=self.size[0], height=self.size[1], highlightthickness=0)
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image)
        self.search_bar_2 = ctk.CTkEntry(
            self, fg_color=self.SECONDARY_COLOR, border_color=self.LESSER_COLOR,
            width=600, height=50, corner_radius=200, placeholder_text_color='white',
            placeholder_text='Search...', font=('Arial', 15)
        )

        self.yt_search_result_data = self.fetch_result_data_json(os.path.join(os.getcwd(), 'Json', 'search_results.json'))
        self.place_search_results()

        self.search_bar_2.bind("<KeyRelease>", self.on_key_release)
        self.search_bar_2.bind("<Return>", self.on_entry_enter)

        self.canvas.create_window(int(self.size[0]/2), 100, anchor='center', window=self.search_bar_2)

        FloatingButtonList(self, orientation='vertical', functions=self.page_commands)

        self.listbox_suggestions = tk.Listbox(self, background=self.SECONDARY_COLOR, height=0)
        self.listbox_suggestions.bind("<Double-Button-1>", self.on_select)
        self.listbox_suggestions.bind("<<ListboxSelect>>", self.on_item_select)

        self.back_button = ctk.CTkButton(
            self, text='\u25C4', font=('Arial Black', 20), fg_color=self.SECONDARY_COLOR,
            hover_color=self.TERTIARY_COLOR, command=self.back
        )
        self.canvas.create_window(100, 595, anchor='sw', window=self.back_button)

        self.canvas_text = self.canvas.create_text(
            int(self.size[0]/2), 595, anchor='s', text=f'Page: {0 if len(self.yt_search_result_data) == 0 else int(self.end/6) }/{int(len(self.yt_search_result_data)/6)}',
            font=('Arial Black', 20)
        )

        self.forward_button = ctk.CTkButton(
            self, text='\u25BA', font=('Arial Black', 20), fg_color=self.SECONDARY_COLOR,
            hover_color=self.TERTIARY_COLOR, command=self.forward
        )
        self.canvas.create_window(800, 595, anchor='se', window=self.forward_button)
        self.canvas.pack(expand=True, fill='both')

    def back(self) -> None:
        """
        Navigate to the previous page of YouTube search results.
        """
        self.clear_search_results()
        self.canvas.delete(self.loading_line)

        self.end = self.start if self.start > 0 else 6
        self.start = (self.start - 6) if self.start > 0 else 0

        self.canvas.delete(self.canvas_text)
        self.canvas_text = self.canvas.create_text(
            int(self.size[0]/2), 595, anchor='s', text=f'Page: {int(self.end/6)}/{int(len(self.yt_search_result_data)/6)}',
            font=('Arial Black', 20)
        )
        self.loading_line = self.canvas.create_window(
            int(self.size[0]/2), int(self.size[1]/2), anchor='center',
            window=ctk.CTkLabel(self, text='Reloading', font=('Arial Black', 15), width=900, fg_color=self.LESSER_COLOR, text_color='white')
        )

        self.after(100, self.place_search_results)

    def forward(self) -> None:
        """
        Navigate to the next page of YouTube search results.
        """
        self.clear_search_results()
        self.canvas.delete(self.loading_line)

        self.start = (self.start + 6) if self.start < len(self.yt_search_result_data) - 6 else len(self.yt_search_result_data) - 6
        self.end = self.start + 6

        self.canvas.delete(self.canvas_text)
        self.canvas_text = self.canvas.create_text(
            int(self.size[0]/2), 595, anchor='s', text=f'Page: {int(self.end/6)}/{int(len(self.yt_search_result_data)/6)}',
            font=('Arial Black', 20)
        )
        self.loading_line = self.canvas.create_window(
            int(self.size[0]/2), int(self.size[1]/2), anchor='center',
            window=ctk.CTkLabel(self, text='Reloading', font=('Arial Black', 15), width=900, fg_color=self.LESSER_COLOR, text_color='white')
        )

        self.after(100, self.place_search_results)

    def bind_items(self) -> None:
        """
        Bind the YouTube search result items to open the download screen on click.
        """
        id = 0
        for _, image_label, title_label, duration_label in self.yt_search_result_frame_details:
            image_label.bind("<Button-1>", lambda event, id=id, images=self.images, data=self.first_6_data: self.open_download_screen(event, id, images, data))
            title_label.bind("<Button-1>", lambda event, id=id, images=self.images, data=self.first_6_data: self.open_download_screen(event, id, images, data))
            duration_label.bind("<Button-1>", lambda event, id=id, images=self.images, data=self.first_6_data: self.open_download_screen(event, id, images, data))
            id += 1

    def place_label(self) -> None:
        """
        Place a label in the text-based preview frame.
        """
        self.opening_message = ctk.CTkLabel(self.text_based_preview_frame, text='Double Click To Select a File', font=('Kokonor', 30))
        self.opening_message.pack(expand=True)
        self.opening_message.bind("<Double-Button-1>", self.open_text_based_file)

    def search_youtube(self) -> None:
        """
        Search for YouTube videos and update the search results.

        This method disables the search bar and navigation buttons, performs a YouTube search,
        and updates the UI with the new search results.
        """
        time.sleep(1)
        self.search_bar_2.configure(state='disabled')
        self.forward_button.configure(state='disabled')
        self.back_button.configure(state='disabled')
        search = YoutubeDownloader(False, say)
        query = self.search_bar_2.get()
        max_result = random.choice([6, 12, 16, 24, 30, 36])
        search_results = search.search_videos(self.search_bar_2.get(), random.choice([6, 12, 16, 24, 30, 36]))
        if search_results:
            search.save_as_json(search_results, os.path.join(os.getcwd(), 'Json', 'search_results.json'))
            logging.info(f"Performed search  with {query} as query and {max_result} as number of result.")
        self.canvas.delete(self.loading_line)
        self.search_bar_2.configure(state='normal')
        self.forward_button.configure(state='normal')
        self.back_button.configure(state='normal')
        self.start = 0
        self.end = 6
        self.canvas.delete(self.canvas_text)
        self.yt_search_result_data = self.fetch_result_data_json(os.path.join(os.getcwd(), os.path.join(os.getcwd(), 'Json', 'search_results.json')))
        self.canvas_text = self.canvas.create_text(
            int(self.size[0]/2), 595, anchor='s', text=f'Page: {int(self.end/6)}/{int(len(self.yt_search_result_data)/6)}',
            font=('Arial Black', 20)
        )
        self.search_bar_2.delete(0, tk.END)
        self.after(100, self.place_search_results)

    def on_select(self, event: tk.Event) -> None:
        """
        Handle the selection of an item from the suggestion listbox.

        Args:
            event (tk.Event): The event that triggered the method.
        """
        selected = event.widget.get(tk.ACTIVE)
        if str(selected).strip():
            self.search_bar_2.delete(0, tk.END)
            self.search_bar_2.insert(tk.END, selected.strip())
            self.canvas.delete(self.listbox_id)

    def clear_search_results(self) -> None:
        """
        Clear the current search results from the canvas.
        """
        for result_frame, image_label, title_label, duration_label in self.yt_search_result_frame_details:
            self.canvas.delete(result_frame)

    def place_search_results(self) -> None:
        """
        Place the search results on the canvas.

        This method displays the first 6 search results, creating frames and labels for each result.
        """
        self.yt_search_result_frame_details = []
        self.first_6_data = self.yt_search_result_data[self.start:self.end]
        self.images = [self.fetch_image_from_internet(url['largest_thumbnail']) for url in self.first_6_data]
        idx = 0
        for i in [50, 350, 650]:
            for j in [170, 380]:
                if self.first_6_data and idx < len(self.images):
                    self.result_frame = ctk.CTkFrame(self, width=250, height=180, corner_radius=0, fg_color=self.TERTIARY_COLOR )

                    self.canvas_result_frame = self.canvas.create_window(i-25, j, anchor='nw', window=self.result_frame)

                    self.image_label = tk.Label(self.result_frame, image=self.images[idx], height=112)
                    self.image_label.pack()

                    self.title_label  = ctk.CTkLabel(self.result_frame, text=self.manage_break(self.break_text(self.first_6_data[idx]['title'], 30)), width=20, padx=5, font=('Arial', 12), justify='left', fg_color=self.TERTIARY_COLOR , text_color='white')
                    self.title_label.pack(expand=True, side='left', fill='both')

                    self.duration_label = ctk.CTkLabel(self.result_frame, text=self.first_6_data[idx]['audio_length'], font=('Arial', 12), fg_color=self.TERTIARY_COLOR , text_color='white')
                    self.duration_label.pack(expand=True, side='right', fill='both')


                    
                    self.result_frame.propagate(False)
                    self.yt_search_result_frame_details.append((self.canvas_result_frame, self.image_label, self.title_label, self.duration_label))
                idx+=1
        self.bind_items()
        self.reloading = False
        self.update()
        self.canvas.delete(self.loading_line)
        self.listbox_suggestions.lift()




    def on_item_select(self, event: tk.Event) -> None:
        """
        Handle the selection of an item in the suggestion listbox.

        Args:
            event (tk.Event): The event that triggered the method.
        """
        for selected in self.listbox_suggestions.curselection():
            if selected % 2 != 0:
                self.listbox_suggestions.selection_clear(self.listbox_suggestions.curselection())

    def on_key_release(self, event: tk.Event) -> None:
        """
        Handle key release events in the search bar.

        Args:
            event (tk.Event): The event that triggered the method.
        """
        key = event.keysym
        if key != "Return":
            threading.Thread(target=self.get_suggestions_for_list_box).start()

    def on_entry_enter(self, event: tk.Event) -> None:
        """
        Handle pressing Enter in the search bar.

        Args:
            event (tk.Event): The event that triggered the method.
        """
        self.clear_search_results()
        self.canvas.delete(self.listbox_id)
        self.canvas.delete(self.listbox_id)
        self.canvas.delete(self.loading_line)
        self.loading_line = self.canvas.create_window(
            int(self.size[0] / 2), int(self.size[1] / 2), anchor='center',
            window=ctk.CTkLabel(self, text='Searching', font=('Arial Black', 15), width=900,
                                 fg_color=self.LESSER_COLOR, text_color='white')
        )
        threading.Thread(target=self.search_youtube).start()

    def break_text(self, text: str, width: int) -> List[str]:
        """
        Break a text into lines of given width.

        Args:
            text (str): The text to break.
            width (int): The maximum width of each line.

        Returns:
            List[str]: List of broken lines.
        """
        if len(text) < width:
            return [text]
        lines = []
        words = text.split()
        current_line = ''
        for word in words:
            if len(current_line) + len(word) <= width:
                current_line += word + ' '
            else:
                break
        lines.append(current_line.strip())
        current_line = ''
        for word in words[len(lines[0].split()):]:
            if len(current_line) + len(word) <= width:
                current_line += word + ' '
            else:
                break
        if current_line:
            if len(current_line) > width:
                current_line = current_line[:width-3] + '...'
            lines.append(current_line.strip())
        if len(lines) > 1 and len(words) > len(lines[0].split()) + len(lines[1].split()):
            lines[1] = lines[1][:width-3] + '...'
        return lines

    def manage_break(self, text_list: List[str]) -> str:
        """
        Manage the broken text list.

        Args:
            text_list (List[str]): The list of broken text lines.

        Returns:
            str: The formatted text.
        """
        if len(text_list) >= 2:
            text = ''
            for line in text_list:
                text += line + '\n'
            return (text[:-1])
        else:
            return text_list[0]

    def update_listbox(self, suggestions: List[str]) -> None:
        """
        Update the suggestion listbox with new suggestions.

        Args:
            suggestions (List[str]): The list of suggestions to display.
        """
        self.listbox_suggestions.delete(0, tk.END)
        for suggestion in suggestions:
            self.listbox_suggestions.insert(tk.END, '   '+str(suggestion))
            self.listbox_suggestions.insert(tk.END, '')
        if suggestions:
            self.listbox_id = self.canvas.create_window(
                150, 125, anchor='nw', window=self.listbox_suggestions, width=600)
            self.canvas.tag_raise(self.listbox_id)
        else:
            self.canvas.delete(self.listbox_id)

    def get_suggestions_for_list_box(self) -> None:
        """
        Fetch suggestions for the listbox based on the search bar input.
        """
        query = self.search_bar_2.get()
        suggestions = YoutubeDownloader(False, say).fetch_suggestions(query) if query.strip() else []
        self.listbox_suggestions.after(0, self.update_listbox, suggestions)

    def fetch_result_data_json(self, path: str) -> Dict:
        """
        Load search result data from a JSON file.

        Args:
            path (str): The path to the JSON file.

        Returns:
            Dict: The loaded JSON data.
        """
        try:
            with open(path, 'r') as rj:
                return json.loads(rj.read())
        except Exception as e:
                return []

    def open_download_screen(self, event: tk.Event, id: int, image: Any, data: Any) -> None:
        """
        Open the download screen for a selected video.

        Args:
            event (tk.Event): The event that triggered the method.
            id (int): The ID of the selected video.
            image (Any): The image associated with the video.
            data (Any): The data associated with the video.
        """
        AudioOrVideoDownloadScreen(self, id, image, data)

    def fetch_image_from_internet(self, url: str, target_width: int = 250) -> Any:
        """
        Fetch an image from the internet and resize it.

        Args:
            url (str): The URL of the image.
            target_width (int): The target width for resizing.

        Returns:
            Any: The resized image.
        """
        try:
            res = requests.get(url, timeout=5)
            img = Image.open(BytesIO(res.content))
            width, height = img.size
            new_width, new_height = (target_width, int(target_width/(width/height)))
            return ImageTk.PhotoImage(img.resize((new_width, new_height)))
        except:
            img = Image.open(os.path.join(os.getcwd(), 'Images', 'placeholder.jpg'))
            width, height = img.size
            new_width, new_height = (target_width, int(target_width/(width/height)))
            return ImageTk.PhotoImage(img.resize((new_width, new_height)))


class Toast(tk.Toplevel):
    """
    A class representing a Toast notification.

    Attributes:
        parent (tk.Tk): The parent window.
        offset (tuple): The offset for the toast position on the screen.
        message (str): The message to be displayed in the toast.
        label (tk.Label): The label displaying the toast message.
    """

    def __init__(self, parent: tk.Tk, message: str, offset: tuple = (80, 200)):
        """
        Initialize the Toast class.

        Args:
            parent (tk.Tk): The parent window.
            message (str): The message to be displayed in the toast.
            offset (tuple): The offset for the toast position on the screen. Defaults to (80, 200).
        """
        super().__init__(parent)
        self.parent = parent
        self.offset = offset
        self.message = message
        self.overrideredirect(True)
        self.resizable(False, False)
        self.after(2000, self.destroy)  # Destroy the toast after 2 seconds
        self.label = tk.Label(self, text=self.message, background=self.parent.AUXILIARY_COLOR, padx=30, pady=10)
        self.label.pack(expand=True, fill='both')
        # Set the geometry of the toast
        self.geometry(f"+{int(self.parent.winfo_screenwidth()/2)-int(self.winfo_width()/2)-self.offset[0]}+"
                      f"{int(self.parent.winfo_screenheight()/2)-int(self.winfo_height()/2)+self.offset[1]}")


class Pulser(ctk.CTkFrame):
    """
    A class representing a pulsing animation frame with audio playback capabilities.

    Attributes:
        parent (tk.Tk): The parent window.
        speed (int): The speed of the GIF animation.
        speaking (bool): The speaking state of the Pulser.
        color (str): The foreground color of the frame.
        output_file (str): The audio output file.
        y (ndarray): The audio data.
        sr (int): The sample rate of the audio.
    """
    def __init__(self, parent: tk.Tk, border_width: int = 2, border_color: str = 'black', 
                 corner_radius: int = 200, fg_color: str = 'black', width: int = 350, 
                 height: int = 350, speed: int = 50):
        """
        Initialize the Pulser class.

        Args:
            parent (tk.Tk): The parent window.
            border_width (int): The width of the border. Defaults to 2.
            border_color (str): The color of the border. Defaults to 'black'.
            corner_radius (int): The radius of the corners. Defaults to 200.
            fg_color (str): The foreground color. Defaults to 'black'.
            width (int): The width of the frame. Defaults to 350.
            height (int): The height of the frame. Defaults to 350.
            speed (int): The speed of the GIF animation. Defaults to 50.
        """
        self.parent = parent
        background_corner_colors = (self.parent.SECONDARY_COLOR, self.parent.SECONDARY_COLOR, 
                                    self.parent.TERTIARY_COLOR, self.parent.TERTIARY_COLOR)
        super().__init__(parent, border_width=border_width, border_color=border_color, 
                         corner_radius=corner_radius, fg_color=fg_color, width=width, 
                         height=height, background_corner_colors=background_corner_colors)
        self.speed = speed
        self.speaking = False
        self.color = fg_color
        self.output_file = os.path.join(os.getcwd(), 'Sound', 'prompt.aiff')
        self.y, self.sr = librosa.load(self.output_file, sr=None)

        self._create_gif_section()

    def _play(self) -> None:
        """
        Play the audio file and toggle the speaking state.

        Returns:
            None
        """
        self.speaking = not self.speaking
        sd.play(self.y, self.sr)
        sd.wait()
        self.speaking = not self.speaking

    def pack_frame(self) -> 'Pulser':
        """
        Pack the frame and prevent propagation.

        Returns:
            Pulser: The instance of the Pulser class.
        """
        self.pack(expand=True)
        self.pack_propagate(False)
        return self

    def speech(self, text: str) -> None:
        """
        Convert the text to speech and play it.

        Args:
            text (str): The text to be converted to speech.

        Returns:
            None
        """
        subprocess.run(["say", "-o", os.path.join(os.getcwd(), 'Sound', 'prompt.aiff'), text])
        self.y, self.sr = librosa.load(self.output_file, sr=None)
        self._toggle_speech()

    def _toggle_speech(self) -> None:
        """
        Toggle the speech playback in a separate thread.

        Returns:
            None
        """
        threading.Thread(target=self._play).start()

    def _create_gif_section(self) -> None:
        """
        Create the section for displaying the GIF.

        Returns:
            None
        """
        gif_div_ctk = tk.Label(self, text='', bd=0, background='black')
        self._play_gif(gif_div_ctk, self._get_frames(os.path.join(os.getcwd(), 'Images', 'conviva-orb.gif')))
        gif_div_ctk.pack(expand=True)

    def _get_frames(self, img_path: str) -> list:
        """
        Get the frames from the GIF image.

        Args:
            img_path (str): The path to the GIF image.

        Returns:
            list: The frames of the GIF image.
        """
        frames = []
        try:
            with Image.open(img_path) as img:
                while True:
                    try:
                        img.seek(img.tell() + 1)
                        frames.append(img.copy())
                    except EOFError:
                        break
        except Exception as e:
            print("Error:", e)
        return frames

    def _play_gif(self, container: tk.Label, frames: list) -> None:
        """
        Play the GIF animation.

        Args:
            container (tk.Label): The label to display the GIF.
            frames (list): The frames of the GIF image.

        Returns:
            None
        """
        total_delay = 50
        for frame in frames:
            self.parent.after(total_delay, self._next_frame, frame, container, frames)
            total_delay += self.speed
        self.parent.after(total_delay, self._next_frame, frame, container, frames, True)

    def _next_frame(self, frame: Image, container: tk.Label, frames: list, restart: bool = False) -> None:
        """
        Display the next frame of the GIF animation.

        Args:
            frame (Image): The current frame to display.
            container (tk.Label): The label to display the frame.
            frames (list): The frames of the GIF image.
            restart (bool, optional): Whether to restart the animation. Defaults to False.

        Returns:
            None
        """
        if self.speaking:
            x = random.randint(200, 250)
        else:
            x = 200
        if restart:
            self.parent.after(1, self._play_gif, container, frames)
        photo_image = ImageTk.PhotoImage(frame.resize((x, x)))
        container.configure(image=photo_image)
        container.image = photo_image


class MenuBarEntries(tk.Menu):
    """
    A class to create and manage menu bar entries.

    Attributes:
        parent (tk.Tk): The parent window.

    Methods:
        file(): Define the File menu and its items.
        pages(): Define the Pages menu and its items.
        configuration(): Define the Configuration menu and its items.
        help(): Define the Help menu and its items.
        get_file_text(file_path: str): Read and return the text from the specified file.
        open_text_file(file_path: str = None): Open and display the text file content in a new panel.
        clear_text_file(file_path: str = None): Clear the content of the specified text file.
        clear_ingested_database(): Clear the ingested database after user confirmation.
        switch_page(page_index: int): Switch to the specified page index.
        get_and_set_first_page(current_idx: int): Get and set the first page based on the current index.
    """
    def __init__(self, parent: tk.Tk):
        """
        Initialize the MenuBarEntries class.

        Args:
            parent (tk.Tk): The parent window.
        """
        super().__init__(parent)
        self.parent = parent
        self.file()
        self.pages()
        self.configuration()
        self.help()
        self.parent.configure(menu=self)

    def file(self) -> None:
        """
        Define the File menu and its items.

        Returns:
            None
        """
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='Open Conversation Text File', command=self.open_text_file)
        file_menu.add_command(label='Open Summarised Text File', 
                              command=lambda file_path=os.path.join(os.getcwd(), 'Persistence Documents', 'summary_result.txt'): self.open_text_file(file_path=file_path))
        file_menu.add_command(label='Open Database Folder', 
                              command=lambda: filedialog.askdirectory(initialdir=os.path.join(os.getcwd(), 'Database'), title='Select A File'))
        file_menu.add_command(label='Open Models Folder', 
                              command=lambda: filedialog.askdirectory(initialdir=os.path.join(os.getcwd(), 'Models'), title='Select A File'))
        file_menu.add_separator()
        file_menu.add_command(label='Clear Database', command=self.clear_ingested_database)
        file_menu.add_command(label='Clear Summarised Text File', 
                              command=lambda file_path=os.path.join(os.getcwd(), 'Persistence Documents', 'summary_result.txt'): self.clear_text_file(file_path=file_path))
        file_menu.add_command(label='Clear Conversation Text File', command=self.clear_text_file)
        file_menu.add_separator()
        file_menu.add_command(label='Close / Exit / Quit', command=self.parent.quit)
        self.add_cascade(label='File', menu=file_menu)

    def pages(self) -> None:
        """
        Define the Pages menu and its items.

        Returns:
            None
        """
        pages_menu = tk.Menu(self, tearoff=False)
        pages_menu.add_command(label='Conviva Orb Interface', command=lambda page_index=0: self.switch_page(page_index))
        pages_menu.add_command(label='Conviva Chat Interface', command=lambda page_index=1: self.switch_page(page_index))
        pages_menu.add_separator()
        pages_menu.add_command(label='Text Based File Manipulation Interface', command=lambda page_index=2: self.switch_page(page_index))
        pages_menu.add_command(label='Conviva Mini-Youtube', command=lambda page_index=3: self.switch_page(page_index))
        self.add_cascade(label='Screens', menu=pages_menu)

    def configuration(self) -> None:
        """
        Define the Configuration menu and its items.

        Returns:
            None
        """
        configuration_menu = tk.Menu(self, tearoff=True)
       
        first_page_selection_menu = tk.Menu(configuration_menu, tearoff=False)

        self.ai_page = tk.BooleanVar(value=False)
        self.text_page = tk.BooleanVar(value=False)
        self.chat_page = tk.BooleanVar(value=False)
        self.youtube_page = tk.BooleanVar(value=False)

        first_page_selection_menu.add_checkbutton(label=' Conviva Orb Interface ', 
                                                  onvalue=True, 
                                                  offvalue=False, 
                                                  variable=self.ai_page,
                                                  command=lambda: self.get_and_set_first_page(current_idx=0))
        first_page_selection_menu.add_checkbutton(label=' Conviva Chat Interface ', 
                                                  onvalue=True, 
                                                  offvalue=False, 
                                                  variable=self.chat_page,
                                                  command=lambda: self.get_and_set_first_page(current_idx=1))
        first_page_selection_menu.add_checkbutton(label=' Text Based File Manipulation Interface ', 
                                                  onvalue=True, 
                                                  offvalue=False, 
                                                  variable=self.text_page,
                                                  command=lambda: self.get_and_set_first_page(current_idx=2))
        first_page_selection_menu.add_checkbutton(label=' Mini-Youtube ', 
                                                  onvalue=True, 
                                                  offvalue=False, 
                                                  variable=self.youtube_page,
                                                  command=lambda: self.get_and_set_first_page(current_idx=3))

        configuration_menu.add_cascade(label='Set First Page To: ', menu=first_page_selection_menu)
        self.add_cascade(label='Configuration', menu=configuration_menu)

    def help(self) -> None:
        """
        Define the Help menu and its items.

        Returns:
            None
        """
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='Open Documentation', command=lambda: DocumentationPanel(self.parent))
        self.add_cascade(label='Help', menu=help_menu)

    def get_file_text(self, file_path: str) -> list:
        """
        Read and return the text from the specified file.

        Args:
            file_path (str): The path to the file.

        Returns:
            list: The lines of text in the file.
        """
        with open(file_path, 'r') as fr:
            return fr.readlines()

    def open_text_file(self, file_path: str = None) -> None:
        """
        Open and display the text file content in a new panel.

        Args:
            file_path (str, optional): The path to the text file. Defaults to None.

        Returns:
            None
        """
        self.parent.summarize_button = ctk.CTkButton(self.parent)
        SummarizerPanel(self.parent, summarise=False).show_summary(self.get_file_text(file_path if file_path else os.path.join(os.getcwd(), 'Persistence Documents', 'conversation_history.txt')))

    def clear_text_file(self, file_path: str = None) -> None:
        """
        Clear the content of the specified text file.

        Args:
            file_path (str, optional): The path to the text file. Defaults to None.

        Returns:
            None
        """
        with open(file_path if file_path else os.path.join(os.getcwd(), 'Persistence Documents', 'conversation_history.txt'), 'w') as fw:
            fw.write('')
        Toast(self.parent, "File Cleared")

    def clear_ingested_database(self) -> None:
        """
        Clear the ingested database after user confirmation.

        Returns:
            None
        """
        if messagebox.askyesno('Clear Database?', 'Are You Sure That You Want To Clear The Database?'):
            FileChat().clear_database()
            Toast(self.parent, "Database Cleared")

    def switch_page(self, page_index: int) -> None:
        """
        Switch to the specified page index.

        Args:
            page_index (int): The index of the page to switch to.

        Returns:
            None
        """
        self.parent.current_page_idx = page_index
        self.parent.clear_page_frame()
        self.parent.load_page()

    def get_and_set_first_page(self, current_idx: int) -> None:
        """
        Get and set the first page based on the current index.

        Args:
            current_idx (int): The index of the current page.

        Returns:
            None
        """
        self.ai_page.set(False)
        self.chat_page.set(False)
        self.text_page.set(False)
        self.youtube_page.set(False)
        
        # Set the corresponding page to True
        if current_idx == 0:
            self.ai_page.set(True)
        elif current_idx == 1:
            self.chat_page.set(True)
        elif current_idx == 2:
            self.text_page.set(True)
        elif current_idx == 3:
            self.youtube_page.set(True)
        
        # Save the starting page index to a configuration file
        data = {"starting-page-index": current_idx}
        with open(os.path.join(os.getcwd(), "Json", "ai_config.json"), 'w') as aw:
            json.dump(data, aw, indent=4)
        logging.info(f"First Page set to {'Conviva Orb Interface' if current_idx == 0 else 'Conviva Chat Interface' if current_idx == 1 else 'Text Based File Manipulation Interface' if current_idx == 2 else 'Mini-Youtube' if current_idx == 3 else ''}")


class ChatBar(ctk.CTkTextbox):
    """
    A class representing a chat input bar with animated border and height adjustment.

    Attributes:
        parent (tk.Tk): The parent window.
        text (str): The text entered in the chat bar.
        width (int): The width of the chat bar.
        change (bool): The state indicating if the text has changed.
        height (int): The height of the chat bar.
        animate (bool): Whether the border animation is enabled.
        should_strip (bool): Whether the text should be stripped of newline characters.
        height_increased (bool): Whether the height has been increased.
        border_color (str): The border color of the chat bar.
    """

    def __init__(self, parent: tk.Tk, width: int = 600, height: int = 55, corner_radius: int = 20, 
                 border_width: int = 3, animate: bool = False):
        """
        Initialize the ChatBar class.

        Args:
            parent (tk.Tk): The parent window.
            width (int): The width of the chat bar. Defaults to 600.
            height (int): The height of the chat bar. Defaults to 55.
            corner_radius (int): The radius of the corners. Defaults to 20.
            border_width (int): The width of the border. Defaults to 3.
            animate (bool): Whether to animate the border. Defaults to False.
        """
        super().__init__(parent, width=width, height=height, fg_color=parent.SECONDARY_COLOR, 
                         border_color=parent.LESSER_COLOR, corner_radius=corner_radius, 
                         border_width=border_width, font=('Arial', 18))
        
        self.text = ''
        self.width = width
        self.change = False
        self.height = height
        self.parent = parent
        self.animate = animate
        self.should_strip = True
        self.height_increased = False
        self.border_color = parent.LESSER_COLOR

        # Bind events to methods
        self.bind('<Return>', self.get_text)
        self.bind('<Shift-Return>', self.shift_increase_height)
        
        # Start the border animation and assisted height adjustment
        self.assisted_increase_height()
        self.border_animation()
        self.focus()

    def get_text(self, e: tk.Event) -> str:
        """
        Get the text from the chat bar when the Enter key is pressed.

        Args:
            e (tk.Event): The event object.

        Returns:
            str: The text from the chat bar.
        """
        text = self.get("0.0", "end")
        self.delete("0.0", "end")
        self.change = True
        self.text = text
        self.height_increased = False
        return text

    def border_animation(self) -> None:
        """
        Animate the border color of the chat bar.

        Returns:
            None
        """
        if self.animate:
            self.change = not self.change
            if self.change:
                self.border_color = self.parent.LESSER_COLOR
            else:
                self.border_color = self.parent.AUXILIARY_COLOR
            self.configure(border_color=self.border_color)
            self.parent.after(500, self.border_animation)

    def shift_increase_height(self, e: tk.Event) -> None:
        """
        Increase the height of the chat bar when Shift + Enter is pressed.

        Args:
            e (tk.Event): The event object.

        Returns:
            None
        """
        self.configure(height=100)
        self.height_increased = True
        self.should_strip = False

    def assisted_increase_height(self) -> None:
        """
        Automatically increase the height of the chat bar based on the text length.

        Returns:
            None
        """
        current_text = self.get("1.0", "end-1c")
        if len(current_text) >= 80 or self.height_increased:
            self.configure(height=100)
        else:
            self.configure(height=55)
        self.parent.after(500, self.assisted_increase_height)


class ChatBubble(ctk.CTkLabel): 
    """
    A class representing a chat bubble with copy-to-clipboard functionality.

    Attributes:
        parent (tk.Widget): The parent widget.
        root (tk.Tk): The root window.
        text (str): The text to display in the chat bubble.
    """
    def __init__(self, parent: tk.Widget, root: tk.Tk, text: str = "Chat Bubble", fg_color: str = 'Green'):
        """
        Initialize the ChatBubble class.

        Args:
            parent (tk.Widget): The parent widget.
            root (tk.Tk): The root window.
            text (str): The text to display in the chat bubble. Defaults to "Chat Bubble".
            fg_color (str): The foreground color of the chat bubble. Defaults to 'Green'.
        """
        super().__init__(parent, text=text, fg_color=fg_color, corner_radius=20, anchor='e', wraplength=300, 
                         justify='left', padx=20, pady=10)
        self.text = text
        self.root = root
        self.parent = parent
        self.bind("<Double-Button-1>", self.copy_text)

    def get_height(self) -> int:
        """
        Get the height of the chat bubble.

        Returns:
            int: The height of the chat bubble.
        """
        self.update()
        h = self.winfo_reqheight()
        return h

    def copy_text(self, event: tk.Event) -> None:
        """
        Copy the text of the chat bubble to the clipboard when double-clicked.

        Args:
            event (tk.Event): The event object.

        Returns:
            None
        """
        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.text)
        Toast(self.root, 'Copied Successfully')


class SplashScreen(tk.Toplevel):
    """
    A class representing a splash screen window.

    Attributes:
        parent (tk.Tk): The parent window.
        size (tuple): The size of the splash screen.
        image_path (str): The path to the splash image.
        image (PIL.Image): The splash image.
        photo (ImageTk.PhotoImage): The photo image of the splash image.
        label (tk.Label): The label displaying the splash image.
    """
    def __init__(self, parent: tk.Tk):
        """
        Initialize the SplashScreen class.

        Args:
            parent (tk.Tk): The parent window.
        """
        super().__init__(parent)
        self.parent = parent
        self.size = (450, 450)
        self.overrideredirect(True)
        self.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.winfo_screenwidth()/2)-int(self.size[0]/2)}+"
                      f"{int(self.winfo_screenheight()/2)-int(self.size[1]/2)-50}")
        
        # Load and display the splash image
        self.image_path = os.path.join(os.getcwd(), 'Images', 'splash.jpg')
        self.image = Image.open(self.image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.label = tk.Label(self, image=self.photo)
        self.label.pack(expand=True)
        
        # Create and place a frame in the center of the splash screen
        tk.Frame(self, width=150, height=150, background=self.parent.PRIMARY_COLOR).place(
            x=int(self.size[0]/2), y=int(self.size[1]/2), anchor='center')
        logging.info("Conviva Opened")


class SummarizerPanel(tk.Toplevel):
    """
    A class representing a panel for summarizing text.

    Attributes:
        parent (tk.Tk): The parent window.
        summarise (bool): Whether to summarize the text.
        file_path (str): The file path for the text to be summarized.
        summarizing (bool): The state indicating if summarization is in progress.
        loading_frame (tk.Frame): The frame displaying the loading screen.
        canvas (tk.Canvas): The canvas displaying the loading animation.
        summary (tk.Text): The text widget displaying the summary.
    """
    def __init__(self, parent: tk.Tk, summarise: bool = True, file_path: str = None):
        """
        Initialize the SummarizerPanel class.

        Args:
            parent (tk.Tk): The parent window.
            summarise (bool): Whether to summarize the text. Defaults to True.
            file_path (str): The file path for the text to be summarized. Defaults to None.
        """
        super().__init__(parent, background=parent.SECONDARY_COLOR)
        global FileChat, YoutubeDownloader, Assistant, Functionalities, say, load_intents
        self.arc_id = 0
        self.text_id = 0
        self.loading_id = 0
        self.parent = parent
        self.summarise = summarise
        self.summarizing = False
        self.file_path = file_path
        self.overrideredirect(True)
        self.geometry(f"{int((self.parent.size[0]-100)/2)}x{self.parent.size[1]-50}+"
                      f"{int(self.parent.winfo_screenwidth()/2)-int(((self.parent.size[0]-100)-int((self.parent.size[0]-100)/2))/2)}+"
                      f"{int(self.parent.winfo_screenheight()/2)-int((self.parent.size[1]-100)/2)-50}")
        self.create_page()
        logging.info("Performed Summary")

    def close(self) -> None:
        """
        Close the summarizer panel.

        Returns:
            None
        """
        self.destroy()

    def summarize(self) -> None:
        """
        Perform the summarization of the text.

        Returns:
            None
        """
        self.parent.summarize_button.configure(state='disabled')
        if self.summarise:
            try:
                Functionalities(False, say).text_summary(file_path=self.file_path)
            except:
                print("Something Went Wrong")
                self.summarizing = False
                self.close()
                self.parent.summarize_button.configure(state='normal')
                return
            # Functionalities(False, say).text_summary(file_path=self.file_path)
            self.canvas.pack_forget()
            self.parent.summarize_button.configure(state='normal')
            time.sleep(0.5)
            self.show_summary()

    def create_page(self) -> None:
        """
        Create the loading page for the summarizer panel.

        Returns:
            None
        """
        self.loading_frame = tk.Frame(self, background=self.parent.AUXILIARY_COLOR)
        self.summarize_loader()
        self.loading_frame.pack(fill='both', expand=True)

    def show_summary(self, other_text: str = None) -> None:
        """
        Display the summary of the text.

        Args:
            other_text (str): Alternative text to display. Defaults to None.

        Returns:
            None
        """
        self.summary = tk.Text(self.loading_frame, padx=10, pady=10, wrap='word', height=400)
        for line in self.get_summarized_text() if other_text == None else other_text:
            self.summary.insert('end', line)
        self.summary.configure(state='disabled')
        ctk.CTkButton(self.loading_frame, text='Close', fg_color=self.parent.PRIMARY_COLOR, 
                      corner_radius=20, hover_color=self.parent.SECONDARY_COLOR, 
                      command=self.close).pack(pady=10, expand=True)
        self.summary.pack(fill='both', expand=True)

    def summarize_loader(self) -> None:
        """
        Display the loading screen while the summarization is in progress.

        Returns:
            None
        """
        self.canvas = tk.Canvas(self.loading_frame, background=self.parent.AUXILIARY_COLOR, highlightthickness=0)
        self.summarizing = True
        self.loading_screen(100, start=0, extention_count=0, radius=70, width=10, text='Summarising')
        self.canvas.pack(fill='both', expand=True) if self.summarise else ''
        threading.Thread(target=self.summarize).start()

    def get_summarized_text(self) -> list:
        """
        Get the summarized text from the file.

        Returns:
            list: The summarized text.
        """
        with open(os.path.join(os.getcwd(), 'Persistence Documents', 'summary_result.txt'), 'r') as st:
            return st.readlines()

    def loading_screen(self, extent: int, start: int = 0, extention_count: int = 0, radius: int = 80, width: int = 5, text: str = 'Summarizing') -> None:
        """
        Display the loading animation on the screen.

        Args:
            extent (int): The extent of the arc.
            start (int): The starting angle of the arc. Defaults to 0.
            extention_count (int): The count of extensions. Defaults to 0.
            radius (int): The radius of the arc. Defaults to 80.
            width (int): The width of the arc. Defaults to 5.
            text (str): The text to display on the screen. Defaults to 'Summarizing'.

        Returns:
            None
        """
        color = self.parent.PRIMARY_COLOR
        self.canvas.delete(self.arc_id)
        self.canvas.delete(self.text_id)
        if self.summarizing:
            if extention_count % 600 == 0:
                extent = random.randint(90, 270)
            else:
                extent = extent
            center_x = int(self.parent.size[0]/2)-240
            center_y = int(self.parent.size[1]/2)
            x1 = center_x - radius
            y1 = center_y - radius
            x2 = center_x + radius
            y2 = center_y + radius
            self.arc_id = self.canvas.create_arc((x1, y1, x2, y2), outline=color, width=width, style='arc', start=start, extent=extent)
            start += 10
            extention_count += 5
            self.loading_id = self.after(25, self.loading_screen, extent, start, extention_count, radius, width, text)
            self.text_id = self.canvas.create_text(int(self.parent.size[0]/2)-240, int(self.parent.size[1]/2), anchor='center', text=text, font=('Arial Black', 15))
        else:
            self.after_cancel(self.loading_id)


class DocumentationPanel(tk.Toplevel):
    """
    A class to create and manage a documentation panel window.

    Attributes:
        parent (tk.Tk): The parent window.
        html_label (HTMLLabel): The widget to display HTML content.

    Methods:
        open_file(): Open the markdown file and convert its content to HTML.
        display_html(html_content: str): Display the HTML content in the HTMLLabel widget.
    """

    def __init__(self, parent: tk.Tk):
        """
        Initialize the DocumentationPanel class.

        Args:
            parent (tk.Tk): The parent window.
        """
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        
        # Set the geometry of the window.
        self.geometry(f"{int((self.parent.size[0]-100)/2)}x{self.parent.size[1]-50}+"
                      f"{int(self.parent.winfo_screenwidth()/2)-int(((self.parent.size[0]-100)-int((self.parent.size[0]-100)/2))/2)}+"
                      f"{int(self.parent.winfo_screenheight()/2)-int((self.parent.size[1]-100)/2)-50}")
        
        frame = tk.Frame(self, background="black", highlightthickness=0, highlightcolor="black")
        frame.pack(expand=True, fill="both")

        self.html_label = HTMLLabel(frame, wrap='word', background='black', padx=10, pady=10)
        self.html_label.pack(expand=True, fill='both')

        # Add a close button
        ctk.CTkButton(frame, text="Close", fg_color=self.parent.PRIMARY_COLOR, 
                      corner_radius=20, hover_color=self.parent.PRIMARY_COLOR, 
                      command=self.destroy).pack(pady=10)

        # Open and display the markdown file
        self.open_file()
        logging.info("Documentation Opened")

    def open_file(self) -> None:
        """
        Open the markdown file and convert its content to HTML.

        Returns:
            None
        """
        file_path = os.path.join(os.getcwd(), 'Documents', 'file.md')
        file_path = os.path.join(os.getcwd(), 'User-Manual.md')
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
            html_content = markdown2.markdown(markdown_content)
            html_content_with_style = f'<div style="color: white;">{html_content}</div>'
            self.display_html(html_content_with_style)

    def display_html(self, html_content: str) -> None:
        """
        Display the HTML content in the HTMLLabel widget.

        Args:
            html_content (str): The HTML content to be displayed.

        Returns:
            None
        """
        self.html_label.set_html(html_content)


class FloatingButtonList(ctk.CTkLabel):
    """
    A class representing a floating button list.

    Attributes:
        parent (tk.Tk): The parent window.
        orientation (str): The orientation of the button list ('vertical' or 'horizontal').
        functions (list): The list of functions to be called when buttons are clicked.
        i (int): The index of the current button.
        i_id (int): The ID of the current button.
        photos (list): The list of button images.
        labels (list): The list of button labels.
        label_toggle (bool): The toggle state of the labels.
        image_names (list): The list of image names for the buttons.
    """

    def __init__(self, parent: tk.Tk, orientation: str = 'vertical', functions: list = []) -> None:
        """
        Initializes the FloatingButtonList instance.

        Args:
            parent (tk.Tk): The parent window.
            orientation (str, optional): The orientation of the button list ('vertical' or 'horizontal'). Defaults to 'vertical'.
            functions (list, optional): The list of functions to be called when buttons are clicked. Defaults to [].
        """
        super().__init__(parent, text='\u2630'.strip(), font=('Arial Black', 45), fg_color=parent.SECONDARY_COLOR, corner_radius=200)
        self.i = 0
        self.i_id = 0
        self.photos = []
        self.labels = []
        self.parent = parent
        self.label_toggle = False
        self.functions = functions
        self.orientation = orientation
        self.bind("<Button-1>", self.open_other_buttons)
        self.image_names = ["ai", "chat", "text", "mini"]
        self.place(x=self.parent.size[0]-50, y=50, anchor='ne')

    def place_buttons(self) -> None:
        """
        Places the floating buttons on the screen.
        """
        if self.i < 4: 
            self.label_button = ctk.CTkLabel(self.parent, image=self.get_button_image(self.image_names[self.i]), corner_radius=10, text='', fg_color=self.parent.AUXILIARY_COLOR)
            self.label_button.bind("<Button-1>", lambda event, id=self.i: self.open_next_page(event, id))
            if self.orientation == 'horizontal':
                self.label_button.place(x=(self.parent.size[0]-310 + self.i * 100), y=70, anchor='ne')
            else:
                self.label_button.place(x=self.parent.size[0]-50, y=(150 + self.i * 100), anchor='ne')
            self.labels.append(self.label_button)
            self.i += 1
            self.i_id = self.parent.after(25, self.place_buttons)                
        else:
            self.after_cancel(self.i_id)

    def clear_buttons(self) -> None:
        """
        Clears the floating buttons from the screen.
        """
        for i in self.labels:
            i.place_forget()
        self.i = 0
            
    def open_other_buttons(self, e: tk.Event) -> None:
        """
        Opens or closes the floating buttons.

        Args:
            e (tk.Event): The event triggering the method.
        """
        if not self.label_toggle:
            self.place_buttons()
            self.label_toggle = not self.label_toggle
        else:
            self.clear_buttons()
            self.label_toggle = not self.label_toggle

    def open_next_page(self, e: tk.Event, id: int) -> None:
        """
        Opens the next page based on the button clicked.

        Args:
            e (tk.Event): The event triggering the method.
            id (int): The ID of the button clicked.
        """
        self.place_forget()
        self.clear_buttons()
        self.functions[id]()

    def get_button_image(self, image_name: str) -> ImageTk.PhotoImage:
        """
        Retrieves the image for the button.

        Args:
            image_name (str): The name of the image file.

        Returns:
            ImageTk.PhotoImage: The image for the button.
        """
        image_path = os.path.join(os.getcwd(), 'Images', f'{image_name}.png')
        image = Image.open(image_path).resize((40, 40))
        self.photo = ImageTk.PhotoImage(image)
        self.photos.append(self.photo)
        return self.photo


class ChatInterFace(ctk.CTkScrollableFrame):
    """
    A class representing a chat interface with scrollable chat history.

    Attributes:
        parent (tk.Tk): The parent window.
        root (Conviva): The root application instance.
        chat_bar (ChatBar): The chat bar widget.
        inner_canvas (tk.Canvas): The inner canvas of the scrollable frame.
        background_photo (ImageTk.PhotoImage): The background image of the canvas.
        intent (str): The intent for processing user input.
        functionality (str): The functionality for processing user input.
        intent_function_mappings (dict): Mapping of intents to functions.
        image_list (list): List to store images.
    """

    def __init__(self, parent: tk.Tk, root: Conviva, chat_bar: ChatBar) -> None:
        """
        Initialize the ChatInterface class.

        Args:
            parent: The parent widget.
            root: The root window.
            chat_bar: The chat bar widget.
        """
        super().__init__(parent, width=890, height=300, border_width=0, fg_color=root.SECONDARY_COLOR)
        global FileChat, YoutubeDownloader, Assistant, Functionalities, say, load_intents
        self.pack()
        self.root = root
        self.parent = parent
        self.image_list = []  # List to store images
        self.chat_bar = chat_bar
        self.inner_canvas = self._parent_canvas  # Accessing the inner canvas of the scrollable frame
        self.background_photo = ImageTk.PhotoImage(Image.open(os.path.join(os.getcwd(), 'Images', 'frame-bg.jpg')))

        # Configure the inner canvas
        self.inner_canvas.configure(yscrollcommand=self._scrollbar.set, scrollregion=self.inner_canvas.bbox('all'))
        self.inner_canvas.yview_moveto('1.0')
        self.inner_canvas.configure(highlightthickness=0)
        self._scrollbar.configure(fg_color=self.root.AUXILIARY_COLOR, button_color=self.root.LESSER_COLOR)

        self.intent = self.root.intent  # Intent for processing user input
        self.functionality = self.root.functionality  # Functionality for processing user input
        self.intent_function_mappings = self.root.intent_function_mappings  # Mapping of intents to functions

        self.check_if_text_has_been_entered()

    def check_if_text_has_been_entered(self, h: int = 100, image_y_pos: int = 310) -> None:
        """
        Check if text has been entered in the chat bar.

        Args:
            h: The height.
            image_y_pos: The position of the image.

        Returns:
            None
        """
        # Create a background image for the canvas
        self.inner_canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        if self.chat_bar.change:
            # Get the text from the chat bar
            text = self.chat_bar.text.strip('\n') if self.chat_bar.should_strip else self.chat_bar.text
            with open(os.path.join(os.getcwd(), "Persistence Documents", "conversation_history.txt"), 'a') as ch:
                ch.write(f"\t\t\t{text}\n")
            self.chat_bar.should_strip = True
            # Create a chat bubble for the user's text
            text_bubble = ChatBubble(self.inner_canvas, self.root, text=text, fg_color=self.root.LESSER_COLOR)
            height = text_bubble.get_height()
            self.inner_canvas.create_window(850, h, anchor='ne', window=text_bubble)
            self.chat_bar.change = False
            # Get the response from the assistant
            response, add_ons, tag = Assistant(self.intent, False, say, intent_mapping=self.intent_function_mappings).get_response(text)
            print_add_ons, say_add_ons = add_ons or ("", "")
            response = response + print_add_ons
            # Create a chat bubble for the assistant's response
            with open(os.path.join(os.getcwd(), "Persistence Documents", "conversation_history.txt"), 'a') as ch:
                ch.write(f"{response}\n\n")
            response_bubble = ChatBubble(self.inner_canvas, self.root, text=response, fg_color=self.root.AUXILIARY_COLOR)
            response_height = response_bubble.get_height() * len(response.split("\n"))
            self.inner_canvas.create_window(50, h + height + 100, anchor='nw', window=response_bubble)
            h += 100 + height + response_height
            self.parent.update()
            self.inner_canvas.configure(scrollregion=self.inner_canvas.bbox("all"))
            self._scrollbar.set(*self.inner_canvas.yview())
            self.inner_canvas.yview_moveto('1.0')
            self._scrollbar.update()
            self.inner_canvas.update_idletasks()
            # Add background images if necessary
            if image_y_pos < h:
                self.inner_canvas.create_image(0, image_y_pos, anchor="nw", image=self.background_photo)
                image_y_pos += 310
            if h - image_y_pos in range(800, 10000):
                for i in range(10):
                    self.inner_canvas.create_image(0, image_y_pos, anchor="nw", image=self.background_photo)
                    image_y_pos += 310
        # Check again after a delay
        self.parent.after(500, self.check_if_text_has_been_entered, h, image_y_pos)


class AudioOrVideoDownloadScreen(tk.Toplevel):
    """
    A class representing a screen for downloading audio or video files.

    Attributes:
        parent (tk.Tk): The parent window.
        id (int): The id of the item being downloaded.
        image (Image): The image representing the item being downloaded.
        data (dict): The data about the item being downloaded.
        progress (tk.DoubleVar): A Tkinter variable to track the download progress.
        frame (tk.Frame): The main frame of the screen.
        img (ImageTk.PhotoImage): The image to display on the screen.
        video_details_label (ctk.CTkLabel): A label to display details about the video.
        mp4 (ctk.CTkButton): A button to download the video in MP4 format.
        mp3 (ctk.CTkButton): A button to download the audio in MP3 format.
        flood (Floodgauge): A progress bar widget.
        download_frame (tk.Frame): A frame to contain the download indicators.
    """

    def __init__(self, parent: tk.Tk, id: int, image: Image, data: dict) -> None:
        """
        Initializes the AudioOrVideoDownloadScreen instance.

        Args:
            parent (tk.Tk): The parent window.
            id (int): The id of the item being downloaded.
            image (Image): The image representing the item being downloaded.
            data (dict): The data about the item being downloaded.
        """
        super().__init__(parent)
        self.parent = parent
        self.image = image
        self.data = data
        self.id = id
        self.overrideredirect(True)
        self.geometry(f"{self.parent.size[0]-100}x{self.parent.size[1]-100}+{int(self.parent.winfo_screenwidth()/2)-int((self.parent.size[0]-100)/2)}+{int(self.parent.winfo_screenheight()/2)-int((self.parent.size[1]-100)/2)-50}")

        # Bind labels to lift the window when clicked
        for _, image_label, title_label, duration_label in self.parent.yt_search_result_frame_details:
            title_label.unbind('<Button-1>')
            image_label.unbind('<Button-1>')
            duration_label.unbind('<Button-1>')
            
            title_label.bind('<Button-1>', self.lift_window)
            image_label.bind('<Button-1>', self.lift_window)
            duration_label.bind('<Button-1>', self.lift_window)

        self.place_screen_content()

    def close(self) -> None:
        """
        Closes the download screen.
        """
        self.parent.bind_items()
        self.destroy()

    def failure_message(self) -> None:
        """
        Displays a failure message when the download fails.
        """
        self.flood.pack_forget()
        self.download_frame.pack_forget()
        failure = ctk.CTkLabel(self, text=f"Sorry, Failed To Download {self.parent.manage_break(self.parent.break_text(self.data[self.id]['title'], 30))}".replace('\n', ' '), font=('Arial Black', 15), fg_color=self.parent.PRIMARY_COLOR, pady=10, text_color='#FF9999')
        failure.configure(fg_color=self.parent.PRIMARY_COLOR, text_color='#FF9999')
        failure.pack(side='bottom', fill='both')
        self.after(6000, lambda: self.remove_failure_message(failure))

    def progress_hook(self, d: dict) -> None:
        """
        A callback function to update the download progress.

        Args:
            d (dict): The download status dictionary.
        """
        try:
            if d['status'] == 'downloading':
                percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str'])
                if percent_str.strip().endswith('%'):
                    self.progress.set(float(float(percent_str.replace('%', ''))))
        except:
            raise ValueError

    def lift_window(self, event: tk.Event) -> None:
        """
        Brings the download screen to the front.

        Args:
            event (tk.Event): The event triggering the method.
        """
        self.lift()

    def place_screen_content(self) -> None:
        """
        Places the content on the download screen.
        """
        self.download_frame = tk.Frame(self)
        video_details = f"Title:\t{self.data[self.id]['title']}\n\nDuration:\t{self.data[self.id]['audio_length']}\n\nChannel:\t{self.data[self.id]['channel_name']}\n\nUploaded:\t{self.data[self.id]['upload_date']}"
        
        self.frame = tk.Frame(self, background=self.parent.PRIMARY_COLOR)
        self.frame.configure(background=self.parent.PRIMARY_COLOR)

        self.img = self.parent.fetch_image_from_internet(self.data[self.id]['largest_thumbnail'], target_width=350)
        
        ctk.CTkButton(self.frame, text='\u00D7', command=self.close, fg_color=self.parent.PRIMARY_COLOR, font=('Arial', 30), hover_color=self.parent.SECONDARY_COLOR).place(relx=1, rely=0, anchor='ne', relwidth=0.08)
        
        tk.Label(self.frame, image=self.img, background='white', width=355, height=201).pack(expand=True, pady=15)

        self.video_details_label = ctk.CTkLabel(self.frame, text=video_details, justify='left', fg_color=self.parent.PRIMARY_COLOR)
        self.video_details_label.pack(expand=True)

        self.mp4 = ctk.CTkButton(self.frame, text='MP4', text_color=self.parent.LESSER_COLOR, fg_color=self.parent.PRIMARY_COLOR, font=('Arial', 17), hover_color=self.parent.SECONDARY_COLOR, corner_radius=10, border_color=self.parent.LESSER_COLOR, border_width=3, width=30, command=lambda type='Video': self.place_download_indicators(type=type))
        self.mp4.pack(side='left', expand=True, pady=20, ipady=15)

        ctk.CTkButton(self.frame, text='Watch Online', text_color=self.parent.LESSER_COLOR, fg_color=self.parent.PRIMARY_COLOR, font=('Arial', 17), hover_color=self.parent.SECONDARY_COLOR, corner_radius=10, border_color=self.parent.LESSER_COLOR, border_width=3, command=lambda link=self.data[self.id]['url']: webbrowser.open(link)).pack(side='left', expand=True, pady=20, ipady=15)
        
        self.mp3 = ctk.CTkButton(self.frame, text='MP3', text_color=self.parent.LESSER_COLOR, fg_color=self.parent.PRIMARY_COLOR, font=('Arial', 17), hover_color=self.parent.SECONDARY_COLOR, corner_radius=10, border_color=self.parent.LESSER_COLOR, border_width=3, width=30, command=lambda type='Audio': self.place_download_indicators(type=type))
        self.mp3.pack(side='left', expand=True, pady=20, ipady=15)
        
        self.frame.pack(expand=1, fill='both')

    def download(self, link: str, type: str) -> None:
        """
        Handles the download process of the audio or video.

        Args:
            link (str): The URL of the item to be downloaded.
            type (str): The type of download ('Audio' or 'Video').
        """
        self.mp4.configure(state='disabled')
        self.mp3.configure(state='disabled')
        downloader = YoutubeDownloader(False, say)
        if type == 'Video':
            video = downloader.download_video(link=link, progress_hook=self.progress_hook)
            if video == 'Success':
                self.success_message(type)
            else:
                self.failure_message()
        else:
            audio = downloader.download_video_audio_aka_music(link=link, progress_hook=self.progress_hook)
            if audio == 'Success':
                self.success_message(type)
            else:
                self.failure_message()
        self.mp4.configure(state='enabled')
        self.mp3.configure(state='enabled')

    def success_message(self, type: str) -> None:
        """
        Displays a success message when the download completes successfully.

        Args:
            type (str): The type of download ('Audio' or 'Video').
        """
        self.flood.pack_forget()
        self.download_frame.pack_forget()
        success = ctk.CTkLabel(self, text=f"{self.parent.manage_break(self.parent.break_text(self.data[self.id]['title'], 30))} {type} Downloaded Successfully".replace('\n', ' '), font=('Arial Black', 15), fg_color=self.parent.PRIMARY_COLOR, pady=10, text_color='#99FF99')
        success.configure(fg_color=self.parent.PRIMARY_COLOR, text_color='#99FF99')
        success.pack(side='bottom', fill='both')
        self.after(6000, lambda: self.remove_success_message(success))

    def remove_success_message(self, success: ctk.CTkLabel) -> None:
        """
        Removes the success message from the screen.

        Args:
            success (ctk.CTkLabel): The label displaying the success message.
        """
        success.pack_forget()

    def remove_failure_message(self, failure: ctk.CTkLabel) -> None:
        """
        Removes the failure message from the screen.

        Args:
            failure (ctk.CTkLabel): The label displaying the failure message.
        """
        failure.pack_forget()

    def place_download_indicators(self, type: str = None) -> None:
        """
        Places the download indicators on the screen.

        Args:
            type (str, optional): The type of download ('Audio' or 'Video'). Defaults to None.
        """
        from ttkbootstrap.widgets import Floodgauge
        self.frame.configure(background=self.parent.PRIMARY_COLOR)
        self.video_details_label.configure(fg_color=self.parent.PRIMARY_COLOR, text_color='white')
        self.download_frame.configure(background=self.parent.PRIMARY_COLOR)
        self.progress = tk.DoubleVar(value=0)
        self.flood = Floodgauge(self.download_frame, mask='{}%', maximum=100, font=('Arial Black', 15), variable=self.progress)
        self.flood.pack(fill='x', padx=50, pady=10)
        threading.Thread(target=self.download, args=(self.data[self.id]["url"], type)).start()
        self.download_frame.pack(side='bottom', fill='both')





def main():
    try:
        Conviva('Conviva', (900, 600))
    except Exception as e:
        print(f"Something happened {e}")









if __name__ == '__main__':
    # main()
    Conviva('Conviva', (900, 600))


# source myenv/bin/activate  # macOS/Linux
# myenv\Scripts\activate      # Windows    for creating/reusing a virtual environment



# Downloads (Audio/Video)