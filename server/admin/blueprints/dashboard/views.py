# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   render_template,
                   g)


from admin.decorators import login_required


blueprint = Blueprint('dashboard', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    configure = g.configure

    count = {
        'users': current_app.mongodb.User.find().count(),
        'books': current_app.mongodb.Book.find().count(),
    }
    overtime_vols = []
    if configure['rental_time_limit']:
        vol_list = current_app.mongodb.\
            BookVolume.find_overtime(configure['rental_time_limit'])
        for vol in vol_list:
            vol['overtime'] = True
            overtime_vols.append(vol)

    return render_template('dashboard.html',
                           count=count,
                           overtime_vols=overtime_vols)
