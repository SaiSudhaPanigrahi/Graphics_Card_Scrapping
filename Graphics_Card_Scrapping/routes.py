import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from Graphics_Card_Scrapping import app, db, bcrypt
from Graphics_Card_Scrapping.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from Graphics_Card_Scrapping.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/home")
def Main():
    from bs4 import BeautifulSoup as soup  # HTML data structure
    from urllib.request import urlopen as uReq  # Web client

    # URl to web scrap from.
    # in this example we web scrap graphics cards from Newegg.com
    page_url = "https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card"

    # opens the connection and downloads html page from url
    uClient = uReq(page_url)


    print(uClient)

    # parses html into a soup data structure to traverse html
    # as if it were a json data type.
    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()


    # finds each product from the store page
    containers = page_soup.findAll("div", {"class": "item-container"})

    #print(containers[1])

    # name the output file to write to local disk
    out_filename = "graphics_cards.csv"
    # header of csv file to be written
    headers = "brand,product_name,current_price,shipping \n"

    # opens file, and writes headers
    f = open(out_filename, "w")
    f.write(headers)
    l=[]

    # loops over each product and grabs attributes about
    # each product
    for container in containers:
        
    
     # Finds all link tags "a" from within the first div.
     make_rating_sp = container.select("div")[2].select("a") #added extra div, removed select
     #print(make_rating_sp) #only if u collect something together u can use square braces. 

     # Grabs the title from the image title attribute
     # Then does proper casing using .title()
     brand = make_rating_sp[0].img["title"].title()
     print("brand: " + brand + "\n")
     d={ }

     # Grabs the text within the second "(a)" tag from within
     # the list of queries.
     #print(container.select("div")[1])
    
    
    
    
     product_name = container.findAll("a", {"class": "item-title"})[0].text.strip().replace("$", "").replace(" Shipping", "")
     #print("p_n :" + p_n + "\n")
    
     #product_name = container.select("div")[1].select("a")[1].text
     print("product name: "+ product_name + "\n")
     current_price = container.find("li", {"class": "price-current"}).find("strong").text #awesome
     print("current price: " , current_price )
     print(" ")
    
     shipping = container.findAll("li", {"class": "price-ship"})[0].text.strip().replace("$", "").replace(" Shipping", "")
     print("shipping: " + shipping + "\n")
     d['product_name']=product_name
     d['current_price']=current_price
     d['shipping']=shipping
     d['brand']=brand
    
    
     print("-----------------------------------------------------------------")
    

     # writes the dataset to file
     f.write(brand + ", " + product_name.replace(",", "|") + ", "+ current_price + ", " + shipping + "\n")
     l.append(d)

    
    f.close()  # Close the file
    #---End of code---
    return render_template('home.html', lists=l)
    
@app.route("/")
def home():
    return render_template('intro.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


