from models import *
import datetime
#----------------------------------------------------------------------------#
# Populate database
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# artists
#----------------------------------------------------------------------------#

# guns n petals
artist1 = Artist(
    name="Guns N Petals",
    city="San Francisco",
    state="CA",
    phone="326-123-5000",
    genres=["Rock n Roll"],
    facebook_link="https://www.facebook.com/GunsNPetals",
    image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    website="https://www.gunsnpetalsband.com",
    seeking_venues=True,
    seeking_description="Looking for shows to perform at in the San Francisco Bay Area!"
)

# matt queved
artist2 = Artist(
    name="Matt Quevedo",
    city="New York",
    state="NY",
    phone="300-400-5000",
    genres=["Jazz"],
    facebook_link="https://www.facebook.com/mattquevedo923251523",
    image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    seeking_venues=False
)

# the wild sax band
artist3 = Artist(
    name="The Wild Sax Band",
    city="San Francisco",
    state="CA",
    phone="432-325-5432",
    genres=["Jazz", "Classical"],
    image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    seeking_venues=False
)

#----------------------------------------------------------------------------#
# venues
#----------------------------------------------------------------------------#
# The Musical Hop
# Park Square Live Music & Coffee
# The Dueling Pianos Bar
venue1 = Venue(
    name="The Musical Hop",
    city="San Francisco",
    state="CA",
    address="1015 Folsom Street",
    phone="123-123-1234",
    genres=["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    facebook_link="https://www.facebook.com/TheMusicalHop",
    image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    website="https://www.themusicalhop.com",
    seeking_talent=True,
    seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",
)

venue2 = Venue(
    name="The Dueling Pianos Bar",
    city="New York",
    state="NY",
    address="335 Delancey Street",
    phone="914-003-1132",
    genres=["Classical", "R&B", "Hip-Hop"],
    facebook_link="https://www.facebook.com/theduelingpianos",
    image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    website="https://www.theduelingpianos.com",
    seeking_talent=False
)

venue3 = Venue(
    name="Park Square Live Music & Coffee",
    city="San Francisco",
    state="CA",
    address="34 Whiskey Moore Ave",
    phone="415-000-1234",
    genres=["Rock n Roll", "Jazz", "Classical", "Folk"],
    facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    website="https://www.parksquarelivemusicandcoffee.com",
    seeking_talent=False
)

#----------------------------------------------------------------------------#
# shows
#----------------------------------------------------------------------------#
# --- artists
# 1: "Guns N Petals"
# 2: "Matt Quevedo",
# 3: "The Wild Sax Band",
# --- venues
# 1: "The Musical Hop",
# 2: "The Dueling Pianos Bar",
# 3: "Park Square Live Music & Coffee",
shows = [
    Show(artist_id=1, venue_id=1, start_time=datetime.datetime(
        year=2019, month=5, day=21, hour=21, minute=30)),
    Show(artist_id=2, venue_id=3, start_time=datetime.datetime(
        year=2019, month=6, day=15, hour=23, minute=0)),
    Show(artist_id=3, venue_id=3, start_time=datetime.datetime(
        year=2035, month=4, day=1, hour=20, minute=0)),
    Show(artist_id=3, venue_id=3, start_time=datetime.datetime(
        year=2035, month=4, day=8, hour=20, minute=0)),
    Show(artist_id=3, venue_id=3, start_time=datetime.datetime(
        year=2035, month=4, day=15, hour=20, minute=0))
]


if __name__ == "__main__":
    db.session.add_all([artist1, artist2, artist3])
    db.session.commit()

    db.session.add_all([venue1, venue2, venue3])
    db.session.commit()

    db.session.add_all(shows)
    db.session.commit()
