from django.shortcuts import render,HttpResponse
import mysql.connector
from datetime import *

mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "Sivasaran@2003",
        database = "db"
    )
c = mydb.cursor()


# Create your views here.
def login(request):
    if(request.method == 'POST'):
        user = request.POST.get('user',False)
        pwd = request.POST.get('pwd',False)
        if(user == 'admin' and pwd == 'admin'):
            return render(request,'select.html')
        else:
            return HttpResponse('<h2>invalid user name or password</h2>')
    return render(request,'login.html')

def show_books(request):
    if(request.method == 'POST'):
        isbn = request.POST.get('isbn',False)
        stock = request.POST.get('stock',False)
        c.execute('update available set available = available + '+str(stock)+' where bookID = '+str(isbn))
        print('update available set available = available + '+str(stock)+' where bookID = '+str(isbn))
    c.execute("select * from book")
    p = c.fetchall()
    p = list(p)
    c.execute("select available from available")
    avail = list(c.fetchall())
    for i in range(0,len(p)):
        p[i] = list(p[i])
        p[i].append(avail[i][0])
    d = {'data' : p}
    return render(request,'show_books.html',d)

def add_book(request):
    d = {}
    if(request.method == 'POST'):
        isbn = request.POST.get('isbn',False)
        title = request.POST.get('title',False)
        year = request.POST.get('year',False)
        price = request.POST.get('price',False)
        pub = request.POST.get('publisher',False)
        pubid = request.POST.get('pubid',False)
        author = request.POST.get('author',False)
        category = request.POST.get('category',False)
        available = request.POST.get('available',False)
        
        c.execute("select * from book")
        books = list(c.fetchall())

        # checking if book exists
        for i in books :
            print(i)
            if int(isbn) in i :
                print('erf')
                return HttpResponse('<h2>book already exists</h2>')

        pubs = list(c.fetchall())
        # checking if publisher exists
        f = 1
        for i in pubs :
            if int(pubid) in i :
                f = 0
        # else inserting into pub table
        query = ""
        if(f == 1):
            query = "insert into publisher values('"+pubid+"','"+pub+"')"
            c.execute(query)

        # inserting into book
        query = "insert into book values('"+isbn+"','"+title+"','"+year+"','"+year+"','"+pubid+"','"+author + "','"+category+"')"
        c.execute(query)
        # inserting into available
        query = "insert into available values ('"+isbn+"','"+available+"')"
        print('book inserted')
        c.execute(query)
    return render(request,'add_book.html')

def delete_book(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        c.execute("select * from book")
        books = list(c.fetchall())
        for i in books :
            if int(isbn) in list(i) :
                c.execute("delete from book where isbn = "+isbn)
                print('book deleted')
                return render(request,'delete_book.html')
        return HttpResponse('<h2>invalid isbn number</h2>')
    return render(request,'delete_book.html')

def borrow(request):
  
    if request.method == 'POST':
        userid = request.POST.get('userid',False)
        isbn = request.POST.get('isbn',False)
        duedate = date.today() + timedelta(days = 15)

        c.execute("select available from available where bookID = '"+isbn+"'")
        avail = int(c.fetchall()[0][0])
        print(avail)
        if(avail > 0):
           c.execute("insert into borrowed values('"+userid+"','"+isbn+"','"+str(duedate)+"')")
           c.execute("update available set available = available - 1 where bookID = '"+isbn+"'")

    return render(request,'borrow.html')

def return_book(request):
    d = {}
    if(request.method == 'POST'):
        userid = request.POST.get('userid',False)
        isbn = request.POST.get('bookid',False)
        duedate = 0
        try:
            q = "select due_date from db.borrowed where userID = "+str(userid)+" and bookID = "+str(isbn)
            c.execute(q)
            duedate = c.fetchone()[0]
            print(duedate)
        except :
            return HttpResponse('<h1>invalid userid or isbn number</h1>')
        # due = datetime.strptime(duedate, '%Y-%m-%d').date()
        current = date.today()
        fine = (current - duedate).days
        print(fine)
        if fine > 0 :
           fine = 2*fine
        else :
           fine = 0
        print(fine)
        c.execute("delete from borrowed where userid = "+userid+" and bookID = "+isbn)
        c.execute("update available set available = available + 1 where bookID = "+isbn)
        c.execute("update db.user set num_book = num_book - 1 where userID = "+userid)
        d['user'] = userid
        d['fine'] = fine
    return render(request,'return_book.html',d)
        

def users(request):
    d = {}
    c.execute("select * from user")
    users = list(c.fetchall())
    d['data'] = users
    c.execute("select * from borrowed")
    borrowed = list(c.fetchall())
    d['borrowed'] = borrowed
    return render(request,'users.html',d)


def add_user(request):
    c.execute('select count(*) from user')
    new_id = int(c.fetchall()[0][0]) + 101
    d = {}
    d['id_'] = new_id
    if(request.method == 'POST'):
        username = request.POST.get('name',False)
        phno = request.POST.get('phno',False)
        c.execute(f"insert into db.user values('"+str(new_id)+"','"+username+"','"+str(phno)+"',0)")
        
    return render(request,'add_user.html',d)