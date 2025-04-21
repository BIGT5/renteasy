import secrets
from sqlalchemy import and_
from functools import wraps
from flask import (render_template,request,redirect,url_for,flash,make_response,session,get_flashed_messages)
from flask_mail import Message
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,myforms,mail
from pkg.myforms import Register,Login
from pkg.models import db,Tenant, Landlord,States,Vacant,Pictures,Types,Bookmark


def login_required(f):
    @wraps(f)
    def login_decorator(*args, **kwargs):
        guestid = session.get("useronline")
        if guestid:
            return f(*args, **kwargs)
        else:
            flash("you must be logged in to view that page", category="failed")
            return redirect(url_for("login"))

    return login_decorator


@app.template_filter("currency")
def formatter(value):
    values = float(value)
    return "{:,}".format(values)


@app.after_request
def after_request(response):
    response.headers["cache-control"] = "no-cache,no-store,must-revalidate"
    return response


@app.errorhandler(404)
def page_not_found(error):
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/404.html", landlord=landlord, tenant=tenant, error=error),404
    


@app.errorhandler(400)
def bad_request(error):
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/400.html", landlord=landlord, tenant=tenant, error=error), 400


@app.errorhandler(403)
def forbidden(error):
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/403.html",landlord=landlord, tenant=tenant, error=error), 403


@app.errorhandler(405)
def not_allowed(error):
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/405.html", landlord=landlord, tenant=tenant, error=error), 405


@app.errorhandler(408)
def request_timeout(error):
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/408.html",landlord=landlord, tenant=tenant, error=error), 408


@app.errorhandler(413)
def too_large(error):
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/413.html", landlord=landlord, tenant=tenant, error=error), 413


@app.route("/")
def index():
    guest_id= session.get('useronline')
    landlord = (db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first())
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    prop = db.session.query(Vacant).filter(Vacant.is_featured==True).limit(4).all()
    new = db.session.query(Vacant).order_by(Vacant.date_listed.desc()).limit(4).all()
    all_states = db.session.query(States).all()
    all_types = db.session.query(Types).all()
    return render_template("user/index.html",prop=prop,new=new,landlord=landlord,tenant=tenant,all_types=all_types,all_states=all_states)


@app.route("/about/")
def about():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/about.html",landlord=landlord,tenant=tenant)


@app.route("/register/", methods=["GET", "POST"])
def register():
    register = Register()
    if register.validate_on_submit():
        try:
            fname = register.fname.data
            lname = register.lname.data
            email = register.email.data
            pwd = register.password.data
            user = register.user.data
            hashed_pwd = generate_password_hash(pwd)

            landlord_exist = db.session.query(Landlord).filter(Landlord.landlord_email==email).first()
            tenant_exist = db.session.query(Tenant).filter(Tenant.tenant_email==email).first()

            if landlord_exist or tenant_exist:
                flash("Email already registered", category="failed")
                return redirect(url_for('register'))

            if user == "landlord":
                landlord = Landlord(
                    landlord_fname=fname,
                    landlord_lname=lname,
                    landlord_email=email,
                    landlord_password=hashed_pwd,
                )
                db.session.add(landlord)
                db.session.commit()
                flash("Registration successful", category="success")
                return redirect(url_for("login"))
            else:
                tenant = Tenant(
                    tenant_fname=fname,
                    tenant_lname=lname,
                    tenant_email=email,
                    tenant_password=hashed_pwd,
                )
                db.session.add(tenant)
                db.session.commit()
                flash("Registration successful", category="success")
                return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occured during registration", category="failed")
    return render_template("user/register.html", register=register)


