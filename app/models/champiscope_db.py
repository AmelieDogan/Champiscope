from ..app import app, db

#Tables de relation

surface_champi = db.Table(
    "surface_champi",
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('zone_id', db.String(25), db.ForeignKey('zone.id')),
    db.Column('surface_id', db.Integer, db.ForeignKey('surface.id'))
)

forme_champi = db.Table(
    "forme_champi",
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('zone_id', db.String(25), db.ForeignKey('zone.id')),
    db.Column('forme_id', db.Integer, db.ForeignKey('forme.id'))
)

couleur_champi = db.Table(
    "couleur_champi",
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('zone_id', db.String(25), db.ForeignKey('zone.id')),
    db.Column('couleur_id', db.Integer, db.ForeignKey('couleur.id'))
)

type_lamelle_champi = db.Table(
    "type_lamelle_champi",
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('type_lamelle_id', db.Integer, db.ForeignKey('type_lamelle.id'))
)

insertion_pied_chapeau = db.Table(
    "insertion_pied_chapeau",
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('mode_insertion_id', db.Integer, db.ForeignKey('mode_insertion.id'))
)

confusion = db.Table(
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('confusion_id', db.Integer, db.ForeignKey('referentiel.taxref_id'))
)

taxon_superieur = db.Table(
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('taxsup_id', db.Integer, db.ForeignKey('referentiel.taxref_id'))
)

milieu_champi = db.Table(
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('milieu_id', db.Integer, db.ForeignKey('milieu.id'))
)

#Classes pour tables
class Referentiel(db.Model):
    __tablename__="referentiel"
    taxref_id = db.Column(db.Integer, primary_key = True, unique=True)
    rang = db.Column(db.String(25))
    nom = db.Column(db.String(250))
    auteur = db.Column(db.String(250))
    date = db.Column(db.Integer)
    nom_complet = db.Column(db.String(250))
    nom_complet_html = db.Column(db.String(250))
    nom_vernaculaire = db.Column(db.String(250))
    est_reference = db.Column(db.Boolean)
    #Foreign keys
    reference_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'))
    habitat_id = db.Column(db.Integer, db.ForeignKey('habitat.id'))

    #Relations entre Referentiel et les autres tables PAS de relation
    referentiels_mois_pousse = db.relationship("Referentiel", backref="mois_pousse", uselist=False)
    referentiels_description_champignon = db.relationship("Referentiel", backref="description_champigon", uselist=False)
    referentiels_observation_humaine = db.relationship("Referentiel", backref="observation_humaine", uselist=False)
    referentiels_presence = db.relationship("Referentiel", backref="presence", uselist=False)
    referentiels_habitat = db.relationship("Referentiel", backref="habitat", uselist=False)
    referentiels_confusion = db.relationship("Referentiel", backref="confusion", uselist=False)
    referentiels_iconographie = db.relationship("Referentiel", backref="iconographie", uselist=False)
    referentiels_taxon_superieur = db.relationship("Referentiel", backref="taxon_superieur", uselist=False)

    def __repr__(self):
        return '<Referentiel %r>' % (self.name) 

class Surface(db.Model):
    __tablename__="surface"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    surface = db.Column(db.String(250))

    #Relation entre surface et referentiel via surface_champi
    surfaces = db.relationship("Surface", secondary=surface_champi, backref="referentiel")
    def __repr__(self):
        return '<Surface %r>' % (self.name) 

class Zone(db.Model):
    __tablename__="zone"
    id = db.Column(db.String(25), primary_key = True, unique=True)
    zone = db.Column(db.String(250))

    #Relation entre zone et referentiel via surface_champi
    zones_surface = db.relationship("Zone", secondary=surface_champi, backref="referentiel")

    #Relation entre zone et referentiel via surface_champi
    zones_forme = db.relationship("Zone", secondary=forme_champi, backref="referentiel")

    #Relation entre zone et referentiel via surface_champi
    zones_couleur = db.relationship("Zone", secondary=couleur_champi, backref="referentiel")

    def __repr__(self):
        return '<Zone %r>' % (self.name) 

class Forme(db.Model):
    __tablename__="forme"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    forme = db.Column(db.String(250))

    #Relation entre zone et referentiel via surface_champi
    formes_champis = db.relationship("Forme", secondary=forme_champi, backref="referentiel")

    def __repr__(self):
        return '<Forme %r>' % (self.name) 

class Couleur(db.Model):
    __tablename__="couleur"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    couleur = db.Column(db.String(250))

    #Relation de couleur à référentiel via couleur_champi
    couleurs = db.relationship("Couleur", secondary=couleur_champi, backref="referentiel"
                               )
    def __repr__(self):
        return '<Couleur %r>' % (self.name) 

class TypeLamelle(db.Model):
    __tablename__="type_lamelle"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    type_lamelle = db.Column(db.String(250))

    #Relation entre type lamelle et referentiel via type lamelle champi
    types_lamelles = db.relationship("TypeLamelle", secondary=type_lamelle_champi, backref="referentiel")

    def __repr__(self):
        return '<TypeLamelle %r>' % (self.name) 

