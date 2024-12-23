from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import folium

views = Blueprint('views', __name__)

# @views.route('/')
# def home():
#     map_center = [31.25181, 34.7913]
#     beer_sheva_map = folium.Map(location=map_center, zoom_start=13)
#     # Save the map to an HTML file
#     beer_sheva_map.save('website/templates/map.html')
#     with open('website/templates/map.html') as f:
#         map=f.read()
#     return render_template("home.html", user=current_user, map=map)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note
            db.session.add(new_note) #adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')

    map_center = [31.25181, 34.7913]
    beer_sheva_map = folium.Map(location=map_center, zoom_start=13)
    # Save the map to an HTML file
    beer_sheva_map.save('website/templates/map.html')
    with open('website/templates/map.html') as f:
        map = f.read()
    return render_template("home.html", user=current_user, map=map)




@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
