from datetime import date, datetime, time

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LogEntry(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False, default=date.today)
    entry_time = db.Column(db.Time, nullable=False, default=lambda: datetime.now().time().replace(microsecond=0))
    category = db.Column(db.String(80), nullable=False)
    responsible = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=True)
    evidence = db.Column(db.String(255), nullable=True)


class Maintenance(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False, unique=True)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    priority = db.Column(db.String(30), nullable=False, default="Media")
    status = db.Column(db.String(40), nullable=False, default="Agendada")
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    start_time = db.Column(db.Time, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    responsible = db.Column(db.String(120), nullable=True)
    provider = db.Column(db.String(120), nullable=True)
    amount = db.Column(db.Numeric(12, 2), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.String(255), nullable=True)


class Occurrence(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False, unique=True)
    category = db.Column(db.String(80), nullable=False)
    occurred_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    apartment = db.Column(db.String(30), nullable=True)
    block = db.Column(db.String(60), nullable=True)
    resident = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=False)
    witnesses = db.Column(db.Text, nullable=True)
    affects_residents = db.Column(db.Boolean, nullable=False, default=False)
    requires_fine = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(40), nullable=False, default="Aberta")
    evidence = db.Column(db.String(255), nullable=True)


class Purchase(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(140), nullable=False)
    quantity = db.Column(db.String(60), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(40), nullable=False, default="Normal")
    has_quote = db.Column(db.Boolean, nullable=False, default=False)
    supplier = db.Column(db.String(120), nullable=True)
    amount = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="Solicitada")
    attachment = db.Column(db.String(255), nullable=True)


def parse_date(value, fallback=None):
    if not value:
        return fallback
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_time(value):
    if not value:
        return None
    return datetime.strptime(value, "%H:%M").time()


def parse_decimal(value):
    normalized = (value or "").replace(".", "").replace(",", ".").strip()
    return float(normalized) if normalized else None


def seed_initial_data():
    if LogEntry.query.first():
        return

    db.session.add_all(
        [
            LogEntry(
                entry_date=date.today(),
                entry_time=time(8, 0),
                category="Limpeza",
                responsible="Joao",
                title="Limpeza dos halls finalizada",
                description="Todos os blocos foram conferidos e liberados.",
                location="Blocos A, B e C",
                evidence="IMG_001.jpg",
            ),
            Maintenance(
                code="MAN-0001",
                title="Inspecao preventiva do elevador",
                category="Elevador",
                priority="Alta",
                status="Em execucao",
                start_date=date.today(),
                start_time=time(9, 30),
                responsible="Equipe de manutencao",
                provider="Elevadores Alfa",
                location="Torre 1",
                description="Revisao preventiva com checagem de cabos, portas e painel.",
            ),
            Occurrence(
                code="OCO-0001",
                category="Convivencia",
                occurred_at=datetime.combine(date.today(), time(10, 15)),
                apartment="302",
                block="B",
                resident="Morador informado",
                description="Registro de barulho recorrente em horario de descanso.",
                affects_residents=True,
                requires_fine=False,
                status="Em analise",
            ),
            Purchase(
                material="Lampadas LED para areas comuns",
                quantity="24 unidades",
                purpose="Reposicao de pontos queimados nos corredores.",
                urgency="Normal",
                has_quote=False,
                status="Aguardando orcamento",
            ),
        ]
    )
    db.session.commit()
