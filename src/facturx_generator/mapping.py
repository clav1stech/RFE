"""Table de correspondance des Business Terms EN16931 vers CII et UBL.

Cette table sert de documentation vivante et est réutilisée par l'UI Streamlit
pour afficher, pour chaque BT, son emplacement dans les deux syntaxes XML.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BTMapping:
    """Correspondance d'un Business Term vers les deux syntaxes normées."""

    bt: str  # identifiant EN16931, ex. "BT-1"
    label: str  # libellé métier
    cii_path: str  # chemin XPath simplifié dans la syntaxe CII (Factur-X)
    ubl_path: str  # chemin XPath simplifié dans la syntaxe UBL


# Sous-ensemble représentatif du profil EN16931 (Factur-X / Chorus Pro).
BT_MAPPINGS: list[BTMapping] = [
    BTMapping(
        "BT-1",
        "Numéro de facture",
        "ExchangedDocument/ID",
        "cbc:ID",
    ),
    BTMapping(
        "BT-2",
        "Date d'émission",
        "ExchangedDocument/IssueDateTime",
        "cbc:IssueDate",
    ),
    BTMapping(
        "BT-3",
        "Code type de facture",
        "ExchangedDocument/TypeCode",
        "cbc:InvoiceTypeCode",
    ),
    BTMapping(
        "BT-5",
        "Code devise de la facture",
        "…/InvoiceCurrencyCode",
        "cbc:DocumentCurrencyCode",
    ),
    BTMapping(
        "BT-10",
        "Référence acheteur",
        "…/BuyerReference",
        "cbc:BuyerReference",
    ),
    BTMapping(
        "BT-27",
        "Nom du vendeur",
        "…/SellerTradeParty/Name",
        "cac:AccountingSupplierParty/…/cbc:RegistrationName",
    ),
    BTMapping(
        "BT-31",
        "N° TVA du vendeur",
        "…/SellerTradeParty/SpecifiedTaxRegistration/ID",
        "cac:AccountingSupplierParty/…/cac:PartyTaxScheme/cbc:CompanyID",
    ),
    BTMapping(
        "BT-44",
        "Nom de l'acheteur",
        "…/BuyerTradeParty/Name",
        "cac:AccountingCustomerParty/…/cbc:RegistrationName",
    ),
    BTMapping(
        "BT-106",
        "Somme des montants nets de lignes",
        "…/LineTotalAmount",
        "cac:LegalMonetaryTotal/cbc:LineExtensionAmount",
    ),
    BTMapping(
        "BT-109",
        "Total hors taxes",
        "…/TaxBasisTotalAmount",
        "cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount",
    ),
    BTMapping(
        "BT-110",
        "Montant total de TVA",
        "…/TaxTotalAmount",
        "cac:TaxTotal/cbc:TaxAmount",
    ),
    BTMapping(
        "BT-112",
        "Total toutes taxes comprises",
        "…/GrandTotalAmount",
        "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount",
    ),
    BTMapping(
        "BT-115",
        "Net à payer",
        "…/DuePayableAmount",
        "cac:LegalMonetaryTotal/cbc:PayableAmount",
    ),
]
