from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .extensions import db
from .models import LogEntry, Maintenance, Occurrence, Purchase, parse_date, parse_decimal, parse_time


main_bp = Blueprint("main", __name__)


def normalize_text(value):
    return (value or "").strip() or None


def maintenance_next_code():
    return f"MAN-{Maintenance.query.count() + 1:04d}"


def occurrence_next_code():
    return f"OCO-{Occurrence.query.count() + 1:04d}"


def fill_log_entry(entry):
    entry.entry_date = parse_date(request.form.get("entry_date"), date.today())
    entry.entry_time = parse_time(request.form.get("entry_time")) or datetime.now().time().replace(microsecond=0)
    entry.category = request.form["category"]
    entry.responsible = request.form["responsible"]
    entry.title = request.form["title"]
    entry.description = request.form["description"]
    entry.location = normalize_text(request.form.get("location"))
    entry.evidence = normalize_text(request.form.get("evidence"))
    return entry


def fill_maintenance(item):
    item.code = request.form["code"]
    item.title = request.form["title"]
    item.category = request.form["category"]
    item.priority = request.form["priority"]
    item.status = request.form["status"]
    item.start_date = parse_date(request.form.get("start_date"), date.today())
    item.start_time = parse_time(request.form.get("start_time"))
    item.end_date = parse_date(request.form.get("end_date"))
    item.end_time = parse_time(request.form.get("end_time"))
    item.responsible = normalize_text(request.form.get("responsible"))
    item.provider = normalize_text(request.form.get("provider"))
    item.amount = parse_decimal(request.form.get("amount"))
    item.location = normalize_text(request.form.get("location"))
    item.description = request.form["description"]
    item.attachments = normalize_text(request.form.get("attachments"))
    return item


def fill_occurrence(item):
    occurred_date = parse_date(request.form.get("occurred_date"), date.today())
    occurred_time = parse_time(request.form.get("occurred_time")) or time(0, 0)
    item.code = request.form["code"]
    item.category = request.form["category"]
    item.occurred_at = datetime.combine(occurred_date, occurred_time)
    item.apartment = normalize_text(request.form.get("apartment"))
    item.block = normalize_text(request.form.get("block"))
    item.resident = normalize_text(request.form.get("resident"))
    item.description = request.form["description"]
    item.witnesses = normalize_text(request.form.get("witnesses"))
    item.affects_residents = request.form.get("affects_residents") == "on"
    item.requires_fine = request.form.get("requires_fine") == "on"
    item.status = request.form["status"]
    item.evidence = normalize_text(request.form.get("evidence"))
    return item


def fill_purchase(item):
    item.material = request.form["material"]
    item.quantity = request.form["quantity"]
    item.purpose = request.form["purpose"]
    item.urgency = request.form["urgency"]
    item.has_quote = request.form.get("has_quote") == "on"
    item.supplier = normalize_text(request.form.get("supplier"))
    item.amount = parse_decimal(request.form.get("amount"))
    item.status = request.form["status"]
    item.attachment = normalize_text(request.form.get("attachment"))
    return item


@main_bp.get("/")
def dashboard():
    today = date.today()
    stats = {
        "logs_today": LogEntry.query.filter_by(entry_date=today).count(),
        "open_occurrences": Occurrence.query.filter(Occurrence.status.in_(["Aberta", "Em analise"])).count(),
        "pending_maintenance": Maintenance.query.filter(Maintenance.status.in_(["Agendada", "Em execucao"])).count(),
        "pending_purchases": Purchase.query.filter(Purchase.status.notin_(["Concluida", "Cancelada"])).count(),
    }
    agenda = Maintenance.query.filter(Maintenance.start_date >= today).order_by(Maintenance.start_date, Maintenance.start_time).limit(6).all()
    latest_logs = LogEntry.query.order_by(LogEntry.entry_date.desc(), LogEntry.entry_time.desc()).limit(6).all()
    occurrences = Occurrence.query.order_by(Occurrence.occurred_at.desc()).limit(5).all()
    return render_template("dashboard.html", stats=stats, agenda=agenda, latest_logs=latest_logs, occurrences=occurrences)


