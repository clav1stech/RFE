"""Interface Streamlit — génération de factures de test Factur-X / UBL.

Cette couche UI ne contient AUCUNE logique métier : elle se contente d'appeler
le package `facturx_generator`. La séparation permet de tester la génération
sans Streamlit et de réutiliser le moteur ailleurs (CLI, API, batch).
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import streamlit as st

# Community Cloud exécute app.py à la racine : on expose `src/` au PYTHONPATH.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from facturx_generator import __version__  # noqa: E402
from facturx_generator.generator import Format, generate  # noqa: E402
from facturx_generator.mapping import BT_MAPPINGS  # noqa: E402
from facturx_generator.models import Invoice, InvoiceLine, Party  # noqa: E402
from facturx_generator.profiles import PROFILES, get_profile  # noqa: E402

st.set_page_config(page_title="Générateur Factur-X / UBL", page_icon="🧾", layout="wide")

st.title("🧾 Générateur de factures de test Factur-X / UBL")
st.caption(
    f"Mapping des Business Terms EN16931 · v{__version__} · logique métier découplée de l'UI"
)

with st.sidebar:
    st.header("Paramètres")
    source = st.radio(
        "Source de la facture",
        ["Profil prédéfini", "Saisie manuelle"],
        help="Charger un profil de test ou saisir une facture simple à la main.",
    )
    fmt_label = st.selectbox("Format de sortie", ["CII (Factur-X)", "UBL 2.1"])
    fmt = Format.CII if fmt_label.startswith("CII") else Format.UBL


def _build_manual() -> Invoice:
    st.subheader("Saisie manuelle")
    col_a, col_b = st.columns(2)
    with col_a:
        number = st.text_input("N° de facture (BT-1)", "FA-2026-0100")
        issue = st.date_input("Date d'émission (BT-2)", date(2026, 1, 1))
        currency = st.text_input("Devise (BT-5)", "EUR")
    with col_b:
        seller_name = st.text_input("Nom vendeur (BT-27)", "Ma Société SAS")
        buyer_name = st.text_input("Nom acheteur (BT-44)", "Grenoble-Alpes Métropole")
        buyer_ref = st.text_input("Référence acheteur (BT-10)", "SERVICE-ACHATS")

    st.markdown("**Ligne de facture (BG-25)**")
    lc1, lc2, lc3, lc4 = st.columns(4)
    with lc1:
        item = st.text_input("Article (BT-153)", "Prestation")
    with lc2:
        qty = st.number_input("Quantité (BT-129)", min_value=0.0, value=1.0, step=1.0)
    with lc3:
        price = st.number_input("Prix unitaire (BT-146)", min_value=0.0, value=100.0)
    with lc4:
        vat = st.number_input("Taux TVA % (BT-152)", min_value=0.0, value=20.0)

    return Invoice(
        invoice_number=number,
        issue_date=issue,
        invoice_type_code="380",
        currency=currency,
        buyer_reference=buyer_ref,
        seller=Party(name=seller_name, country_code="FR"),
        buyer=Party(name=buyer_name, country_code="FR"),
        lines=[
            InvoiceLine(
                line_id="1",
                name=item,
                quantity=Decimal(str(qty)),
                unit_code="C62",
                unit_price=Decimal(str(price)),
                vat_rate=Decimal(str(vat)),
            )
        ],
    )


if source == "Profil prédéfini":
    profile_name = st.sidebar.selectbox("Profil", sorted(PROFILES))
    invoice = get_profile(profile_name)
    st.subheader(f"Profil : `{profile_name}`")
else:
    invoice = _build_manual()

# --- Récapitulatif des totaux ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total HT (BT-109)", f"{invoice.tax_basis_total} {invoice.currency}")
m2.metric("Total TVA (BT-110)", f"{invoice.tax_total} {invoice.currency}")
m3.metric("Total TTC (BT-112)", f"{invoice.grand_total} {invoice.currency}")
m4.metric("Net à payer (BT-115)", f"{invoice.due_payable} {invoice.currency}")

# --- Génération XML ---
xml_bytes = generate(invoice, fmt)
xml_text = xml_bytes.decode("utf-8")

tab_xml, tab_mapping = st.tabs(["XML généré", "Mapping BT ↔ CII/UBL"])

with tab_xml:
    ext = "cii" if fmt is Format.CII else "ubl"
    st.download_button(
        "⬇️ Télécharger le XML",
        data=xml_bytes,
        file_name=f"{invoice.invoice_number}_{ext}.xml",
        mime="application/xml",
    )
    st.code(xml_text, language="xml")

with tab_mapping:
    st.markdown(
        "Correspondance d'un sous-ensemble représentatif des Business Terms "
        "EN16931 entre les deux syntaxes normées."
    )
    st.dataframe(
        [
            {
                "BT": m.bt,
                "Libellé": m.label,
                "CII (Factur-X)": m.cii_path,
                "UBL": m.ubl_path,
            }
            for m in BT_MAPPINGS
        ],
        use_container_width=True,
        hide_index=True,
    )
