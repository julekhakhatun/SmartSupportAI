# SmartSupportAI

    The project name is SmartSupport AI. In the UI, user have inquiry box, where user can ask question. there are two buttons in the UI. Those are 'Ask Ai' and 'Ask RAG'. 

    For the 'Ask Ai' button, user can ask random question and AI will answer those questions based on Google Gemini AI (genai) to generate content and SQLAlchemy to cache for performance improvement.

    For the 'Ask RAG' button, user can ask question from the web document link https://lilianweng.github.io/posts/2023-06-23-agent/ is provided. RAG will answer those questions from the web documents.



Prerequisites:
    Python 3.10 or higher installed
    Basic command line
    A code editor like VS Code
    Inter access

    To Install Flask, use this command:
    '''pip install flask'''

    To create and activate virtual Environment:
    in Mac/Linux:
        '''python3 -m venv venv
        source venv/bin/avtivate'''
    in Windows:
        '''python -m venv venv
        venv\Scripts\activate'''

How to run:
    1. git clone https://github.com/julekhakhatun/SmartSupportAI.git
    2. install the required packages
    '''pip install -r requirements.txt'''
    3. run '''python app.py'''
    4. open the browser and use the link: http://127.0.0.1:8000/


