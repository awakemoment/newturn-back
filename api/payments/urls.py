"""
Stripe 결제 URL
"""
from django.urls import path
from . import views


urlpatterns = [
    path('create-checkout/', views.create_checkout_session, name='create-checkout'),
    path('create-portal/', views.create_portal_session, name='create-portal'),
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
]