@main_bp.route("/diario", methods=["GET", "POST"])
def diary():
    if request.method == "POST":
        entry = fill_log_entry(LogEntry())
        db.session.add(entry)
        db.session.commit()
        flash("Registro incluido no diario de bordo.", "success")
        return redirect(url_for("main.diary"))

    query = LogEntry.query
    search = normalize_text(request.args.get("q"))
    if search:
        if search.isdigit():
            query = query.filter(LogEntry.id == int(search))
        else:
            like = f"%{search}%"
            query = query.filter(LogEntry.title.ilike(like) | LogEntry.category.ilike(like) | LogEntry.responsible.ilike(like))
    entries = query.order_by(LogEntry.entry_date.desc(), LogEntry.entry_time.desc()).all()
    return render_template("diary.html", entries=entries, today=date.today(), entry=None, action_url=url_for("main.diary"), q=search or "")


@main_bp.route("/diario/<int:item_id>/editar", methods=["GET", "POST"])
def diary_edit(item_id):
    entry = LogEntry.query.get_or_404(item_id)
    if request.method == "POST":
        fill_log_entry(entry)
        db.session.commit()
        flash(f"Registro ID {entry.id} atualizado.", "success")
        return redirect(url_for("main.diary"))

    entries = LogEntry.query.order_by(LogEntry.entry_date.desc(), LogEntry.entry_time.desc()).all()
    return render_template("diary.html", entries=entries, today=date.today(), entry=entry, action_url=url_for("main.diary_edit", item_id=entry.id), q="")


@main_bp.post("/diario/<int:item_id>/excluir")
def diary_delete(item_id):
    entry = LogEntry.query.get_or_404(item_id)
    db.session.delete(entry)
    db.session.commit()
    flash(f"Registro ID {item_id} excluido.", "success")
    return redirect(url_for("main.diary"))


@main_bp.route("/manutencoes", methods=["GET", "POST"])
def maintenance():
    if request.method == "POST":
        item = fill_maintenance(Maintenance())
        db.session.add(item)
        db.session.commit()
        flash("Manutencao cadastrada.", "success")
        return redirect(url_for("main.maintenance"))

    query = Maintenance.query
    search = normalize_text(request.args.get("q"))
    if search:
        if search.isdigit():
            query = query.filter(Maintenance.id == int(search))
        else:
            like = f"%{search}%"
            query = query.filter(Maintenance.code.ilike(like) | Maintenance.title.ilike(like) | Maintenance.category.ilike(like) | Maintenance.status.ilike(like))
    items = query.order_by(Maintenance.start_date.desc()).all()
    return render_template("maintenance.html", items=items, today=date.today(), next_code=maintenance_next_code(), item=None, action_url=url_for("main.maintenance"), q=search or "")


@main_bp.route("/manutencoes/<int:item_id>/editar", methods=["GET", "POST"])
def maintenance_edit(item_id):
    item = Maintenance.query.get_or_404(item_id)
    if request.method == "POST":
        fill_maintenance(item)
        db.session.commit()
        flash(f"Manutencao ID {item.id} atualizada.", "success")
        return redirect(url_for("main.maintenance"))

    items = Maintenance.query.order_by(Maintenance.start_date.desc()).all()
    return render_template("maintenance.html", items=items, today=date.today(), next_code=item.code, item=item, action_url=url_for("main.maintenance_edit", item_id=item.id), q="")


@main_bp.post("/manutencoes/<int:item_id>/excluir")
def maintenance_delete(item_id):
    item = Maintenance.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"Manutencao ID {item_id} excluida.", "success")
    return redirect(url_for("main.maintenance"))


@main_bp.get("/agenda")
def agenda():
    items = Maintenance.query.order_by(Maintenance.start_date.asc(), Maintenance.start_time.asc()).all()
    return render_template("agenda.html", items=items)


@main_bp.route("/ocorrencias", methods=["GET", "POST"])
def occurrences():
    if request.method == "POST":
        item = fill_occurrence(Occurrence())
        db.session.add(item)
        db.session.commit()
        flash("Ocorrencia registrada.", "success")
        return redirect(url_for("main.occurrences"))

    query = Occurrence.query
    search = normalize_text(request.args.get("q"))
    if search:
        if search.isdigit():
            query = query.filter(Occurrence.id == int(search))
        else:
            like = f"%{search}%"
            query = query.filter(Occurrence.code.ilike(like) | Occurrence.category.ilike(like) | Occurrence.status.ilike(like) | Occurrence.description.ilike(like))
    items = query.order_by(Occurrence.occurred_at.desc()).all()
    return render_template("occurrences.html", items=items, today=date.today(), next_code=occurrence_next_code(), item=None, action_url=url_for("main.occurrences"), q=search or "")


