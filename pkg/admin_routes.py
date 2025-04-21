import secrets
from functools import wraps
from flask import (render_template,request,redirect,url_for,flash,make_response,session,)
from werkzeug.security import generate_password_hash, check_password_hash
from pkg import app
from pkg.myforms import AdminRegister,AdminLogin
from pkg.models import db, Admin,Landlord,Tenant,Vacant,Bookmark


def login_required(f):
    @wraps(f) 
    def login_decorator(*args, **kwargs):
        adminid = session.get("adminonline")
        admin = db.session.query(Admin).filter(Admin.admin_id == adminid).first()
        admin_type = session.get("usertype")

        if adminid and admin and admin_type == "admin":
            return f(*args, **kwargs)
        else:
            flash("you must be logged in to view this page", category="danger")
            return redirect(url_for("admin_login"))

    return login_decorator


@app.after_request
def after_request(response):
    response.headers["cache-control"] = "no-cache,no-store,must-revalidate"
    return response

@app.route("/admin/dashboard/")
@login_required
def admin_dashboard():
    admin_id = session.get('adminonline')
    admin = db.session.query(Admin).filter(Admin.admin_id == admin_id).first()
    landlord = db.session.query(Landlord).all()
    tenant = db.session.query(Tenant).all()
    vacant = db.session.query(Vacant).all()
    new = db.session.query(Vacant).order_by(Vacant.date_listed.desc()).limit(3).all()
    blocked_landlord = db.session.query(Landlord).filter(Landlord.status == "inactive").all()   
    blocked_tenant = db.session.query(Tenant).filter(Tenant.status == "inactive").all() 
    bookmark = db.session.query(Bookmark).all()
    return render_template("admin/dash.html",admin=admin,landlord=landlord,tenant=tenant,vacant=vacant,bookmark=bookmark,blocked_landlord=blocked_landlord,blocked_tenant=blocked_tenant,new=new)

@app.route("/admin/register/",methods=['GET','POST'])
def admin_register():
    register = AdminRegister()
    if register.validate_on_submit():
        username = register.username.data
        pwd = register.password.data
        hashed_pwd = generate_password_hash(pwd)

        admin = Admin(
            admin_username=username,
            password=hashed_pwd,
        )
        db.session.add(admin)
        db.session.commit()
        flash("Registration successful", category="success")
        return redirect(url_for("admin_login"))

    return render_template("admin/register.html",register=register)


@app.route("/admin/login/", methods=["GET", "POST"])
def admin_login():
    login = AdminLogin()
    if login.validate_on_submit():
        username = login.username.data
        pwd = login.password.data
        admin = (
            db.session.query(Admin).filter(Admin.admin_username == username).first()
        )

        if admin:
            check = check_password_hash(admin.password, pwd)
            if check:
                session["adminonline"] = admin.admin_id
                session["usertype"] = "admin"
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Wrong password", category="failed")

        else:
            flash("Wrong email", category="failed")
            return redirect(url_for("admin_login"))

    return render_template("admin/login.html",login=login)


@app.route("/admin/listings/", methods=["POST", "GET"])
@login_required
def admin_listings():

    admin_id = session.get("adminonline")
    admin = db.session.query(Admin).filter(Admin.admin_id == admin_id).first()
    listings = db.session.query(Vacant).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        rows = ""
        if listings:
            for i, listing in enumerate(listings, start=1):
                rows += f"""
                <tr>
                    <td>{i}</td>
                    <td>{listing.house_id}</td>
                    <td><img src="/static/properties/{listing.cover_image}" alt="Cover" style="width: 50px;"></td>
                    <td>{listing.house_price}</td>
                    <td>{listing.house_type.type_name}</td>
                    <td>{listing.landlord_id}</td>
                    <td>{listing.house_status}</td>
                    <td>{listing.is_featured}</td>
                    <td>{listing.location}</td>
                    <td>{listing.address}</td>
                    <td>{listing.description}</td>
                    <td>{listing.date_listed}</td>
                    <td><button type="button" data-id="{listing.house_id}" class="btn btn-success btn-sm featured">{"Featured" if listing.is_featured  else "Unfeatured"}</button></td>
                    <td><button type="button" data-id="{listing.house_id}" class="btn btn-danger btn-sm del">Delete</button></td>
                </tr>
                """
        else:
            rows = "<tr><td colspan='10' class='text-center'>No listings available for this landlord</td></tr>"
        return rows

    return render_template("admin/all_listings.html", list=listings,admin=admin)


