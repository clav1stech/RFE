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


# Couvre l'ensemble des Business Terms effectivement produits par cii.py/ubl.py
# (cf. docs/CODEMAP.md : cette table est un artefact de documentation, elle ne
# pilote pas la sérialisation — toute nouvelle balise ajoutée aux sérialiseurs
# doit être répercutée ici pour éviter la dérive).
BT_MAPPINGS: list[BTMapping] = [
    # --- En-tête document ---
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
        "BT-9",
        "Date d'échéance de paiement",
        "…/SpecifiedTradePaymentTerms/DueDateDateTime",
        "cbc:DueDate",
    ),
    BTMapping(
        "BT-10",
        "Référence acheteur",
        "…/BuyerReference",
        "cbc:BuyerReference",
    ),
    BTMapping(
        "BT-22",
        "Note libre sur la facture",
        "ExchangedDocument/IncludedNote/Content",
        "cbc:Note",
    ),
    # --- Vendeur (BG-4) ---
    BTMapping(
        "BT-27",
        "Nom du vendeur",
        "…/SellerTradeParty/Name",
        "cac:AccountingSupplierParty/…/cbc:RegistrationName",
    ),
    BTMapping(
        "BT-30",
        "Identifiant légal du vendeur (SIREN/SIRET)",
        "…/SellerTradeParty/SpecifiedLegalOrganization/ID",
        "cac:AccountingSupplierParty/…/cac:PartyLegalEntity/cbc:CompanyID",
    ),
    BTMapping(
        "BT-31",
        "N° TVA du vendeur",
        "…/SellerTradeParty/SpecifiedTaxRegistration/ID",
        "cac:AccountingSupplierParty/…/cac:PartyTaxScheme/cbc:CompanyID",
    ),
    BTMapping(
        "BT-35",
        "Ligne d'adresse du vendeur",
        "…/SellerTradeParty/PostalTradeAddress/LineOne",
        "cac:AccountingSupplierParty/…/cac:PostalAddress/cbc:StreetName",
    ),
    BTMapping(
        "BT-37",
        "Ville du vendeur",
        "…/SellerTradeParty/PostalTradeAddress/CityName",
        "cac:AccountingSupplierParty/…/cac:PostalAddress/cbc:CityName",
    ),
    BTMapping(
        "BT-38",
        "Code postal du vendeur",
        "…/SellerTradeParty/PostalTradeAddress/PostcodeCode",
        "cac:AccountingSupplierParty/…/cac:PostalAddress/cbc:PostalZone",
    ),
    BTMapping(
        "BT-40",
        "Code pays du vendeur",
        "…/SellerTradeParty/PostalTradeAddress/CountryID",
        "cac:AccountingSupplierParty/…/cac:Country/cbc:IdentificationCode",
    ),
    # --- Acheteur (BG-7) ---
    BTMapping(
        "BT-44",
        "Nom de l'acheteur",
        "…/BuyerTradeParty/Name",
        "cac:AccountingCustomerParty/…/cbc:RegistrationName",
    ),
    BTMapping(
        "BT-47",
        "Identifiant légal de l'acheteur (SIREN/SIRET)",
        "…/BuyerTradeParty/SpecifiedLegalOrganization/ID",
        "cac:AccountingCustomerParty/…/cac:PartyLegalEntity/cbc:CompanyID",
    ),
    BTMapping(
        "BT-48",
        "N° TVA de l'acheteur",
        "…/BuyerTradeParty/SpecifiedTaxRegistration/ID",
        "cac:AccountingCustomerParty/…/cac:PartyTaxScheme/cbc:CompanyID",
    ),
    BTMapping(
        "BT-50",
        "Ligne d'adresse de l'acheteur",
        "…/BuyerTradeParty/PostalTradeAddress/LineOne",
        "cac:AccountingCustomerParty/…/cac:PostalAddress/cbc:StreetName",
    ),
    BTMapping(
        "BT-52",
        "Ville de l'acheteur",
        "…/BuyerTradeParty/PostalTradeAddress/CityName",
        "cac:AccountingCustomerParty/…/cac:PostalAddress/cbc:CityName",
    ),
    BTMapping(
        "BT-53",
        "Code postal de l'acheteur",
        "…/BuyerTradeParty/PostalTradeAddress/PostcodeCode",
        "cac:AccountingCustomerParty/…/cac:PostalAddress/cbc:PostalZone",
    ),
    BTMapping(
        "BT-55",
        "Code pays de l'acheteur",
        "…/BuyerTradeParty/PostalTradeAddress/CountryID",
        "cac:AccountingCustomerParty/…/cac:Country/cbc:IdentificationCode",
    ),
    # --- Ventilation de la TVA (BG-23) ---
    BTMapping(
        "BT-116",
        "Base imposable TVA (par taux)",
        "…/ApplicableTradeTax/BasisAmount",
        "cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount",
    ),
    BTMapping(
        "BT-117",
        "Montant de TVA (par taux)",
        "…/ApplicableTradeTax/CalculatedAmount",
        "cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount",
    ),
    BTMapping(
        "BT-118",
        "Code catégorie de TVA (ventilation)",
        "…/ApplicableTradeTax/CategoryCode",
        "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:ID",
    ),
    BTMapping(
        "BT-119",
        "Taux de TVA (ventilation)",
        "…/ApplicableTradeTax/RateApplicablePercent",
        "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent",
    ),
    # --- Totaux (BG-22) ---
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
    # --- Ligne de facture (BG-25) ---
    BTMapping(
        "BT-126",
        "Identifiant de la ligne de facture",
        "…/AssociatedDocumentLineDocument/LineID",
        "cac:InvoiceLine/cbc:ID",
    ),
    BTMapping(
        "BT-129",
        "Quantité facturée",
        "…/SpecifiedLineTradeDelivery/BilledQuantity",
        "cac:InvoiceLine/cbc:InvoicedQuantity",
    ),
    BTMapping(
        "BT-130",
        "Code unité de mesure",
        "…/BilledQuantity/@unitCode",
        "cac:InvoiceLine/cbc:InvoicedQuantity/@unitCode",
    ),
    BTMapping(
        "BT-131",
        "Montant net de la ligne",
        "…/SpecifiedTradeSettlementLineMonetarySummation/LineTotalAmount",
        "cac:InvoiceLine/cbc:LineExtensionAmount",
    ),
    BTMapping(
        "BT-146",
        "Prix unitaire net",
        "…/NetPriceProductTradePrice/ChargeAmount",
        "cac:InvoiceLine/cac:Price/cbc:PriceAmount",
    ),
    BTMapping(
        "BT-151",
        "Code catégorie de TVA de la ligne",
        "…/SpecifiedLineTradeSettlement/ApplicableTradeTax/CategoryCode",
        "cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory/cbc:ID",
    ),
    BTMapping(
        "BT-152",
        "Taux de TVA de la ligne",
        "…/ApplicableTradeTax/RateApplicablePercent",
        "cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory/cbc:Percent",
    ),
    BTMapping(
        "BT-153",
        "Nom de l'article facturé",
        "…/SpecifiedTradeProduct/Name",
        "cac:InvoiceLine/cac:Item/cbc:Name",
    ),
    BTMapping(
        "BT-154",
        "Description de l'article facturé",
        "…/SpecifiedTradeProduct/Description",
        "cac:InvoiceLine/cac:Item/cbc:Description",
    ),
]
