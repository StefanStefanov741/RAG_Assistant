import tkinter as tk
from threading import Thread
import queue
from Database.chromadb_functions import load_database_from_dir
from Bots.openai_bot import OpenAI_GPT_Bot
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database folder and loading
db_folder_path = "Output"

def contains_sqlite3_file(folder_path):
    return any(file.endswith('.sqlite3') for file in os.listdir(folder_path))

if contains_sqlite3_file(db_folder_path):
    db = load_database_from_dir(db_folder_path)
    if not db:
        raise ValueError("Error loading the database!")
else:
    raise FileNotFoundError("No database was found at the specified location!")

def query_database(query_text, db_folder, k=5):
    """
    Queries the ChromaDB database to retrieve the k most similar chunks.
    """
    db = load_database_from_dir(db_folder)
    if db is None:
        return []
    results = db.similarity_search(query_text, k=k)
    if not results:
        return []
    extracted_texts = [doc.page_content for doc in results]
    return extracted_texts

# Bot setup
template = """You are an assistant that answers questions based strictly on the context provided below.
If the question is not directly answerable from the provided context, simply respond with "I don't know." 
Do not make up answers or use your pre-trained knowledge to answer the question.
Do not ask follow-up questions, only provide answers.
Answer the question directly, without any introductory phrases or explanations. 

Context:
=========
{context}
=========

Question:
"""


my_bot = OpenAI_GPT_Bot(model="gpt-4o-mini",temperature=0.7)

class RAGBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RAG Bot Chat")
        self.root.geometry("1280x720")
        self.root.configure(bg="#212121")

        # Queue for communication between threads
        self.queue = queue.Queue()

        # Frame for chat display
        self.chat_frame = tk.Frame(root, bg="#212121", padx=10, pady=10)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        # Chat display area
        self.chat_area = tk.Text(
            self.chat_frame, wrap=tk.WORD, state='disabled', width=80, height=25,
            font=("Arial", 12), bg="#303030", fg="#ffffff", highlightthickness=0, borderwidth=0
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # Frame for user input
        self.input_frame = tk.Frame(root, bg="#212121", padx=10, pady=10)
        self.input_frame.pack(fill=tk.X)

        # User input field
        self.input_field = tk.Entry(
            self.input_frame, font=("Arial", 14), width=50, bg="#5c5c5c", fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.input_field.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

        # K value input
        self.k_frame = tk.Frame(self.input_frame, bg="#212121")
        self.k_frame.pack(side=tk.RIGHT, padx=5)

        # Label "K: "
        self.k_label = tk.Label(
            self.k_frame, text="📄", font=("Arial", 12), bg="#212121", fg="#ffffff"
        )
        self.k_label.pack(side=tk.LEFT, padx=(0, 5))

        # Number field (to the right)
        self.number_field = tk.Entry(
            self.k_frame, font=("Arial", 12), width=5, bg="#5c5c5c", fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.number_field.insert(0, "5")
        self.number_field.pack(side=tk.LEFT, padx=(0, 5))
        self.number_field.bind("<FocusOut>", self.on_number_field_focus_out)

        # Send button
        self.send_button = tk.Button(
            self.k_frame, text="Send", font=("Arial", 12), bg="#0a6194", fg="#ffffff",
            command=self.ask_bot
        )
        self.send_button.pack(side=tk.LEFT)

        # Bind Enter key to send message
        self.input_field.bind("<Return>", lambda event: self.ask_bot())

        # Start the background thread that will process the queue
        self.process_queue()

    def on_number_field_focus_out(self, event):
        """Ensure number field always has a valid value when losing focus."""
        if self.number_field.get().strip() == "":
            self.number_field.insert(0, "5")  # Reset to 5 if empty

    def ask_bot(self):
        user_input = self.input_field.get().strip()
        user_k = self.number_field.get()

        # Start a separate thread for database query
        if user_input:
            self.display_message(f"🧑: {user_input}", user=True)
            self.input_field.delete(0, tk.END)

            Thread(target=self.query_database_and_respond, args=(user_input, int(user_k))).start()

    def query_database_and_respond(self, query_text, k):
        """Run the query and process the response in a separate thread."""
        extracted_texts = query_database(query_text, db_folder_path, k)
        processed_context = "\n".join(extracted_texts)
        full_context = self.combine_context(processed_context)

        # Request bot response and put the result into the queue
        bot_response = self.get_bot_response(query_text, full_context)
        self.queue.put(bot_response)

    def combine_context(self, retrieved_context):
        """Combine template and retrieved context."""
        return template.format(context=retrieved_context)

    def get_bot_response(self, user_input, full_context):
        """Get the response from the bot."""
        try:
            bot_response = str(my_bot.ask(question=user_input, context=full_context))
        except Exception as e:
            bot_response = f"Error: {str(e)}"
        return bot_response

    def process_queue(self):
        """Process the queue in the main thread."""
        try:
            while True:
                bot_response = self.queue.get_nowait()
                self.display_message(f"🤖: {bot_response}", user=False)
        except queue.Empty:
            pass
        # Repeat after 100ms
        self.root.after(100, self.process_queue)

    def display_message(self, message, user=False):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n\n", ("user" if user else "bot",))
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

        self.chat_area.tag_config("user", foreground="#8bc34a")
        self.chat_area.tag_config("bot", foreground="#ffffff")

if __name__ == "__main__":
    root = tk.Tk()
    app = RAGBotApp(root)
    root.mainloop()