@app.route("/admin/landlord/", methods=["POST", "GET"])
@login_required
def admin_landlord():
    admin_id = session.get("adminonline")
    admin = db.session.query(Admin).filter(Admin.admin_id == admin_id).first()

    landlord = db.session.query(Landlord).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        rows = ""
        if landlord:
            for i, l in enumerate(landlord, start=1):
                state_name = l.states.state_name if l.states else "N/A"
                rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><img src="/static/uploads/{l.profile_pictures}" alt="Cover" style="width: 50px;"></td>
                    <td>{l.landlord_fname}</td>
                    <td>{l.landlord_lname}</td>
                    <td>{l.landlord_email}</td>
                    <td>{l.landlord_phone}</td>
                    <td>{l.address}</td>
                    <td>{l.status}</td>
                    <td>{state_name}</td>
                    <td>{l.date_registered}</td>
                    <td><a class="btn btn-primary btn-sm details" href="/landlord/details/{l.landlord_id}/">Details</a></td>
                    <td><button type="button" class="btn btn-warning btn-sm toggle-block" data-id="{l.landlord_id}">{"Unblock" if l.status == "inactive" else "Block"}</button></td>
                    <td><button type="button" data-id="{l.landlord_id}" class="btn btn-danger btn-sm delete">Delete</button></td>
                </tr>
                """
        else:
            rows = "<tr><td colspan='10' class='text-center'>No listings available for this landlord</td></tr>"
        return rows

    return render_template("admin/landlord_listings.html", list=landlord,admin=admin)

@app.route("/blocked/landlord/", methods=["POST", "GET"])
@login_required
def blocked_landlord():
    admin_id = session.get("adminonline")
    admin = db.session.query(Admin).filter(Admin.admin_id == admin_id).first()

    landlord = db.session.query(Landlord).filter(Landlord.status == "inactive").all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        rows = ""
        if landlord:
            for i, l in enumerate(landlord, start=1):
                state_name = l.states.state_name if l.states else "N/A"
                rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><img src="/static/uploads/{l.profile_pictures}" alt="Cover" style="width: 50px;"></td>
                    <td>{l.landlord_fname}</td>
                    <td>{l.landlord_lname}</td>
                    <td>{l.landlord_email}</td>
                    <td>{l.landlord_phone}</td>
                    <td>{l.address}</td>
                    <td>{l.status}</td>
                    <td>{state_name}</td>
                    <td>{l.date_registered}</td>
                    <td><button type="button"  data-id="{l.landlord_id}" class="btn btn-primary btn-sm details">Details</button></td>
                    <td><button type="button" class="btn btn-warning btn-sm toggle-block" data-id="{l.landlord_id}">{"Unblock" if l.status == "inactive" else "Block"}</button></td>
                    <td><button type="button" data-id="{l.landlord_id}" class="btn btn-danger btn-sm delete">Delete</button></td>
                </tr>
                """
        else:
            rows = "<tr><td colspan='10' class='text-center'>No listings available for this landlord</td></tr>"
        return rows

    return render_template("admin/blocked_landlords.html", list=landlord,admin=admin)


@app.route("/landlord/details/<int:id>/", methods=["POST", "GET"])
@login_required
def landlord_details(id):
    admin_id = session.get("adminonline")
    admin = db.session.query(Admin).filter(Admin.admin_id == admin_id).first()
    landlord = db.session.query(Landlord).filter(Landlord.landlord_id == id).first()
    prop = db.session.query(Vacant).filter(Vacant.landlord_id == id).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data_type = request.args.get("type")

        if data_type == "landlord":
            rows = ""
            if landlord:
                landlord_list = [landlord]
                for i, l in enumerate(landlord_list, start=1):
                    state_name = l.states.state_name if l.states else "N/A"
                    rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td><img src="/static/uploads/{l.profile_pictures}" alt="Cover" style="width: 50px;"></td>
                        <td>{l.landlord_fname}</td>
                        <td>{l.landlord_lname}</td>
                        <td>{l.landlord_email}</td>
                        <td>{l.landlord_phone}</td>
                        <td>{l.address}</td>
                        <td>{l.status}</td>
                        <td>{state_name}</td>
                        <td>{l.date_registered}</td>
                    <td><button type="button" class="btn btn-warning btn-sm toggle-block" data-id="{l.landlord_id}">{"Unblock" if l.status == "inactive" else "Block"}</button></td>
                    <td><button  type="button" data-id="{l.landlord_id}" class="btn btn-danger btn-sm">Delete</button></td>
                    </tr>
                    """
            else:
                rows = "<tr><td colspan='10' class='text-center'>No landlord found</td></tr>"
            return rows

        elif data_type == "property":
            rows = ""
            if prop:
                for i, listing in enumerate(prop, start=1):
                    rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{listing.house_id}</td>
                        <td><img src="/static/properties/{listing.cover_image}" alt="Cover" style="width: 50px;"></td>
                        <td>{listing.house_price}</td>
                        <td>{listing.house_type.type_name}</td>
                        <td>{listing.landlord_id}</td>
                        <td>{listing.house_status}</td>
                        <td>{listing.is_featured}</td>
                        <td>{listing.location}</td>
                        <td>{listing.address}</td>
                        <td>{listing.description}</td>
                        <td>{listing.date_listed}</td>
                    </tr>
                    """
            else:
                rows = "<tr><td colspan='10' class='text-center'>No property listings found</td></tr>"
            return rows

    return render_template("admin/landlord_details.html", landlord=landlord, admin=admin, list=prop)


