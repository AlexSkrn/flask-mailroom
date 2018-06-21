"""This is the main module with functions for the web-based mailroom."""
import os

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Donation, Donor, User

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY').encode()


@app.route('/')
def home():
    """Handle calls to the root of the web site."""
    return redirect(url_for('show_all'))


@app.route('/donations/')
def show_all():
    """Handle a page showing all donors and donations."""
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    """Handle creation of donors and donations."""
    # If user types an existing name, add a donation for such name
    # If user types a new name, create a new donor
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        donor = request.form['name']
        amount = int(request.form['number'])
        query = Donor.select().where(Donor.name == donor)
        if query.exists():
            Donation(donor=query.get(), value=amount).save()
            return redirect(url_for('show_all'))
        else:
            new_donor = Donor(name=donor)
            new_donor.save()
            Donation(donor=new_donor, value=amount).save()
            return redirect(url_for('show_all'))
    return render_template('create.jinja2')


def show_single(donor, donations):
    """Provide a helper function to render donations for a single donor."""
    return render_template('show_single.jinja2',
                           donor=donor,
                           donations=donations)


@app.route('/single/')
def get_single():
    """Handle calls to a page to view donations for a single donor."""
    donor_name = request.args.get('name', None)

    if donor_name is None:
        return render_template('single.jinja2')
    try:
        donor = Donor.get(Donor.name == donor_name)
    except Donor.DoesNotExist:
        return render_template('single.jinja2', error="Donor not found")

    try:
        donations = Donation.select().where(Donation.donor == donor)
    except Donation.DoesNotExist:
        return render_template('single.jinja2', error="Donations not found")

    return show_single(donor, donations)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Provide a handler for the user login template."""
    if request.method == 'POST':
        try:
            user = User.select().where(User.name == request.form['name']).get()
        except User.DoesNotExist:
            return render_template('login.jinja2',
                                   error='Incorrect username or password'
                                   )

        if user and pbkdf2_sha256.verify(request.form['password'], user.password):
            session['username'] = request.form['name']
            return redirect(url_for('show_all'))
        return render_template('login.jinja2',
                               error='Incorrect username or password'
                               )
    else:
        return render_template('login.jinja2')


@app.route('/logout')
def logout():
    """Provide a hander for the user logout template."""
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
