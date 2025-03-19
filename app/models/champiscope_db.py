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
    "confusion",
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('confusion_id', db.Integer, db.ForeignKey('referentiel.taxref_id'))
)

taxon_superieur = db.Table(
    "taxon_superieur",
    db.Column('taxref_id', db.Integer, db.ForeignKey('referentiel.taxref_id')),
    db.Column('taxsup_id', db.Integer, db.ForeignKey('referentiel.taxref_id'))
)

milieu_champi = db.Table(
    "milieu_champi",
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

    synonymes = db.relationship(
        'Referentiel',
        backref=db.backref('reference', remote_side=[taxref_id]),
        foreign_keys=[reference_id]
    )

    mois_pousses = db.relationship("MoisPousse", backref="mois_pousses", lazy=True)
    description_champignons = db.relationship("DescriptionChampignon", backref="description_champignons", lazy=True)
    observation_humaines = db.relationship("ObservationHumaine", backref="observation_humaines", lazy=True)
    presences = db.relationship("Presence", backref="presences", lazy=True)
    habitats = db.relationship("Habitat", backref="habitats", lazy=True)
    iconographies = db.relationship("Iconographie", backref="iconographies", lazy=True)
    liste_rouges = db.relationship("ListeRouge", backref="liste_rouges", lazy=True)

    confusions = db.relationship(
        'Referentiel', secondary=confusion,
        primaryjoin=(confusion.c.taxref_id == taxref_id),
        secondaryjoin=(confusion.c.confusion_id == taxref_id),
        backref=db.backref('confused_with', lazy='dynamic'), lazy='dynamic')
    
    taxon_superieurs = db.relationship(
        'Referentiel', secondary=taxon_superieur,
        primaryjoin=(taxon_superieur.c.taxref_id == taxref_id),
        secondaryjoin=(taxon_superieur.c.taxsup_id == taxref_id),
        backref=db.backref('taxon_parent_de', lazy='dynamic'), lazy='dynamic')
    
    surfaces_associées = db.relationship("Surface", secondary=surface_champi, back_populates="referentiels")
    formes_associées = db.relationship("Forme", secondary=forme_champi, back_populates="referentiels")
    couleurs_associées = db.relationship("Couleur", secondary=couleur_champi, back_populates="referentiels")

    def __repr__(self):
        return '<Referentiel %r>' % (self.name) 

class Surface(db.Model):
    __tablename__="surface"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    surface = db.Column(db.String(250))

    zones = db.relationship("Zone", secondary=surface_champi, back_populates="surfaces")
    referentiels = db.relationship("Referentiel", secondary=surface_champi, back_populates="surfaces_associées")

    def __repr__(self):
        return '<Surface %r>' % (self.name) 

class Zone(db.Model):
    __tablename__="zone"
    id = db.Column(db.String(25), primary_key = True, unique=True)
    zone = db.Column(db.String(250))

    surfaces = db.relationship("Surface", secondary=surface_champi, back_populates="zones")
    formes = db.relationship("Forme", secondary=forme_champi, back_populates="zones")
    couleurs = db.relationship("Couleur", secondary=couleur_champi, back_populates="zones")

    def __lt__(self, other):
        return self.zone < other.zone  # Comparaison basée sur le nom de la zone

    def __repr__(self):
        return '<Zone %r>' % (self.name) 

class Forme(db.Model):
    __tablename__="forme"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    forme = db.Column(db.String(250))

    zones = db.relationship("Zone", secondary=forme_champi, back_populates="formes")
    referentiels = db.relationship("Referentiel", secondary=forme_champi, back_populates="formes_associées")

    def __repr__(self):
        return '<Forme %r>' % (self.name) 

class Couleur(db.Model):
    __tablename__="couleur"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    couleur = db.Column(db.String(250))

    zones = db.relationship("Zone", secondary=couleur_champi, back_populates="couleurs")
    referentiels = db.relationship("Referentiel", secondary=couleur_champi, back_populates="couleurs_associées")
    
    def __repr__(self):
        return '<Couleur %r>' % (self.name) 

class TypeLamelle(db.Model):
    __tablename__="type_lamelle"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    type_lamelle = db.Column(db.String(250))

    #Relation entre type lamelle et referentiel via type lamelle champi
    referentiels = db.relationship("Referentiel", secondary=type_lamelle_champi, backref="types_lamelle_associés")

    def __repr__(self):
        return '<TypeLamelle %r>' % (self.name) 

class ModeInsertion(db.Model):
    __tablename__="mode_insertion"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    mode_insertion = db.Column(db.String(250))


    #Relation entre mode insertion et referentiel via insertion pied chapeau
    referentiels = db.relationship("Referentiel", secondary=insertion_pied_chapeau, backref="modes_insertion_associés")

    def __repr__(self):
        return '<ModeInsertion %r>' % (self.name) 

class Danger(db.Model):
    __tablename__="danger"
    id = db.Column(db.Integer, primary_key = True, unique=True)
    degre = db.Column(db.String(25))
    uicn_categorie = db.Column(db.String(250))

    #Relation entre danger liste_rouge
    dangers = db.relationship("ListeRouge", backref="liste_rouge", lazy=True)

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
    referentiels = db.relationship("Referentiel", secondary=milieu_champi, backref="milieux_associés")

    def __repr__(self):
        return '<Milieu %r>' % (self.name) 

class Presence(db.Model):
    __tablename__="presence"
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'), primary_key=True)
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
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'), primary_key=True)
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

    def __repr__(self):
        return '<MoisPousse %r>' % (self.name) 

class DescriptionChampignon(db.Model):
    __tablename__="description_champignon"
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'), primary_key=True)
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

    def __repr__(self):
        return '<DescriptionChampignon %r>' % (self.name) 

class ListeRouge(db.Model):
    __tablename__ = "liste_rouge",
    taxref_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'), primary_key=True)
    danger_id = db.Column(db.Integer, db.ForeignKey('danger.id'), primary_key=True)
    tendance = db.Column(db.String(250))
    annee = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<ListeRouge %r>' % (self.name) 