@app.route("/admin/tenant/", methods=["POST", "GET"])
@login_required
def admin_tenant():
    admin_id = session.get("adminonline")
    admin = db.session.query(Admin).filter(Admin.admin_id == admin_id).first()

    tenant = db.session.query(Tenant).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        rows = ""
        if tenant:
            for i, l in enumerate(tenant, start=1):
                rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><img src="/static/uploads/{l.profile_pictures}" alt="Cover" style="width: 50px;"></td>
                    <td>{l.tenant_fname}</td>
                    <td>{l.tenant_lname}</td>
                    <td>{l.tenant_email}</td>
                    <td>{l.tenant_phone}</td>
                    <td>{l.status}</td>
                    <td>{l.date_registered}</td>
                    <td><button type="button" class="btn btn-warning btn-sm tog-block" data-id="{l.tenant_id}">{"Unblock" if l.status == "inactive" else "Block"}</button></td>
                    <td><button  type="button" data-id="{l.tenant_id}" class="btn btn-danger btn-sm dele">Delete</button></td>
                </tr>
                """
        else:
            rows = "<tr><td colspan='10' class='text-center'>No listings available for this landlord</td></tr>"
        return rows

    return render_template("admin/tenant_listings.html", list=tenant,admin=admin)

@app.route("/blocked/tenant/", methods=["POST", "GET"])
@login_required
def blocked_tenant():
    admin_id = session.get("adminonline")
    admin = db.session.query(Admin).filter(Admin.admin_id == admin_id).first()

    tenant = db.session.query(Tenant).filter(Tenant.status == "inactive").all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        rows = ""
        if tenant:
            for i, l in enumerate(tenant, start=1):
                rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><img src="/static/uploads/{l.profile_pictures}" alt="Cover" style="width: 50px;"></td>
                    <td>{l.tenant_fname}</td>
                    <td>{l.tenant_lname}</td>
                    <td>{l.tenant_email}</td>
                    <td>{l.tenant_phone}</td>
                    <td>{l.status}</td>
                    <td>{l.date_registered}</td>
                    <td><button type="button" class="btn btn-warning btn-sm tog-block" data-id="{l.tenant_id}">{"Unblock" if l.status == "inactive" else "Block"}</button></td>
                    <td><button  type="button" data-id="{l.tenant_id}" class="btn btn-danger btn-sm dele">Delete</button></td>
                </tr>
                """
        else:
            rows = "<tr><td colspan='10' class='text-center'>No listings available for this landlord</td></tr>"
        return rows

    return render_template("admin/blocked_tenants.html", list=tenant,admin=admin)



@app.route('/admin/delete/<int:id>',methods=['POST'])
@login_required
def admin_delete(id):
    landlord = db.session.query(Landlord).filter(Landlord.landlord_id == id).first()

    if landlord:
        db.session.delete(landlord)
        db.session.commit()
        return "User Deleted",200
    else:
        return "user not found",404 

@app.route('/tenant/delete/<int:id>',methods=['POST'])
@login_required
def tenant_delete(id):
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == id).first()

    if tenant:
        db.session.delete(tenant)
        db.session.commit()
        return "User Deleted",200
    else:
        return "user not found",404

@app.route('/list/delete/<int:id>',methods=['POST'])
@login_required
def list_delete(id):
    prop = db.session.query(Vacant).filter(Vacant.house_id == id).first()

    if prop:
        db.session.delete(prop)
        db.session.commit()
        return "House Deleted",200
    else:
        return "House not found",404


@app.route('/admin/blocked/<int:id>',methods=['POST'])
@login_required
def admin_blocked(id):
    landlord = db.session.query(Landlord).filter(Landlord.landlord_id == id).first()

    if landlord:
        if landlord.status == 'active':
            landlord.status = 'inactive'
        else:
            landlord.status = 'active'
        db.session.commit()
        return "Landlord Blocked", 200
    return "Landlord Not found", 404

@app.route('/tenant/blocked/<int:id>',methods=['POST'])
@login_required
def tenant_blocked(id):
    tenant = db.session.query(Tenant).filter(Tenant.tenant_id == id).first()

    if tenant:
        if tenant.status == 'active':
            tenant.status = 'inactive'
        else:
            tenant.status = 'active'
        db.session.commit()
        return "Tenant Blocked", 200
    return "Tenant Not found", 404


@app.route("/admin/logout/")
def admin_logout():
    if session.get("adminonline") != None:
        session.pop("adminonline", None)
        session.pop("usertype", None)
    return redirect(url_for("admin_login"))


@app.route("/featured/<int:id>", methods=["POST"])
@login_required
def featured(id):
    existing = Vacant.query.filter(Vacant.house_id==id).first()
    if existing:
        existing.is_featured = True
        db.session.commit()
        return "Property marked as featured"
    else:
        return "Property ID not found"


@app.route("/unfeatured/<int:id>", methods=["POST"])
@login_required
def unfeatured(id):
    existing = Vacant.query.filter(Vacant.house_id==id).first()
    if existing:
        existing.is_featured = False
        db.session.commit()
        return "Featured status removed"
    else:
        return "Property ID not found"