@app.route("/login/",methods=['GET','POST'])
def login():
    login = Login()
    if login.validate_on_submit():
        email = login.email.data
        pwd = login.password.data

        try:
            landlord = db.session.query(Landlord).filter(Landlord.landlord_email == email).first()
            if landlord and check_password_hash(landlord.landlord_password, pwd):
                if landlord.status == "active":
                    session["useronline"] = landlord.landlord_id
                    session["username"] = landlord.landlord_fname
                    session["usertype"] = "landlord"
                    flash("Login successful", category="success")
                    return redirect(url_for("dashboard"))
                else:
                    flash(" You account has been banned!!!", category="failed")
                    return redirect(url_for('login'))

            tenant = db.session.query(Tenant).filter(Tenant.tenant_email == email).first()
            if tenant and check_password_hash(tenant.tenant_password, pwd):
                if tenant.status == "active":
                    session["useronline"] = tenant.tenant_id 
                    session['username'] = tenant.tenant_fname
                    session['usertype'] = 'tenant'
                    flash("Login successful", category="success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("You account has been banned!!!", category="failed")
                    return redirect(url_for('login'))

            flash("Wrong password or email", category="failed")
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash("An error occured during login", category="failed")
            return redirect(url_for("login"))

    return render_template("user/login.html",login=login)


@app.route("/dashboard/")
@login_required
def dashboard():
    guest_id = session.get('useronline')

    if not guest_id:
        return redirect(url_for('login'))
    
    if guest_id:
        landlord = db.session.query(Landlord).filter(Landlord.landlord_id==guest_id).first()
        tenant = db.session.query(Tenant).filter(Tenant.tenant_id==guest_id).first()
        return render_template('user/dashboard.html',landlord=landlord,tenant=tenant)
    else:
        flash('You cannot view this page unlesss you are logged in',category='failed')
        return redirect(url_for('login'))


@app.route("/terms/")
def terms():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/terms.html",landlord=landlord,tenant=tenant)


@app.route("/details/<int:id>/")
@login_required
def details(id):
    guest_id = session.get("useronline")
    landlord = (db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first())
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    prop = db.session.query(Vacant).filter(Vacant.house_id==id).first()
    pics = db.session.query(Pictures).filter(Pictures.property_id == id).all()
    return render_template("user/details.html",prop=prop,pics=pics,landlord=landlord,tenant=tenant)


@app.route("/advertise/")
def advertise():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/advertise.html",landlord=landlord,tenant=tenant)


@app.route("/interface/")
@login_required
def interface():
    guest_id = session.get("useronline")
    landlord = (db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first())
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    pagination = db.paginate(db.select(Vacant), page=page, per_page=per_page, error_out=False)
    all_houses = pagination.items if pagination.items else []
    total_pages = pagination.pages if pagination.pages else 0
    return render_template("user/interface.html",all_houses=all_houses,landlord=landlord,tenant=tenant,total_pages=total_pages,page=page)


@app.route("/listings/process/", methods=["POST","GET"])
@login_required
def listings_process():
    id = request.form.get("id")
    if not id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return (
                "<tr><td colspan='10' class='text-center'>Landlord ID is required</td></tr>",
                400,
            )
        return render_template(
            "user/listings.html",
            listings=[],
            landlord=None,
            error="Landlord ID is required",
        )

    landlord = db.session.query(Landlord).filter(Landlord.landlord_id == id).first()
    listings = db.session.query(Vacant).filter(Vacant.landlord_id == id).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        rows = ""
        if listings:
            for i, listing in enumerate(listings, start=1):
                rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><img src="/static/properties/{listing.cover_image}" alt="Cover" style="width: 50px;"></td>
                    <td>${listing.house_price}</td>
                    <td>{listing.location}</td>
                    <td>{listing.address}</td>
                    <td>{listing.house_status}</td>
                    <td>{listing.date_listed}</td>
                    <td><a href="/details/{listing.house_id}/" class="btn btn-primary btn-sm">Details</a></td>
                    <td><a href="/edit/listings/{listing.house_id}" class="btn btn-warning btn-sm">Edit</a></td>
                    <td><a href="/delete/{listing.house_id}" class="btn btn-danger btn-sm">Delete</a></td>
                </tr>
                """
        else:
            rows = "<tr><td colspan='10' class='text-center'>No listings available for this landlord</td></tr>"
        return rows

    return render_template("user/listings.html", list=listings,landlord=landlord)


@app.route("/1bed/")
def bed_1():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/1bed.html",landlord=landlord,tenant=tenant)


@app.route("/2bed/")
def bed_2():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/2bed.html",landlord=landlord,tenant=tenant)


@app.route("/3bed/")
def bed_3():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/3bed.html",landlord=landlord,tenant=tenant)


@app.route("/privacy/")
def privacy():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    return render_template("user/privacy.html",landlord=landlord,tenant=tenant)

@app.route("/user/edit/",methods=['GET','POST'])
@login_required
def edit_profile():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()

    if session.get('useronline') == None:
        return redirect(url_for("login"))

    user_type = session.get('usertype')
    user_id = session.get('useronline')

    all_states = db.session.query(States).all()

    if user_type == 'landlord':
        deets = (db.session.query(Landlord).filter(Landlord.landlord_id == user_id).first())
        if deets is None:
            session.clear()
            return redirect(url_for("login"))
        if deets and request.method == 'POST':
            try:
                file = request.files.get("photo")
                filename = file.filename
                extension = filename.split(".")
                ext = extension[-1]
                generated_filename = secrets.token_urlsafe() + "." + ext
                file.save("pkg/static/uploads/" + generated_filename)

                deets.landlord_email = request.form.get('email')
                deets.landlord_phone = request.form.get('phone')
                deets.address = request.form.get('address')
                deets.state_id = request.form.get('state_id')
                deets.profile_pictures = generated_filename
                db.session.commit()
                flash("Profile updated successfully", category="success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Error updating profile',category='failed')
        return render_template("user/edit.html", deets=deets, all_states=all_states, deets2=None,landlord=landlord,tenant=tenant)

    elif user_type == 'tenant':
        deets2 = db.session.query(Tenant).filter(Tenant.tenant_id == user_id).first()
        if deets2 is None:
            session.clear()
            return redirect(url_for("login"))
        if deets2 and request.method == 'POST':
            try:
                file = request.files.get("photo")
                filename = file.filename
                extension = filename.split(".")
                ext = extension[-1]
                generated_filename = secrets.token_urlsafe() + "." + ext
                file.save("pkg/static/uploads/" + generated_filename)

                deets2.tenant_email = request.form.get('email')
                deets2.tenant_phone = request.form.get('phone')
                deets2.profile_pictures = generated_filename
                db.session.commit()
                flash("Profile updated successfully", category="success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Error updating profile',category='failed')
        return render_template("user/edit.html", deets=None,deets2=deets2,landlord=landlord,tenant=tenant)
    else:
        session.clear()
        return redirect(url_for('login'))


@app.route("/upload/prop/",methods=['GET','post'])
@login_required
def upload():
    guest_id = session.get("useronline")
    landlord = (
        db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
    )
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()
    all_states = db.session.query(States).all()
    all_types = db.session.query(Types).all()
    if request.method == 'POST':
        try:
            new_prop = Vacant(
                cover_image="",  
                house_price=request.form.get('price'),
                description=request.form.get("desc"),
                address=request.form.get('address'),
                location=request.form.get('location'),
                landlord_id=session.get('useronline'), 
                house_type_id=request.form.get('type')
            )
            db.session.add(new_prop)
            db.session.commit() 

            files = request.files.getlist("prop")
            uploaded_filenames = []

            for file in files:
                if file and file.filename != '':
                    extension = file.filename.split(".", 1)
                    ext = extension[-1]
                    generated_filename = secrets.token_urlsafe() + "." + ext
                    file.save("pkg/static/properties/" + generated_filename)
                    uploaded_filenames.append(generated_filename)

                    new_pic = Pictures(
                        pictures=generated_filename,
                        property_id=new_prop.house_id 
                    )
                    db.session.add(new_pic)
                    

            if uploaded_filenames:
                new_prop.cover_image = uploaded_filenames[0]

            db.session.commit()

            flash("Upload successful", category='success')
        except Exception as e:
            flash('Error uploading image', category='failed')

    return render_template('user/upload_prop.html',all_states=all_states,all_types=all_types,landlord=landlord,tenant=tenant)


@app.route('/edit/listings/<int:id>')
@login_required
def edit_listing(id):
    if session.get("usertype") == "landlord":
        prop = db.session.query(Vacant).filter(Vacant.house_id == id).first()
        pics = db.session.query(Pictures).filter(Pictures.property_id == id).all()
        guest_id = session.get("useronline")
        landlord = (
            db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first()
        )
        tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()

        return render_template('user/edit_listing.html',prop=prop,pics=pics,landlord=landlord,tenant=tenant)

@app.route('/update/new/<int:id>',methods=['GET','POST'])
@login_required
def update_new(id):
    if session.get("usertype") == "landlord":
        if request.method == "POST":
            try:
                deets = db.session.query(Vacant).filter(Vacant.house_id == id).first()
                if deets is None:
                    session.clear()
                    return redirect(url_for("login"))
                deets.house_price =request.form.get("price")
                deets.description =request.form.get("desc")
                deets.address =request.form.get("address")
                db.session.commit()

                files = request.files.getlist("prop")
                uploaded_filenames = []

                for file in files:
                    if file and file.filename != "":
                        extension = file.filename.split(".", 1)
                        ext = extension[-1]
                        generated_filename = secrets.token_urlsafe() + "." + ext
                        file.save("pkg/static/properties/" + generated_filename)
                        uploaded_filenames.append(generated_filename)

                        new_pic = Pictures(
                                pictures=generated_filename, property_id=id
                            )
                        db.session.add(new_pic)
                db.session.commit()
            except Exception as e:
                flash("Error uploading image", category="failed")

            return redirect(url_for("dashboard"))


@app.route("/favorites/<int:id>")
@login_required
def favorites(id):
    guest_id = session.get("useronline")
    landlord = (db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first())
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    pagination = db.paginate(db.select(Bookmark).filter(Bookmark.user_id==id), page=page, per_page=per_page, error_out=False)
    bookmark = pagination.items if pagination.items else []
    total_pages = pagination.pages if pagination.pages else 0

    return render_template("user/favorites.html",landlord=landlord,tenant=tenant,bookmark=bookmark,total_pages=total_pages,page=page)

@app.route("/filter/",methods=["GET","POST"])
@login_required
def filter():
    if request.method == 'GET':    
        state = request.args.get('location')
        type = request.args.get('type')
        min = request.args.get('min')
        max = request.args.get('max')

        if state and min and max and type:
            guest_id = session.get("useronline")
            landlord = (db.session.query(Landlord).filter(Landlord.landlord_id == guest_id).first())
            tenant = db.session.query(Tenant).filter(Tenant.tenant_id == guest_id).first() 
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 8, type=int)
            pagination = db.paginate(db.select(Vacant).filter(Vacant.location == state,
                        Vacant.house_type_id == int(type),
                        Vacant.house_price >= float(min),
                        Vacant.house_price <= float(max)), page=page, per_page=per_page, error_out=False)
            prop = pagination.items if pagination.items else []
            total_pages = pagination.pages if pagination.pages else 0

            if prop:
                return render_template("user/filter.html",all_houses=prop,landlord=landlord,tenant=tenant,total_pages=total_pages,page=page)   
            else:
                flash("No properties Found", category='failed')
                return redirect(url_for('index')) 
        else:
            flash("Please select all fields", category="failed")
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))


@app.route("/bookmark/<int:id>", methods=["GET","POST"])
@login_required
def bookmark(id):
    existing = Bookmark.query.filter_by(user_id=session.get('useronline'), property_id=id).first()
    if not existing:
        new_bookmark = Bookmark(user_id=session.get('useronline'), property_id=id)
        db.session.add(new_bookmark)
        db.session.commit()
        return "Bookmarked successfully"
    else:
        return 'You already bookmarked this property'


@app.route("/unbookmark/<int:id>", methods=["GET","POST"])
@login_required
def unbookmark(id):
    bookmark = Bookmark.query.filter_by(user_id=session.get('useronline'), property_id=id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
    return 'Unbookmarked successfully'


@app.route('/delete/<int:id>/')
@login_required
def delete(id):
    if session.get('usertype')=='landlord':
        delete = db.session.query(Vacant).filter(Vacant.house_id==id).first()
        pictures = db.session.query(Pictures).filter(Pictures.property_id==id).all()
        for pic in pictures:
            db.session.delete(pic)
        db.session.delete(delete)
        db.session.commit()

        flash('Property deleted successfully', category='sucesss')
        return redirect(url_for('listings_process'))
    else:
        flash('something went wrong', category='failed')
        return redirect(url_for('index'))


@app.route('/change/password/',methods=['GET','POST'])
@login_required
def change_password():
    id = session.get("useronline")
    landlord = db.session.query(Landlord).filter(Landlord.landlord_id == id).first()
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == id).first()

    if request.method == "POST":
        if session.get("usertype") == "landlord":
            pwd = landlord.landlord_password
            old = request.form.get("password")
            new = request.form.get("new_password")
            if check_password_hash(pwd, old):
                landlord.landlord_password = generate_password_hash(new)
                db.session.commit()
                flash("Password changed successfully", category="success")
                return redirect(url_for("dashboard"))
            else:
                flash("Old password is Incorrect", category="failed")
        elif session.get("usertype") == "tenant":
            pwd = tenant.tenant_password
            old = request.form.get("password")
            new = request.form.get("new_password")
            if check_password_hash(pwd, old):
                tenant.tenant_password = generate_password_hash(new)
                db.session.commit()
                flash("Password changed successfully", category="success")
                return redirect(url_for("dashboard"))
            else:
                flash("Old password is Incorrect", category="failed")

        else:
            flash('Something went wrong', category='failed')
            return redirect(url_for('dashboard'))

    return render_template("user/change_password.html",landlord=landlord,tenant=tenant)


@app.route("/send/email/",methods=["GET","POST"])
def send_email():
    if request.method == "POST":
        email = request.form.get("email")
        text = request.form.get("textarea")
        if not email:
            return "Email is required"

        msg = Message(
            subject="Complaint",
            sender=(email),
            recipients=["ezechukwutochukwu@moatcohorts.com.ng"],
        )
        msg.body = text
        mail.send(msg)
        flash("Email sent successfully", category="success")
        return redirect(url_for("advertise"))
    
@app.route("/subscribe/",methods=["GET","POST"])
def subscribe():
    if request.method == "POST":
        email = request.form.get("email")
        text = request.form.get("name")
        if not email:
            return "Email is required"

        msg = Message(
            subject="Newsletter",
            sender=(email),
            recipients=["ezechukwutochukwu@moatcohorts.com.ng"],
        )
        msg.body = "subscribe me to your newsletter Name: "+text
        mail.send(msg)
        flash("Subscribed!", category="success")
        return redirect(url_for("dashboard"))


@app.route("/logout/")
def logout():
    if session.get("useronline") != None:
        session.pop("useronline", None)
        session.pop("usertype",None)
    return redirect(url_for("index"))
