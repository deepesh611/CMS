"""Room, facility, and booking management routes."""
from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.facility import (
    BuildingForm,
    ExternalChurchForm,
    RoomBookingForm,
    RoomForm,
)
from app.models.facility import Building, ExternalChurch, Room, RoomBooking
from app.utils.decorators import require_permission

facility_bp = Blueprint("facility", __name__, url_prefix="/facility")


# ─── Buildings ────────────────────────────────────────────────────────

@facility_bp.route("/buildings")
@login_required
@require_permission("facility", "view")
def buildings():
    """List all buildings."""
    items = Building.query.order_by(Building.name).all()
    return render_template("facility/buildings.html", buildings=items)


@facility_bp.route("/buildings/add", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def add_building():
    form = BuildingForm()
    if form.validate_on_submit():
        bld = Building()
        form.populate_obj(bld)
        db.session.add(bld)
        db.session.commit()
        flash("Building added.", "success")
        return redirect(url_for("facility.buildings"))
    return render_template("facility/building_form.html", form=form, editing=False)


@facility_bp.route("/buildings/edit/<int:bld_id>", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def edit_building(bld_id):
    bld = db.session.get(Building, bld_id) or abort(404)
    form = BuildingForm(obj=bld)
    if form.validate_on_submit():
        form.populate_obj(bld)
        db.session.commit()
        flash("Building updated.", "success")
        return redirect(url_for("facility.buildings"))
    return render_template("facility/building_form.html", form=form, editing=True)


# ─── Rooms ────────────────────────────────────────────────────────────

@facility_bp.route("/rooms")
@login_required
@require_permission("facility", "view")
def rooms():
    """List all rooms."""
    items = Room.query.order_by(Room.name).all()
    return render_template("facility/rooms.html", rooms=items)


def _populate_room_choices(form):
    form.building_id.choices = [
        (b.id, b.name) for b in Building.query.order_by(Building.name).all()
    ]


@facility_bp.route("/rooms/add", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def add_room():
    form = RoomForm()
    _populate_room_choices(form)
    if form.validate_on_submit():
        room = Room()
        form.populate_obj(room)
        db.session.add(room)
        db.session.commit()
        flash("Room added.", "success")
        return redirect(url_for("facility.rooms"))
    return render_template("facility/room_form.html", form=form, editing=False)


@facility_bp.route("/rooms/edit/<int:room_id>", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def edit_room(room_id):
    room = db.session.get(Room, room_id) or abort(404)
    form = RoomForm(obj=room)
    _populate_room_choices(form)
    if form.validate_on_submit():
        form.populate_obj(room)
        db.session.commit()
        flash("Room updated.", "success")
        return redirect(url_for("facility.rooms"))
    return render_template("facility/room_form.html", form=form, editing=True)


# ─── External Churches ───────────────────────────────────────────────

@facility_bp.route("/churches")
@login_required
@require_permission("facility", "view")
def churches():
    """List partner churches."""
    items = ExternalChurch.query.order_by(ExternalChurch.name).all()
    return render_template("facility/churches.html", churches=items)


@facility_bp.route("/churches/add", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def add_church():
    form = ExternalChurchForm()
    if form.validate_on_submit():
        ch = ExternalChurch()
        form.populate_obj(ch)
        db.session.add(ch)
        db.session.commit()
        flash("Partner church added.", "success")
        return redirect(url_for("facility.churches"))
    return render_template("facility/church_form.html", form=form, editing=False)


@facility_bp.route("/churches/edit/<int:ch_id>", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def edit_church(ch_id):
    ch = db.session.get(ExternalChurch, ch_id) or abort(404)
    form = ExternalChurchForm(obj=ch)
    if form.validate_on_submit():
        form.populate_obj(ch)
        db.session.commit()
        flash("Partner church updated.", "success")
        return redirect(url_for("facility.churches"))
    return render_template("facility/church_form.html", form=form, editing=True)


# ─── Bookings ─────────────────────────────────────────────────────────

def _populate_booking_choices(form):
    form.room_id.choices = [
        (r.id, f"{r.name} ({r.building.name})")
        for r in Room.query.join(Building).order_by(Room.name).all()
    ]
    form.requesting_church_id.choices = [(0, "— Internal —")] + [
        (c.id, c.name) for c in ExternalChurch.query.order_by(ExternalChurch.name).all()
    ]


@facility_bp.route("/bookings")
@login_required
@require_permission("facility", "view")
def bookings():
    """List all bookings."""
    items = RoomBooking.query.order_by(RoomBooking.start_date.desc()).all()
    return render_template("facility/bookings.html", bookings=items)


@facility_bp.route("/bookings/add", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def add_booking():
    form = RoomBookingForm()
    _populate_booking_choices(form)
    if form.validate_on_submit():
        # Check for conflicts
        conflicts = RoomBooking.check_conflict(
            form.room_id.data,
            form.start_date.data,
            form.end_date.data,
            form.start_time.data,
            form.end_time.data,
        )
        if conflicts:
            flash(
                f"Conflict detected: {len(conflicts)} overlapping booking(s) exist for this room and time.",
                "danger",
            )
            return render_template("facility/booking_form.html", form=form, editing=False)

        booking = RoomBooking()
        form.populate_obj(booking)
        booking.booking_number = RoomBooking.generate_booking_number()
        if booking.requesting_church_id == 0:
            booking.requesting_church_id = None

        # Auto-calculate final charge
        rental = booking.rental_amount or Decimal("0")
        deposit = booking.security_deposit or Decimal("0")
        discount = booking.discount or Decimal("0")
        taxes = booking.taxes or Decimal("0")
        booking.final_charge = rental + deposit - discount + taxes

        db.session.add(booking)
        db.session.commit()
        flash(f"Booking {booking.booking_number} confirmed.", "success")
        return redirect(url_for("facility.bookings"))
    return render_template("facility/booking_form.html", form=form, editing=False)


@facility_bp.route("/bookings/edit/<int:booking_id>", methods=["GET", "POST"])
@login_required
@require_permission("facility", "edit")
def edit_booking(booking_id):
    booking = db.session.get(RoomBooking, booking_id) or abort(404)
    form = RoomBookingForm(obj=booking)
    _populate_booking_choices(form)
    if form.validate_on_submit():
        # Check for conflicts excluding self
        conflicts = RoomBooking.check_conflict(
            form.room_id.data,
            form.start_date.data,
            form.end_date.data,
            form.start_time.data,
            form.end_time.data,
            exclude_id=booking_id,
        )
        if conflicts:
            flash(
                f"Conflict detected: {len(conflicts)} overlapping booking(s).",
                "danger",
            )
            return render_template("facility/booking_form.html", form=form, editing=True)

        form.populate_obj(booking)
        if booking.requesting_church_id == 0:
            booking.requesting_church_id = None

        rental = booking.rental_amount or Decimal("0")
        deposit = booking.security_deposit or Decimal("0")
        discount = booking.discount or Decimal("0")
        taxes = booking.taxes or Decimal("0")
        booking.final_charge = rental + deposit - discount + taxes

        db.session.commit()
        flash("Booking updated.", "success")
        return redirect(url_for("facility.bookings"))
    return render_template("facility/booking_form.html", form=form, editing=True)


@facility_bp.route("/bookings/cancel/<int:booking_id>", methods=["POST"])
@login_required
@require_permission("facility", "edit")
def cancel_booking(booking_id):
    booking = db.session.get(RoomBooking, booking_id) or abort(404)
    booking.booking_status = "Cancelled"
    db.session.commit()
    flash(f"Booking {booking.booking_number} cancelled.", "warning")
    return redirect(url_for("facility.bookings"))


# ─── Calendar View ───────────────────────────────────────────────────

@facility_bp.route("/calendar")
@login_required
@require_permission("facility", "view")
def calendar():
    """Calendar view of room bookings."""
    bookings_list = (
        RoomBooking.query.filter(RoomBooking.booking_status != "Cancelled")
        .order_by(RoomBooking.start_date)
        .all()
    )
    # Prepare JSON-serializable events for the calendar
    events = []
    for b in bookings_list:
        events.append(
            {
                "id": b.id,
                "title": f"{b.event_name} ({b.room.name})",
                "start": f"{b.start_date.isoformat()}T{b.start_time.isoformat()}",
                "end": f"{b.end_date.isoformat()}T{b.end_time.isoformat()}",
                "room": b.room.name,
                "status": b.booking_status,
            }
        )
    return render_template("facility/calendar.html", events=events)


# ─── Utilization Dashboard ───────────────────────────────────────────

@facility_bp.route("/utilization")
@login_required
@require_permission("facility", "view")
def utilization():
    """Facility utilization dashboard."""
    rooms_list = Room.query.all()
    total_rooms = len(rooms_list)
    total_bookings = RoomBooking.query.filter(
        RoomBooking.booking_status != "Cancelled"
    ).count()

    # Per-room booking counts
    room_stats = []
    for room in rooms_list:
        active = sum(
            1 for b in room.bookings if b.booking_status != "Cancelled"
        )
        room_stats.append({"room": room, "active_bookings": active})

    # Revenue totals
    from sqlalchemy import func

    revenue = (
        db.session.query(func.sum(RoomBooking.final_charge))
        .filter(RoomBooking.payment_status == "Paid")
        .scalar()
    ) or 0
    outstanding = (
        db.session.query(func.sum(RoomBooking.final_charge))
        .filter(RoomBooking.payment_status.in_(["Pending", "Partial"]))
        .scalar()
    ) or 0

    return render_template(
        "facility/utilization.html",
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        room_stats=room_stats,
        revenue=revenue,
        outstanding=outstanding,
    )
