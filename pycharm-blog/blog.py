from flask import  Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu Sayfayı Görüntülemek İçin Giriş Yap","danger")  
            return redirect(url_for("login"))
    return decorated_function

class RegisterForm(Form):
    name=StringField("İsim , Soyisim:",validators=[validators.Length(min=4,max=20)])
    username=StringField("Kullanıcı Adı:",validators=[validators.Length(min=4,max=20)])
    email=StringField("Email Adresi:",validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Girin")])
    password=PasswordField("Parola:",validators=[
        validators.DataRequired(message="Lütfen Bir Parola Belirleyin"),
        validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor...")

    ]) 
    confirm=PasswordField("Parola Doğrula:")

class LoginForm(Form):
    username= StringField("Kullanıcı Adı:")
    password= PasswordField("Parola:")


app = Flask(__name__)
app.secret_key="blog"

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="blog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql= MySQL(app)

@app.route("/")

def index():
    articles=[
        {"id":1,"title":"Deneme1","content":"Deneme1 Icerik"},
        {"id":2,"title":"Deneme2","content":"Deneme2 Icerik"},
        {"id":3,"title":"Deneme3","content":"Deneme3 Icerik"}



    ]


    return render_template("index.html",articles = articles)



@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/article/<string:id>")
def article():
    cursor= mysql.connection.cursor()

    sorgu="Select * From articles where id = %s"

    result=  cursor.execute(sorgu,(id,))

    if result > 0:
        article= cursor.fetchone()
        return render_template("article.html", article = article)
    else:
        return render_template("article.html")


@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor= mysql.connection.cursor(sorgu,session["username",id])
    sorgu= "Select * From articles where author = %s amd id = %s"

    result= cursor.execute(sorgu2,(id,))
    
    return redirect(url_for("dashboard") )

    if result>0:
        sorgu2= "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard") )

    else:
        flash("Böyle bir makale yok ya da silmeye yetkiniz yok.","danger")
        return redirect(url_for("index"))




@app.route("/dashboard")
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    sorgu="Select * From articles where author= %s"

    result=cursor.execute(sorgu,(session["username"],))

    if result>0:
        articles= cursor.fetchall()
        return render_template("dashboard.html", articles = articles)
    else:
        return render_template("dashboard.html")
    


@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    
    if request.method == "POST" and form.validate():
        name=form.name.data
        username=form.username.data
        email=form.email.data
        password=sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla kayıt oldunuz...","success")


        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)
    


@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id





@app.route("/login",methods=["GET","POST"])
def login():
    form= LoginForm(request.form)
    if request.method=="POST":
        username=form.username.data
        poassword_entered=form.password.data

        cursor=mysql.connection.cursor()
        sorgu= "Select * From users where username = %s"
        result=cursor.execute(sorgu,(username,))

        if result>0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(poassword_entered,real_password):
                flash("Başarıyla Giriş Yaptınız.","success")
                session["logged_in"]= True
                session["username"]= username

                return redirect(url_for("index"))
            else:
                flash("Parolanızı Yanlış Girdiniz.","danger")
                return redirect(url_for("login"))

        else:
            flash("Böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("login"))





    return render_template("login.html",form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/articles")
def articles():
    cursor= mysql.connection.cursor()
    sorgu= "Select * From articles"

    result= cursor.execute(sorgu)
    if result>0:
        articles= cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")

@app.route("/addarticle",methods=["GET","POST"])
def addarticle():
    form=ArticleForm(request.form)
    if request.method=="POST" and form.validate():
        title=form.title.data
        content=form.content.data

        cursor=mysql.connection.cursor()

        sorgu= "Insert into articles(title,author,content) VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username"],content))
        mysql.connection.commit()
        cursor.close()

        flash("Makale Başarıyla Eklendi","success")

        return redirect(url_for("dashboard"))


    return render_template("addarticle.html ",form=form)

class ArticleForm(Form):
    title=StringField("Makale Başlığı",validators=[validators.Length(min=5,max=100)])
    content=TextAreaField("Makale İçeriği",validators=[validators.Length(min=10)])


if __name__ == "__main__":
    app.run(debug=True)

