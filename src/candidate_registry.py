from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    candidate_name: str
    bloc: str
    country: str = "CO"
    election_year: int = 2026


CANDIDATES = [
    Candidate("ivan_cepeda", "Iván Cepeda", "izquierda"),
    Candidate("paloma_valencia", "Paloma Valencia", "derecha"),
    Candidate("sergio_fajardo", "Sergio Fajardo", "centro"),
    Candidate("claudia_lopez", "Claudia López", "centro"),
    Candidate("abelardo_de_la_espriella", "Abelardo de la Espriella", "derecha"),
    Candidate("luis_gilberto_murillo", "Luis Gilberto Murillo", "centro"),
    Candidate("roy_barreras", "Roy Barreras", "centro-izquierda"),
]