class ModeInsertion(db.Model):
    __tablename__="mode_insertion"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    mode_insertion = db.Column(db.String(250))


    #Relation entre mode insertion et referentiel via insertion pied chapeau
    mode_insertions = db.relationship("mode_insertion", secondary=insertion_pied_chapeau, backref="referentiel")

    def __repr__(self):
        return '<ModeInsertion %r>' % (self.name) 

class Danger(db.Model):
    __tablename__="danger"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    degre = db.Column(db.String(25))
    uicn_categorie = db.Column(db.String(250))

    #Relation entre danger et referentiel via liste_rouge
    dangers = db.relationship("danger", secondary=liste_rouge, backref="referentiel")

    def __repr__(self):
        return '<Danger %r>' % (self.name) 

class Iconographie(db.Model):
    __tablename__="iconographie"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    url_image = db.Column(db.Text)
    credit = db.Column(db.String(250))
    #Foreign key
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'))

    def __repr__(self):
        return '<Iconographie %r>' % (self.name) 

class Habitat(db.Model):
    __tablename__="habitat"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    nom = db.Column(db.String(250))
    definition = db.Column(db.String(250))

    def __repr__(self):
        return '<Habitat %r>' % (self.name) 

class Milieu(db.Model):
    __tablename__="milieu"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    milieu = db.Column(db.String(250))

    #Relation entre milieu et referentiel via surface_champi
    milieux = db.relationship("Milieu", secondary=milieu_champi, backref="referentiel")

    def __repr__(self):
        return '<Milieu %r>' % (self.name) 

class Presence(db.Model):
    __tablename__="presence"
    FR = db.Column(db.Boolean)
    GF = db.Column(db.Boolean)
    MAR = db.Column(db.Boolean)
    GUA = db.Column(db.Boolean)
    SM = db.Column(db.Boolean)
    SB = db.Column(db.Boolean)
    SPM = db.Column(db.Boolean)
    MAY = db.Column(db.Boolean)
    EPA = db.Column(db.Boolean)
    REU = db.Column(db.Boolean)
    SA = db.Column(db.Boolean)
    TA = db.Column(db.Boolean)
    PF = db.Column(db.Boolean)
    NC = db.Column(db.Boolean)
    WF = db.Column(db.Boolean)
    CLI = db.Column(db.Boolean)
    #Foreign key
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'))

    def __repr__(self):
        return '<Presence %r>' % (self.name) 

class ObservationHumaine(db.Model):
    __tablename__="observation_humaine"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    latitude_decimale = db.Column(db.Float)
    longitude_decimale = db.Column(db.Float)
    jour = db.Column(db.Integer)
    mois = db.Column(db.Integer)
    annee = db.Column(db.Integer)
    identifie_par = db.Column(db.String(250))
    #Foreign key
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'))

    def __repr__(self):
        return '<ObservationHumaine %r>' % (self.name) 

class MoisPousse(db.Model):
    __tablename__="mois_pousse"
    janvier = db.Column(db.Boolean)
    fevrier = db.Column(db.Boolean)
    mars = db.Column(db.Boolean)
    avril = db.Column(db.Boolean)
    mai = db.Column(db.Boolean)
    juin = db.Column(db.Boolean)
    juillet = db.Column(db.Boolean)
    aout = db.Column(db.Boolean)
    septembre = db.Column(db.Boolean)
    octobre = db.Column(db.Boolean)
    novembre = db.Column(db.Boolean)
    decembre = db.Column(db.Boolean)
    #Foreign key
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'))

    def __repr__(self):
        return '<MoisPousse %r>' % (self.name) 

class DescriptionChampignon(db.Model):
    __tablename__="description_champignon"
    diametre_chapeau_min = db.Column(db.Float)
    diametre_chapeau_max = db.Column(db.Float)
    dessous_chapeau = db.Column(db.String(250))
    oxydation_chapeau = db.Column(db.Boolean)
    espace_entre_lamelles = db.Column(db.String(250))
    pied_creux_ou_plein = db.Column(db.String(250))
    position_pied_chapeau = db.Column(db.String(250))
    presence_anneau = db.Column(db.Boolean)
    pousse_en_touffe = db.Column(db.Boolean)
    oxydation_chair = db.Column(db.Boolean)
    odeur = db.Column(db.String(250))
    latex = db.Column(db.Boolean)
    pousse_sur_du_bois = db.Column(db.Boolean)
    comestibilite = db.Column(db.Boolean)
    comestibilite_detail = db.Column(db.String(250))
    commentaires = db.Column(db.String(250))
     #Foreign key
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'))

    def __repr__(self):
        return '<DescriptionChampignon %r>' % (self.name) 

# Table de relation liste_rouge avant que je la transforme en classe (elle était tout en haut du fichier)    
# liste_rouge = db.Table(
#     "liste_rouge",
#     db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
#     db.Column('id_danger', db.Integer, db.ForeignKey('danger.id')),
#     db.Column('tendance', db.String(250)),
#     db.Column('annee', db.Integer)
#     )  

class ListeRouge(db.Model):
    __tablename__ = "liste_rouge",
    #Foreign keys
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id')),
    id_danger = db.Column(db.Integer, db.ForeignKey('danger.id')),
    #Autres colonnes
    tendance = db.Column(db.String(250)),
    annee = db.Column(db.Integer)
