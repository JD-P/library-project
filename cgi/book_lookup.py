#!/usr/bin/python3

import os

import sys

import codecs

import sqlite3

import cgi

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
    query_cursor.execute("select title, author, pubtext, publisher, edition, awards, "
                         "summary, subjects, dewey, locc, isbn10, isbn13, notes, availability "
                         "from books where key=?", (book_id,))
    book_data = list(query_cursor.fetchall()[0])
    # Swap all empty columns for a not available marker.
    for column in enumerate(book_data):
        if column[1] == '':
            book_data[column[0]] = 'N.A'
        else:
            pass
    # Construct HTML.
    book_data_html = ["<p>" + str(column) + "</p>\n" for column in book_data]
    html_start_block = ("<html>\n"
                        "  <head>\n"
                        '    <link href="/css/lookup.css" rel="stylesheet">\n'
                          '    <title> Details for "' + book_data[0] + '" </title>\n'
                          '    <meta charset="utf-8">\n'
                        '  </head>\n'
                        '  <body>\n'
                        '    <article>\n')
    book_data_html[0] = '<h1> ' + book_data_html[0] + ' </h1>'
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
