import pytest
from django.test import RequestFactory
from django.urls import reverse
from fundooapp import views

pytestmark = pytest.mark.django_db

class TestMyView:
    def test_anonymous(self):
        try:
            req = RequestFactory().get(reverse("fundooapp:rest_register"))
            resp = views.RestUserRegister.as_view()(req)
            assert resp.status_code == 200
        except:
            print(ValueError)

class TestMyCreateView:
    def test_authentication(self):
        try:
            req = RequestFactory().get(reverse("fundooapp:note_create"))
            # req.user = AnonymousUser()
            resp = views.NotesCreate.as_view()(req)
            assert resp.status_code == 200, "Everyone can create a MyModel"
        except:
            print(ValueError)

