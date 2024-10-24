from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, db, Offer, Ticket
from app.forms import OfferForm, UserEditForm, OfferEditForm  # Assurez-vous d'avoir un formulaire pour les offres


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            flash('Accès interdit : administrateur uniquement.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'is_staff') or not current_user.is_staff:
            flash('Accès interdit : administrateur uniquement.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/staff')
@login_required
@staff_required
def staff():
    return render_template('admin/staff.html')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    sales_data = Ticket.query.all()
    return render_template('admin/dashboard.html', sales_data=sales_data)

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def manage_users():
    # Code pour récupérer et afficher les utilisateurs
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.email = form.email.data
        user.is_staff = form.is_staff.data
        db.session.commit()
        flash('Utilisateur mis à jour avec succès.', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Impossible de supprimer un administrateur.', 'danger')
        return redirect(url_for('admin.manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès.', 'success')
    return redirect(url_for('admin.manage_users'))



@admin_bp.route('admin/manage_offers')
@login_required
@admin_required
def manage_offers():
    offers = Offer.query.all()
    return render_template('admin/manage_offers.html', offers=offers)

@admin_bp.route('/admin/create_offer', methods=['GET', 'POST'])
@login_required
@admin_required
def create_offer():
    form = OfferForm()
    if form.validate_on_submit():
        # # Vérifier que l'ID du type d'offre existe dans la table offer_type
        # offer_type_id = int(form.offer_type.data)
        # offer_type = OfferType.query.get(offer_type_id)
        
        # if not offer_type:
        #     flash('Type d\'offre invalide.', 'danger')
        #     return redirect(url_for('admin.create_offer'))
        
        offer = Offer(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            # type_id=offer_type_id,  # Utilisation correcte de l'ID du type d'offre
            stock=form.stock.data,
            stripe_price_id=form.stripe_price_id.data,
        )
        db.session.add(offer)
        db.session.commit()
        flash('Offre cree avec succes!', 'success')
        return redirect(url_for('admin.manage_offers'))
    return render_template('admin/create_offer.html', form=form)


@admin_bp.route('/edit_offer/<int:offer_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    form = OfferEditForm(obj=offer)
    if form.validate_on_submit():
        offer.name = form.name.data
        offer.description = form.description.data
        offer.price = form.price.data
        offer.stock = form.stock.data
        offer.stripe_price_id = form.stripe_price_id.data
        db.session.commit()
        flash('Offre mise a jour avec succès!', 'success')
        return redirect(url_for('admin.manage_offers'))
    return render_template('admin/edit_offer.html', form=form, offer=offer)

@admin_bp.route('/offers/edit/<int:offer_id>', methods=['GET', 'POST'])
def update_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    form = OfferEditForm(obj=offer)

    if form.validate_on_submit():
        offer.name = form.name.data
        offer.description = form.description.data
        offer.price = form.price.data
        # offer.type = form.type.data  # Assurez-vous que le champ type existe dans le formulaire
        offer.stock = form.stock.data
        offer.stripe_price_id = form.stripe_price_id.data
        
        db.session.commit()
        return redirect(url_for('admin.manage_offers'))  # Redirige vers la liste des offres

    return render_template('admin/edit_offer.html', form=form, offer=offer)


@admin_bp.route('/delete_offer/<int:offer_id>', methods=['POST'])
@login_required
@admin_required
def delete_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    flash('Offre supprimée avec succès!', 'success')
    return redirect(url_for('admin.manage_offers'))
