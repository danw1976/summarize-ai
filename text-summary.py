from openai import OpenAI
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import re

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found")
elif api_key[:8] != "sk-proj-":
    print("An API key was found, but it doesn't start sk-proj-; please check you are using the right key")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks llike it might have space or tab characters at the start or end - please remove them")
else:
    print("API key found and looks good so far!")


openai = OpenAI()


# A class to represent a Webpage

class Website:
    """
    A utility class to represent a Website that we have scraped
    """
    url: str
    title: str
    text: str

    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)


# System prompt definition

system_prompt = "You are an an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in simple text."


# A function that writes a User Prompt that asks for summaries of websites

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website are as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt


# Structure message in OpenAI API expected format

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]


# call to OpenAI API

def summarize(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages_for(website)
    )
    return response.choices[0].message.content

def is_valid_url(str):
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    p = re.compile(regex)

    if str == None:
        return False
    elif re.search(p, str):
        return True
    else:
        return False



def display_summary(url):
    summary = summarize(url)
    print(summary)

def main():

    while True:
        web_url = input("Provide a website to analyze: ") 
        if is_valid_url(web_url) == False:
            continue
        else:
            break

    display_summary(web_url)    


if __name__ == "__main__":
    main()
