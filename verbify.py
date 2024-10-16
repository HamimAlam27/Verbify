from bs4 import BeautifulSoup
import requests
from tabulate import tabulate
import csv
import sys
from os import system
from colorama import init
from termcolor import colored
import argparse

init()

def main():
    system("clear")

    parser = argparse.ArgumentParser(description = "Verb Table")
    parser.add_argument("-m",default="s", help = "how much you want to see? 's' for simple and 'a' for all")
    parser.add_argument("-l",default="p", help = "'p' for pt-en, 'e' for en-pt")

    args = parser.parse_args()

    while True:

        try:
            choice = input("\nverb: ")
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit()

        print()
        try:
            if args.l == "p":
                choice = verb_correct(choice)
            else:
                choice = verb_portuguese(choice)

        except AttributeError:
            print(colored("Sorry maybe it's not a verb:)", "red"))
            continue
        print("Infinitive Form: ", choice, "\n")
        url_status = url_open_status(choice)

        soup_verb, soup_translate = url_open(choice)

        try:

            present_simple = verb_extract(container(soup_verb, "Indicativo Presente"))

        except AttributeError:
            print(colored("The word is not a verb or maybe you made a typo:)\n", "red"))
            continue

        present_conjunctive = verb_extract(container(soup_verb, "Conjuntivo / Subjuntivo Presente"))

        past_perfect = verb_extract(container(soup_verb, "Indicativo Pretérito Perfeito"))

        past_imperfect = verb_extract(container(soup_verb, "Indicativo Pretérito Imperfeito"))

        past_perfect_compound = verb_extract(container(soup_verb, "Indicativo Pretérito Perfeito Composto"))

        past_imperfect_conjunctive = verb_extract(container(soup_verb, "Conjuntivo / Subjuntivo Pretérito Imperfeito"))

        future_simple = verb_extract(container(soup_verb, "Indicativo Futuro do Presente Simples"))

        future_perfect_simple = verb_extract(container(soup_verb, "Condicional Futuro do Pretérito Simples"))

        translate = translate_verb(soup_translate)


        print("Meaning: ", end = "")
        for i, word in enumerate(remove_double(translate)):
            if i < len(remove_double(translate)) - 1:
                print(word, end = ", ")
            else:
                print(word)
        print()

        print("Example: ",example(soup_translate), "\n")
        print("Meaning: ", translate_example(soup_translate), "\n")


        if args.m == "s":
            total_verbs = {
                        "subject":["eu","ele/você","tu","nos","vos","eles"],
                        "present":present_simple,
                        "past":past_perfect,
                        "future":future_simple
                        }

            # print(url_status)
            print(tabulate(total_verbs, headers = "keys", tablefmt = "rounded_grid"))

        elif args.m == "a":
            total_verbs_1 = {
            "subject":["eu","tu","ele/você","nos","vos","eles"],
            "present-simple":present_simple,
            "past-simple":past_perfect,
            "future-simple":future_simple,
            }

            total_verbs_2 = {
            "subject":["eu","tu","ele/você","nos","vos","eles"],
            "present-conjunctive": present_conjunctive,
            "past-perfect-compound":past_perfect_compound,
            "past-imperfect":past_imperfect,
            "past-imperfect-conjunctive":past_imperfect_conjunctive,
            "future-perfect-simple":future_perfect_simple

            }

            # print(url_status)
            print(tabulate(total_verbs_1, headers = "keys", tablefmt = "rounded_grid"))
            print()
            print(tabulate(total_verbs_2, headers = "keys", tablefmt = "rounded_grid"))


def verb_portuguese(word):

    url = f"https://dictionary.cambridge.org/dictionary/english-portuguese/{word}"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    html_text = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html_text, "lxml")

    container = soup.find("span", class_ = "trans dtrans")
    return container.text
def verb_correct(word):

    url = f"https://conjugator.reverso.net/conjugation-portuguese-verb-{word}.html"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    html_text = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html_text, "lxml")

    container = soup.find("a", attrs = {"tooltip":"Existing infinitive"})

    return container.text

def url_open_status(word):

    url_verb = f'https://conjugator.reverso.net/conjugation-portuguese-verb-{word}.html'

    url_translate = f'https://dictionary.cambridge.org/dictionary/portuguese-english/{word}'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    verb_text = requests.get(url_verb, headers=headers)

    translate_text = requests.get(url_translate, headers=headers)

    return [verb_text.status_code, translate_text.status_code]

def url_open(word):

    url_verb = f'https://conjugator.reverso.net/conjugation-portuguese-verb-{word}.html'

    url_translate = f'https://dictionary.cambridge.org/dictionary/portuguese-english/{word}'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    verb_text = requests.get(url_verb, headers=headers).text

    translate_text = requests.get(url_translate, headers=headers).text

    return BeautifulSoup(verb_text, "lxml"), BeautifulSoup(translate_text, "lxml")

def container(source, t):

    div_container = source.find("div",attrs={"mobile-title": t})
    return div_container.find_all("i")

def verb_extract(container):

    verbs = []
    for i in container:
        first = i.find(class_="verbtxt")
        second = i.find(class_="verbtxt-term-irr")

        if second == None:
            second = i.find(class_="verbtxt-term")

        if first == None and second == None:
            continue
        elif first != None and second != None:
            verbs.append(first.text + second.text)
        else:
            verbs.append(second.text)

    return verbs

def translate_verb(source):

    verbs_list = []
    verbs = source.find_all("span", class_="trans dtrans lmr--5")
    for verb in verbs:
        verbs_list.append(verb.text)
    return verbs_list

def example(source):

    sentence = source.find("span", class_="eg deg")
    return sentence.text

def translate_example(source):

    sentence = source.find("span", class_="trans dtrans hdb")
    return sentence.text


def remove_double(items):
    new_list = []
    for item in items:
        if not (item in new_list):
            new_list.append(item)

    return new_list

def extract_error(choice):

    url_status = url_open_status(choice)

    soup_verb, soup_translate = url_open(choice)

    present_list = verb_extract(container(soup_verb, "Indicativo Presente"))

#----------for table--------


if __name__ == "__main__":
    main()

