from .database import Base, engine, SessionLocal
from .models import Auto

AUTOS = [
    ("Toyota", "Corolla Cross", 2024, "SUV", 29500, 3, "Blanco", "Híbrido"),
    ("Toyota", "Hilux", 2024, "Pickup", 42000, 2, "Gris", "Diesel"),
    ("Volkswagen", "T-Cross", 2024, "SUV", 27800, 4, "Rojo", "Nafta"),
    ("Volkswagen", "Polo", 2024, "Hatchback", 21000, 5, "Azul", "Nafta"),
    ("Volkswagen", "Taos", 2024, "SUV", 34500, 1, "Negro", "Nafta"),
    ("Ford", "Territory", 2023, "SUV", 31000, 2, "Gris", "Nafta"),
    ("Ford", "Ranger", 2024, "Pickup", 45000, 0, "Blanco", "Diesel"),
    ("Chevrolet", "Tracker", 2024, "SUV", 26500, 6, "Azul", "Nafta"),
    ("Chevrolet", "Cruze", 2023, "Sedan", 28000, 2, "Negro", "Nafta"),
    ("Renault", "Kwid", 2024, "Hatchback", 14500, 8, "Naranja", "Nafta"),
    ("Renault", "Duster", 2024, "SUV", 24500, 3, "Verde", "Nafta"),
    ("Peugeot", "2008", 2024, "SUV", 28900, 2, "Blanco", "Nafta"),
    ("Fiat", "Cronos", 2024, "Sedan", 19500, 5, "Gris", "Nafta"),
    ("BYD", "Dolphin", 2024, "Hatchback", 33000, 2, "Celeste", "Eléctrico"),
]


def run():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    for marca, modelo, anio, tipo, precio, stock, color, comb in AUTOS:
        db.add(Auto(marca=marca, modelo=modelo, anio=anio, tipo=tipo,
                    precio_usd=precio, stock=stock, color=color, combustible=comb))
    db.commit()
    db.close()
    print(f"Base creada con {len(AUTOS)} autos")


if __name__ == "__main__":
    run()
