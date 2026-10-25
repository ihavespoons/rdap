from types import SimpleNamespace

from rdap.normalize.base import Handler
from rdap.schema.rdap import Entity


def _entity_with_contact(name, email):
    return Entity(
        objectClassName="entity",
        vcardArray=[
            "vcard",
            [
                ["fn", {}, "text", name],
                ["email", {}, "text", email],
            ],
        ],
    )


def test_contacts_keeps_distinct_contacts_with_shared_name():
    # Two entities share a display name but have distinct email addresses;
    # both must remain in the normalized contacts list.
    parent = SimpleNamespace(
        entities=[
            _entity_with_contact("Shared Name", "alpha@example.test"),
            _entity_with_contact("Shared Name", "beta@example.test"),
        ]
    )

    contacts = Handler().contacts(parent)
    emails = sorted(contact.email for contact in contacts)

    assert emails == ["alpha@example.test", "beta@example.test"]
