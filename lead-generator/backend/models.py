"""Data model for a single extracted lead."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Lead:
    business_name: str = ""
    contact_name: str = ""
    role: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    website: str = ""
    linkedin: str = ""
    twitter: str = ""
    facebook: str = ""
    instagram: str = ""
    source_page: str = ""

    def key(self) -> tuple:
        """Identity used to de-duplicate leads seen across multiple pages."""
        return (
            self.email.lower().strip(),
            self.phone.strip(),
            self.contact_name.lower().strip(),
        )
