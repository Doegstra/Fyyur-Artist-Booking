#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    Response,
    url_for
)
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import sys
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

# ----------------------------------------------------------------
#  Venues
# ----------------------------------------------------------------


@app.route('/venues')
def venues():

    data = []

    # get all distinct cities
    cities = db.session.query(Venue.city, Venue.state).distinct()
    for city in cities:
        data.append({
            "city": city.city,
            "state": city.state,
            "venues": []
        })

    # get number of shows per venue (if at least one show)
    shows_count = {}
    for row in Show.query.with_entities(
            Show.venue_id, func.count(Show.venue_id)).group_by(Show.venue_id).all():
        shows_count[row.venue_id] = row.count

    # fill venue information in data
    venues = Venue.query.all()
    for venue in venues:
        num_shows = 0
        if venue.id in shows_count:
            num_shows = shows_count[venue.id]
        for element in data:
            if (element["city"] == venue.city) and (element["state"] == venue.state):
                element["venues"].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_shows,
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search on artists with partial string search (case-insensitive).
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    relevant_venues = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    # get number of shows per venue (if at least one show)
    shows_count = {}
    for row in Show.query.with_entities(
            Show.venue_id, func.count(Show.venue_id)).group_by(Show.venue_id).all():
        shows_count[row.venue_id] = row.count

    response = {}
    response["count"] = len(relevant_venues)
    data = []
    for venue in relevant_venues:
        num_shows = 0
        if venue.id in shows_count:
            num_shows = shows_count[venue.id]
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_shows,
        })
    response["data"] = data

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)

    # get info on past and upcoming shows
    past_shows = []
    upcoming_shows = []
    now = datetime.now()

    shows_details = db.session.query(Show).join(
        Artist).filter(Show.venue_id == venue_id).all()

    for show in shows_details:
        info_dict = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > now:
            upcoming_shows.append(info_dict)
        else:
            past_shows.append(info_dict)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    try:
        new_venue = Venue(name=form.name.data,
                          city=form.city.data,
                          state=form.state.data,
                          address=form.address.data,
                          phone=form.phone.data,
                          image_link=form.image_link.data,
                          genres=form.genres.data,
                          facebook_link=form.facebook_link.data,
                          seeking_description=form.seeking_description.data,
                          seeking_talent=form.seeking_talent == True
                          )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        venue = Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash(f'Venue {venue_id} was successfully deleted.')
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash(f'An error occurred. Venue {venue_id} could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = []

    artists = Artist.query.with_entities(Artist.id, Artist.name).all()

    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    relevant_artists = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    # get number of shows per venue (if at least one show)
    shows_count = {}
    for row in Show.query.with_entities(
            Show.artist_id, func.count(Show.artist_id)).group_by(Show.artist_id).all():
        shows_count[row.artist_id] = row.count

    response = {}
    response["count"] = len(relevant_artists)
    data = []
    for artist in relevant_artists:
        num_shows = 0
        if artist.id in shows_count:
            num_shows = shows_count[artist.id]
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_shows,
        })
    response["data"] = data

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)

    # get info on past and upcoming shows
    past_shows = []
    upcoming_shows = []
    now = datetime.now()

    show_details = db.session.query(Show).join(
        Venue).filter(Show.artist_id == artist_id).all()

    for show in show_details:
        info_dict = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > now:
            upcoming_shows.append(info_dict)
        else:
            past_shows.append(info_dict)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": "".join(artist.genres[1:-1]).split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)


@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

    try:
        artist = Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
        flash(f'Artist {artist_id} was successfully deleted.')
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash(f'An error occurred. Artist {artist_id} could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    venue = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    try:
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website_link.data
        artist.image_link = form.image_link.data
        artist.seeking_venues = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
        flash(f'Artist {artist.name} has been updated.')
    except SQLAlchemyError as e:
        print(e)
        flash(f'An error occured while trying to update Artist {artist.name}.')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    try:
        venue = Venue.query.get(venue_id)

        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website_link.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
        flash(f'Venue {venue.name} has been updated.')
    except SQLAlchemyError as e:
        print(e)
        flash(f'An error occured while trying to update Venue {venue.name}.')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    try:
        new_artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            seeking_description=form.seeking_description.data,
            seeking_venues=form.seeking_venue == True
        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] +
              ' was successfully listed!')
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    results = Venue.query.with_entities(
        Venue.id.label("venue_id"),
        Venue.name.label("venue_name"),
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Show.start_time.label("start_time")).join(Show, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).all()

    data = []
    for row in results:
        data.append({
            "venue_id": row.venue_id,
            "venue_name": row.venue_name,
            "artist_id": row.artist_id,
            "artist_name": row.artist_name,
            "artist_image_link": row.artist_image_link,
            "start_time": format_datetime(str(row.start_time))
        })

    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )

        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
