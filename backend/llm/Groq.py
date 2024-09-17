#!/usr/bin/python3
"""This is a module to implement the groq api"""
from groq import Groq
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

class Groq_API:
    """Class with the groq functions"""
    def get_response(self, message: str, system_content: str, temp: int = 2, token: int = 550,
                 stream: bool = False, response_format=None) -> str:
   
        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user","content": message,}
            ],
            model="llama3-groq-70b-8192-tool-use-preview",
            temperature=temp,
            max_tokens=token,
            stream=stream,
            response_format=response_format

        )

        return chat_completion.choices[0].message.content
