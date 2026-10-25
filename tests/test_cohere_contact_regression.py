from types import SimpleNamespace

from rdap.normalize.base import Handler
from rdap.schema.normalized import Contact


def test_shared_phone_does_not_merge_distinct_email_contacts():
    class ContactHandler(Handler):
        def contacts_from_entity(self, entity, deep=True):
            return [entity.contact]

    phone = "+1 415 555 0100"
    entities = [
        SimpleNamespace(contact=Contact(name="Example Operator", phone=phone,
                                        email="first@example.org", roles=["technical"])),
        SimpleNamespace(contact=Contact(name="Example Operator", phone=phone,
                                        email="second@example.org", roles=["administrative"])),
    ]
    contacts = ContactHandler().contacts(SimpleNamespace(entities=entities))

    assert {contact.email for contact in contacts} == {
        "first@example.org", "second@example.org"
    }
    assert len(contacts) == 2
