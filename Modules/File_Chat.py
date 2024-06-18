import os 
import torch
import shutil
import logging
import warnings
import requests
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFacePipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.output_parsers.rail_parser import GuardrailsOutputParser
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, PDFMinerLoader, TextLoader

logging.getLogger().addHandler(logging.NullHandler())
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

class FileChat:
    """
    A class for interacting with files using language models and embedding-based retrieval.

    Attributes:
        KEY (str): The HuggingFace API key loaded from the environment.
        embeddings (SentenceTransformerEmbeddings): The embeddings model used for text embeddings.
        db (Chroma): The Chroma database loaded from the embeddings.
    """
    
    def __init__(self):
        """Initialize the FileChat class."""
        self.KEY = os.getenv('HUGGINGFACE_KEY')
        self.embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
        self.db = self.load_embedding()

    def chat(self):
        """Interact with the user to manage and chat with files."""
        while True:
            choices = "Choose One to Prepare pdf files for chatting \nChoose Two to Chat with files \nChoose Three View all files \nChoose Four to Exit"
            print(choices)
            choice = input("...: ")
            print()
            if choice == '2':
                text = ''
                while True: 
                    text = input('\nWhat would you like to know: ')
                    if text.lower() == 'x':
                        break
                    instruction = { "query": text }
                    print("\n\n\n", self.process_response(instruction), "\n")
            elif choice == '1':
                confirmation = input("Please are you sure that that there has been a new file added (Y/n) ").lower()
                if confirmation == "y": 
                    self.ingest()
                    print('Files Prepared\n')
                else:
                    print('please add a new file first, before preparing file, so as to prevent redundancy.\n')
            elif choice == '3':
                i = 0
                for root, docs, files in os.walk('Documents'):
                    for file in files:
                        i += 1
                        print(f"{i}. {file}")
                print()
            else:
                break

    def ingest(self):
        """Ingest new files into the Chroma database."""
        for root, docs, files in os.walk('Documents'):
            for file in files:
                if file.endswith('.pdf'):
                    print(file)
                    loader = PDFMinerLoader(os.path.join(root, file))
                elif file.endswith('.txt'):
                    print(file)
                    loader = TextLoader((os.path.join(root, file)), encoding='utf-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        db = Chroma.from_documents(texts, self.embeddings, persist_directory='./db')
        db = None

    def qa_llm(self) -> RetrievalQA:
        """
        Load the LLM and set up a retrieval-based QA system.

        Returns:
            RetrievalQA: The retrieval-based QA system.
        """
        llm = self.load_llm()
        retriever = self.db.as_retriever()
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=retriever,
            return_source_documents=True
        )

    def load_llm(self) -> HuggingFacePipeline:
        """
        Load the LLM for text generation.

        Returns:
            HuggingFacePipeline: The loaded HuggingFacePipeline.
        """
        CHECKPOINT = './Models/LaMini' if os.path.exists('./Models/LaMini') else "MBZUAI/LaMini-T5-738M"
        TOKENIZER = AutoTokenizer.from_pretrained(CHECKPOINT, token=self.KEY)
        BASE_MODEL = AutoModelForSeq2SeqLM.from_pretrained(
            CHECKPOINT,
            device_map="auto",
            torch_dtype=torch.float32,
            token=self.KEY,
            offload_folder="Models/ModelOffloader"
        )
        if not os.path.exists('./Models/LaMini'):
            TOKENIZER.save_pretrained('./Models/LaMini')
            BASE_MODEL.save_pretrained('./Models/LaMini')
        return HuggingFacePipeline(pipeline=pipeline(
            "text2text-generation",
            model=BASE_MODEL,
            max_length=256,
            tokenizer=TOKENIZER,
            do_sample=True,
            temperature=0.3,
            top_p=0.95
        ))

    def search_DB(self) -> list:
        """
        Search the Chroma database.

        Returns:
            list: The search results.
        """
        return self.db.similarity_search_with_score(input('search for... '), k=2)

    def clear_database(self):
        """Clear the Chroma database."""
        db_directory = './db'
        if os.path.exists(db_directory):
            shutil.rmtree(db_directory)
        os.makedirs(db_directory)

    def load_embedding(self) -> Chroma:
        """
        Load the embeddings from the Chroma database.

        Returns:
            Chroma: The loaded Chroma database.
        """
        return Chroma(persist_directory='./db', embedding_function=self.embeddings)

    def basic_ingest(self, file_path: str) -> bool:
        """
        Ingest a single file into the Chroma database.

        Args:
            file_path (str): The path to the file to be ingested.

        Returns:
            bool: True if the ingestion is successful, False otherwise.
        """
        if file_path.endswith('.pdf'):
            loader = PDFMinerLoader(file_path)
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        try:
            Chroma.from_documents(texts, self.embeddings, persist_directory='./db')
            return True
        except:
            return False

    def process_response(self, instruction: dict) -> str:
        """
        Process a user query and return the response from the LLM.

        Args:
            instruction (dict): The instruction containing the query.

        Returns:
            str: The generated response from the LLM.
        """
        try:
            qa = self.qa_llm()
            generated_text = qa(instruction)
            return generated_text["result"]
        except (requests.exceptions.ConnectionError, Exception) as e:
            return str(e)




# f = FileChat()
# f.basic_ingest('/Users/mac/Desktop/Ai/Documents/Work.txt')