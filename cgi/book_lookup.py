#!/usr/bin/python3

import os

import sys

import codecs

import sqlite3

import cgi
import cgitb
cgitb.enable()

def main():
    writer = codecs.getwriter('utf-8')(sys.stdout.buffer)
    query = cgi.FieldStorage()
    book_id = query.getvalue("id")
    books_db_path = os.path.join(
        os.path.split(
            os.path.abspath(__file__))[0], 
        "books.sqlite")
    books_db = sqlite3.connect(books_db_path)
    query_cursor = books_db.cursor()
    query_cursor.execute("select title, author, pubtext, edition, awards, "
                         "summary, subjects, dewey, locc, isbn10, isbn13, notes, availability "
                         "from books where key=?", (book_id,))
    book_data = list(query_cursor.fetchall()[0])
    
    # Construct HTML.
    book_data_html = ["<p id='author'>" + "by "
                      + ' '.join(reversed(str(book_data[1]).split(","))).strip()
                      + "</p>",
                      "<p id='pubtext'>" + "Published: " +
                      str(book_data[2]) + ' ' + str(book_data[3]) + "</p>"]
    if book_data[4]:
        book_data_html.append(
            "<ul id='awards'>" +
            ''.join(["<li>" + award + "</li>" for award in book_data[4].split()])
            + "</ul>")
    if book_data[5]:
        book_data_html.append("<p id='summary'>" + str(book_data[5]) + "</p>")
    else:
        book_data_html.append("<p id='summary'>" + "No summary is available for " +
                              book_data[0].title() + ".</p>")
    book_data_html.append("<div id='subject-div'>")
    book_data_html.append("<h2>" + "Subjects" + "</h2>")
    book_data_html.append(
        "<ul id='subjects'>" +
        ''.join(["<li>" +
                 ' '.join([word.capitalize() for word in subject.split("_")])
                 + "</li>" for subject in str(book_data[6]).split(",")])
        + "</ul>")
    book_data_html.append("</div>")
    book_data_html.append("<div id='id-numbers'>")
    book_data_html.append("<h2>" + "Identifiers" + "</h2>")
    if book_data[7]:
        book_data_html.append("<p id='dewey'>" +
                              "<b class='field'>Dewey Decimal: </b>" +
                              str(book_data[7]) +
                              "</p>")
    if book_data[8]:
        book_data_html.append("<p id='locc'>" +
                              "<b class='field'>Library of Congress #: </b>" +
                              str(book_data[8]) +
                              "</p>")
    if book_data[9]:
        book_data_html.append("<p id='isbn10'>" +
                              "<b class='field'>IBSN10: </b>" +
                              str(book_data[9]) +
                              "</p>")
    if book_data[10]:
        book_data_html.append("<p id='isbn13'>" +
                              "<b class='field'>ISBN13: </b>" +
                              str(book_data[10]) +
                              "</p>")
    book_data_html.append("</div>")
    if book_data[12] == 1:
        book_data_html.append("<p id='availability'>" + "<b>Availability: </b>" + 
                              "<span class='available'>" + str(book_data[12]) + "</span>"
                              + " copy available</p>")
    else:
        book_data_html.append("<p id='availability'>" + + "<b>Availability: </b>" + 
                              "<span class='unavailable'>" + str(book_data[12]) + "</span>"
                              + " copy available</p>")

    html_start_block = ("<html>\n"
                        "  <head>\n"
                        '    <link href="/css/lookup.css" rel="stylesheet">\n'
                          '    <title> Details for "' + book_data[0] + '" </title>\n'
                          '    <meta charset="utf-8">\n'
                        '  </head>\n'
                        '  <body>\n'
                        '    <article>\n')
    book_data_html.insert(0, '<h1> ' + str(book_data[0]).title() + ' </h1>')
    html_start_block += ''.join(book_data_html)
    html_start_block += ('    </article>\n'
                         '  </body>\n'
                         '</html>\n')
    # HTTP Headers
    writer.write("Content-Type: text/html; charset=utf-8" + "\r\n")
    writer.write("Content-Length: " + str(len(html_start_block)) + "\r\n")
    # Seperator between headers and HTML
    writer.write("\r\n")
    # HTML
    writer.write(html_start_block)

main()