@main_bp.route("/ocorrencias/<int:item_id>/editar", methods=["GET", "POST"])
def occurrence_edit(item_id):
    item = Occurrence.query.get_or_404(item_id)
    if request.method == "POST":
        fill_occurrence(item)
        db.session.commit()
        flash(f"Ocorrencia ID {item.id} atualizada.", "success")
        return redirect(url_for("main.occurrences"))

    items = Occurrence.query.order_by(Occurrence.occurred_at.desc()).all()
    return render_template("occurrences.html", items=items, today=date.today(), next_code=item.code, item=item, action_url=url_for("main.occurrence_edit", item_id=item.id), q="")


@main_bp.post("/ocorrencias/<int:item_id>/excluir")
def occurrence_delete(item_id):
    item = Occurrence.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"Ocorrencia ID {item_id} excluida.", "success")
    return redirect(url_for("main.occurrences"))


@main_bp.route("/compras", methods=["GET", "POST"])
def purchases():
    if request.method == "POST":
        item = fill_purchase(Purchase())
        db.session.add(item)
        db.session.commit()
        flash("Solicitacao de compra registrada.", "success")
        return redirect(url_for("main.purchases"))

    query = Purchase.query
    search = normalize_text(request.args.get("q"))
    if search:
        if search.isdigit():
            query = query.filter(Purchase.id == int(search))
        else:
            like = f"%{search}%"
            query = query.filter(Purchase.material.ilike(like) | Purchase.status.ilike(like) | Purchase.urgency.ilike(like))
    items = query.order_by(Purchase.created_at.desc()).all()
    return render_template("purchases.html", items=items, item=None, action_url=url_for("main.purchases"), q=search or "")


@main_bp.route("/compras/<int:item_id>/editar", methods=["GET", "POST"])
def purchase_edit(item_id):
    item = Purchase.query.get_or_404(item_id)
    if request.method == "POST":
        fill_purchase(item)
        db.session.commit()
        flash(f"Compra ID {item.id} atualizada.", "success")
        return redirect(url_for("main.purchases"))

    items = Purchase.query.order_by(Purchase.created_at.desc()).all()
    return render_template("purchases.html", items=items, item=item, action_url=url_for("main.purchase_edit", item_id=item.id), q="")


@main_bp.post("/compras/<int:item_id>/excluir")
def purchase_delete(item_id):
    item = Purchase.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"Compra ID {item_id} excluida.", "success")
    return redirect(url_for("main.purchases"))


@main_bp.get("/evidencias")
def evidence():
    records = []
    for entry in LogEntry.query.filter(LogEntry.evidence.isnot(None)).all():
        records.append(("Diario", entry.id, entry.entry_date, entry.title, entry.evidence))
    for item in Maintenance.query.filter(Maintenance.attachments.isnot(None)).all():
        records.append(("Manutencao", item.id, item.start_date, item.title, item.attachments))
    for item in Occurrence.query.filter(Occurrence.evidence.isnot(None)).all():
        records.append(("Ocorrencia", item.id, item.occurred_at.date(), item.code, item.evidence))
    for item in Purchase.query.filter(Purchase.attachment.isnot(None)).all():
        records.append(("Compra", item.id, item.created_at.date(), item.material, item.attachment))
    records.sort(key=lambda row: row[2], reverse=True)
    return render_template("evidence.html", records=records)


@main_bp.route("/relatorios", methods=["GET", "POST"])
def reports():
    end = date.today()
    start = end - timedelta(days=14)
    if request.method == "POST":
        start = parse_date(request.form.get("start_date"), start)
        end = parse_date(request.form.get("end_date"), end)

    start_dt = datetime.combine(start, time.min)
    end_dt = datetime.combine(end, time.max)
    data = {
        "logs": LogEntry.query.filter(LogEntry.entry_date.between(start, end)).order_by(LogEntry.entry_date).all(),
        "maintenance": Maintenance.query.filter(Maintenance.start_date.between(start, end)).order_by(Maintenance.start_date).all(),
        "occurrences": Occurrence.query.filter(Occurrence.occurred_at.between(start_dt, end_dt)).order_by(Occurrence.occurred_at).all(),
        "purchases": Purchase.query.filter(Purchase.created_at.between(start_dt, end_dt)).order_by(Purchase.created_at).all(),
    }
    totals = {key: len(value) for key, value in data.items()}
    return render_template("reports.html", start=start, end=end, data=data, totals=totals)
