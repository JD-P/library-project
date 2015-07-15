#!/usr/bin/python3

import os

import sqlite3

import cgi

def main():
    rows = run_query()
    if rows is False:
        query_failure()
        return False
    else:
        query_response(rows)
        return True

def run_query():
    """Run the queries against the sqlite backend and return the resulting rows."""
    query = cgi.FieldStorage()
    search_by = query.getvalue("searchby")
    search_type = query.getvalue("searchtype")
    # Convert search type to sql statement chunk
    if search_type == 'exact':
        search_type = '=?'
    else:
        search_type = " like ?"
    # Prepend and append bits to search statement based on search type
    if search_type == " like ?":
        search = "%" + query.getvalue("search") + "%"
    else:
        search = query.getvalue("search")
    test = open("books.sqlite", 'r+')
    books_db_path = os.path.join(
        os.path.split(
            os.path.abspath(__file__))[0], 
        "books.sqlite")
    books_db = sqlite3.connect(books_db_path)
    query_cursor = books_db.cursor()
    search_columns = ["title", "author", "summary",
                     "publisher", "dewey", "locc"]
    partial_sql = ("select key, title, author, pubtext, edition,"
                   " availability from books where ")
    # Handle special cases
    if search_by == 'subject':
        query_cursor.execute("select * from books;")
        results = query_cursor.fetchall()
        matching_rows = []
        for row in results:
            subjects = row[7].split(",")
            for subject in subjects:
                if search_type == " like ?":
                    if search in subject:
                        matching_rows.append(row)
                    else:
                        pass
                else:
                    if search == subject:
                        matching_rows.append(row)
                    else:
                        pass
        return matching_rows
    elif search_by == 'isbn':
        query_cursor.execute(partial_sql + "isbn10" + search_type + ";", (search,))
        intermediate_results = query_cursor.fetchall()
        query_cursor.execute(partial_sql + "isbn13" + search_type + ";", (search,))
        return intermediate_results + query_cursor.fetchall()
    elif search_by == 'availability':
        if search[0] == "%":
            search = search[1]
        else:
            pass
        if search == '0' or search == 'false' or search == 'False':
            query_cursor.execute(partial_sql + "availability=0;")
            return query_cursor.fetchall()
        elif search == '1' or search == 'true' or search == 'True':
            query_cursor.execute(partial_sql + "availability=1;")
        else:
            return False
    # Handle all other 'generic' cases.
    elif search_by in search_columns:
        query_cursor.execute(partial_sql + search_by + search_type + ";", (search,))
        return query_cursor.fetchall()
    else:
        return False

def query_response(rows):
    html_start_block = (
        """<html>
             <head>
               <link href="css/query.css" rel="stylesheet">
               <title> List of Books in A&T Library Found By Your Query </title>
               <meta charset="utf-8">
             </head>
             <body>
             <table>
             <tr> <td>id</td> <td>Title</td> <td>Author</td> 
                  <td>Publish Info</td> <td> Edition </td> <td> Availability </td> 
             </tr>  
        """)
    html_rows= [["<tr>"] +  
                ["<td>" + str(column_data) + "</td>" for column_data in row] + 
                ["</tr>"] for row in rows]
    for html_row in html_rows:
        item_id = html_row[1][4:-5]
        html_row[1] = ('<td>' '<a href="cgi/book_lookup.py?id=' + item_id + '">' + 
                       item_id + '</a>' + '</td>')
        html_start_block += ''.join(html_row)
    html_end_block = (
        """    </table>
             </body>
           </html>
        """
        )
    html_start_block += html_end_block
    #HTTP Headers
    print("Content-Type: text/html; charset=utf-8", end='\r\n')
    print("Content-Length: " + str(len(html_start_block)), end='\r\n')
    # Seperator between header and HTML
    print(end='\r\n')
    #HTML
    print(html_start_block)

def query_failure():
    """Give an HTTP response indicating the query failed."""
    response_html_dir = os.path.join(
        os.path.split(
            os.path.split(
                os.path.abspath(__file__))[0])[0], 
        "query_failure.html")
    response_html = open(response_html_dir).read()
    #HTTP Headers
    print("Content-Type: text/html; charset=utf-8", end='\r\n')
    print("Content-Length: " + str(len(response_html)), end='\r\n')
    # Seperator between header and HTML
    print(end='\r\n')
    #HTML
    print(response_html)

main()
