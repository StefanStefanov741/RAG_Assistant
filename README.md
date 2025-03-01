🚀 RAG Chatbot Assistant

This repository is connected to an internship project I did at Maastricht University. 
The goal was finding the best solution posible to creating a RAG bot system that can assist researchers in science fields.

📄More information about the project you can find in the "Project Report.pdf" file.

📌Prerequisites to be able to run the RAG Charbot system:
Docker - It is used to host a parsing service locally that takes care of extracting the information from your files and return them in json format for storing.

Tessaract-ocr - Needed only if you plan to run the parsing code locally without docker, since otherwise the docker container will install tessaract-ocr inside it upon setup.

Poppler-utils - Needed only if you plan to run the parsing code locally without docker, since otherwise the docker container will install poppler-utils inside it upon setup.

Python 3.10 environment in case you want to also run the parsing code locally without docker (to install packages inside ./ParsingService/parsing-requirements.txt), otherwise you can use newer versions of python (Tested up to Python 3.13) to install the packages in (client-requirements.txt) that are needed to create a database from the recieved json data from the docker service as well as run the gui that will allow you to chat with the bot connected to the local vector store.

📦To install the packages needed on the client side (running the gui and creating the database) use:
pip install -r "client-requirements.txt"

📦To install the packages for parsing locally on your machine in case you want to test them out seperately (not by using the docker container service) you need to install the packages from parsing-requirements.txt, but before you do so make sure to uncomment the last backage for python-magic-bin (windows) or python-magic (linux).
Comment that package out again after, to prevent issues arising from the docker container setup.

⚙️To setup the RAG bot yourself you can follow these steps:
After installing docker, open a Terminal inside the ParsingService directory and run the command "docker-compose up"
Once it has finished you would have to make sure to run the container every time you want to use the service to parse files.
Next create a virtual environment with: python -m venv .venv
After the environment is created, activate it in the terminal by using "./.venv/Scripts/activate"
With the environment active run: pip install -r "client-requirements.txt"
Now that you have everything installed, place your files inside the Input folder and run the addFilesToDB.py script.
Make sure that all files you have placed in the input folder are of one type (pdf/docx/html), since the addFilesToDB.py file expects all files from one batch to be of the same type.
After the vector store has been created with the information from your files, you can chat with the RAG Bot by using the guiDemo.py file.
For the current LLM implementation you would need an open-ai key that you need to place inside the .env file, similarly to how it is shown in the .env_example file.

🤖If you want you can add another file inside the Bots folder that creates a new bot class which has the same functions as the one inside the openai_bot.py and there you can implement a connection to a different llm.
