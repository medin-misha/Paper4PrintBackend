from . import views

urlpatterns = {
    "auth.register": views.AuthRegister,
    "payment.init": views.PaymentInitial,
    "payment.status": views.PaymentStatus,
}
