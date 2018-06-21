import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session

from model import Donation, Donor

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    """Handle creation of donors and donations."""
    # If user types an existing name, add a donation for such name
    # If user types a new name, create a new donor
    if request.method == 'POST':
        donor = request.form['name']
        amount = int(request.form['number'])
        query = Donor.select().where(Donor.name == donor)
        if query.exists():
            Donation(donor=query.get(), value=amount).save()
            return redirect(url_for('all'))
        else:
            new_donor = Donor(name=donor)
            new_donor.save()
            Donation(donor=new_donor, value=amount).save()
            return redirect(url_for('all'))
    return render_template('create.jinja2')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
