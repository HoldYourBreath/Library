import os
import pip
import time
print(pip.pep425tags.get_supported())
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
import tkinter
from tkinter import *
from tkinter import ttk

########################
#Read data from library_data.csv and loan_data.csv
########################

print('Reading data from files...')
script_dir = os.path.dirname(os.path.realpath('__file__'))
print(script_dir)
target_file = os.path.join(script_dir, '')
print(target_file)
os.chdir(target_file)
retval = os.getcwd()
print(retval)
target_file = os.path.join(retval, 'data\library_data.csv')
target_file2 = os.path.join(retval, 'data\loan_data.csv')
print(target_file2)
os.chdir(retval)
if os.path.isfile(target_file) and os.access(target_file, os.R_OK):
    print('File library_data.csv exists and is readable')
    print('File loan_data.csv exists and is readable')
else:
    print('Either file library_data.csv is missing or is not readable')
    print('Either file loan_data.csv is missing or is not readable')
    sys.exit()
library_data_file = pd.read_csv(target_file)
loan_data_file = pd.read_csv(target_file2)

#library_data.csv
isbn = library_data_file.ISBN
book_name = library_data_file.BookName
author = library_data_file.Author
topic = library_data_file.Topic
description = library_data_file.Description
number_of_books = library_data_file.NumberOfBooks
books_in_library = library_data_file.BooksInLibrary
book_rating = library_data_file.BooksRating

#loan_data.csv
borrower = loan_data_file.Borrower
date_when_borrowed = loan_data_file.DateWhenBorrowed
date_returned = loan_data_file.DateReturned

import tkinter as tk
class Passwordchecker(tk.Frame):
   def __init__(self, parent):
       tk.Frame.__init__(self, parent)
       self.parent = parent
       self.initialize_user_interface()
       self.LoadBookTable()
       self.grid(sticky=(N, S, W, E))
       self.parent.grid_rowconfigure(0, weight=1)
       self.parent.grid_columnconfigure(0, weight=1)

   def initialize_user_interface(self):
       #self.parent.geometry("1000x1000")
       #self.parent.grid_rowconfigure(0, weight=1)
       #self.parent.grid_columnconfigure(0, weight=1)
       self.parent.title("Library application")
       self.parent.config(background="lavender")


       self.entry1=tk.Entry(self.parent)

       #Search book
       self.button1=tk.Button(self.parent,text="Search", command=self.Search)
       self.button1.grid(row=1, column=2)
       self.button1.grid()

       self.label1=tk.Label(self.parent,text="Search for a keyword")
       self.label1.grid(row=1, column=0, sticky=tkinter.W)
       self.entry1.grid(row=1, column=1)
       #self.entry1.grid_columnconfigure(0, weight=3)
       #self.entry1.grid_rowconfigure(1, weight=3)
       self.label1.grid()
       self.entry1.grid()

       #Loan book
       self.entry2=tk.Entry(self.parent)
       self.entry2.grid()
       self.button2=tk.Button(self.parent,text="Loan", command=self.Loan)
       self.button2.grid(row=2, column=2)
       self.button2.grid()
       self.button3=tk.Button(self.parent,text="Return", command=self.Return)
       self.button3.grid(row=2, column=4)
       self.button3.grid()
       self.label2=tk.Label(self.parent,text="Loan or return a book, enter signum")
       self.label2.grid(row=2, column=0, sticky=tkinter.W)
       self.entry2.grid(row=2, column=1)
       self.label2.grid()

       # Set the treeview
       self.tree = ttk.Treeview(self.parent, columns=('Book Name','Author', 'Topic', 'Description', 'Number of books', 'Books available', 'Rating', 'ISBN'))
       self.tree.heading('#0', text='Book Name')
       self.tree.heading('#1', text='Author')
       self.tree.heading('#2', text='Topic')
       self.tree.heading('#3', text='Description')
       self.tree.heading('#4', text='Number of books')
       self.tree.heading('#5', text='Books available')
       self.tree.heading('#6', text='Rating')
       self.tree.heading('#07', text='ISBN')
       self.tree.column('#0', stretch=tkinter.YES, anchor='center')
       self.tree.column('#1', stretch=tkinter.YES, anchor='center')
       self.tree.column('#2', stretch=tkinter.YES, anchor='center')
       self.tree.column('#3', stretch=tkinter.YES, anchor='center')
       self.tree.column('#4', stretch=tkinter.YES, anchor='center', width=100)
       self.tree.column('#5', stretch=tkinter.YES, anchor='center', width=100)
       self.tree.column('#6', stretch=tkinter.YES, anchor='center', width=100)
       self.tree.column('#7', stretch=tkinter.YES, anchor='center')
       self.tree.grid(row=6, columnspan=5, sticky='nsew')
       self.tree.grid_columnconfigure(5, weight=1)
       self.treeview = self.tree
       # Initialize the counter
       self.i = 0


   def LoadBookTable(self):
        for x in range(0, 3):
            self.tree.insert('', 'end',
                                 text=book_name[x], values=(author[x], topic[x], description[x], number_of_books[x], books_in_library[x], book_rating[x], isbn[x]))

   def Search(self):
       donothing = 'Do nothing button'
       print(donothing)

   def Loan(self):
       print(time.ctime())
       #if
       #If there is entry in the database with the signum,
       # then print("Please return your loaned book first")

   def Return(self):
       print(time.ctime())

if __name__ == '__main__':

   root = tk.Tk()
   run = Passwordchecker(root)
   root.mainloop()