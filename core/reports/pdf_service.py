"""
========================================================
PHOENIX VISION AI ENTERPRISE

Official PDF Report Service

Phoenix Security Technologies
========================================================
"""

from io import BytesIO
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
    TA_RIGHT
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)


class ReportPdfService:

    COMPANY = (
        "Phoenix Security Technologies"
    )

    PRODUCT = (
        "Phoenix Vision AI"
    )


    def __init__(
        self,
        logo_path=
            "web/static/images/logoS.png"
    ):

        self.logo_path = Path(
            logo_path
        )

        self.styles = (
            getSampleStyleSheet()
        )

        self._create_styles()


    def _create_styles(
        self
    ):

        self.title_style = ParagraphStyle(

            "PhoenixTitle",

            parent=
                self.styles[
                    "Heading1"
                ],

            fontName=
                "Helvetica-Bold",

            fontSize=
                15,

            leading=
                18,

            textColor=
                colors.HexColor(
                    "#173744"
                ),

            spaceAfter=
                2,

        )


        self.subtitle_style = ParagraphStyle(

            "PhoenixSubtitle",

            parent=
                self.styles[
                    "Normal"
                ],

            fontName=
                "Helvetica",

            fontSize=
                7,

            leading=
                9,

            textColor=
                colors.HexColor(
                    "#667B85"
                ),

        )


        self.section_style = ParagraphStyle(

            "PhoenixSection",

            parent=
                self.styles[
                    "Heading2"
                ],

            fontName=
                "Helvetica-Bold",

            fontSize=
                10,

            leading=
                13,

            textColor=
                colors.HexColor(
                    "#183847"
                ),

            spaceBefore=
                11,

            spaceAfter=
                6,

        )


        self.body_style = ParagraphStyle(

            "PhoenixBody",

            parent=
                self.styles[
                    "Normal"
                ],

            fontName=
                "Helvetica",

            fontSize=
                7.2,

            leading=
                9,

            textColor=
                colors.HexColor(
                    "#263D48"
                ),

        )


        self.small_style = ParagraphStyle(

            "PhoenixSmall",

            parent=
                self.body_style,

            fontSize=
                6.5,

            leading=
                8,

        )


        self.label_style = ParagraphStyle(

            "PhoenixLabel",

            parent=
                self.small_style,

            fontName=
                "Helvetica-Bold",

            textColor=
                colors.HexColor(
                    "#607680"
                ),

        )


        self.center_style = ParagraphStyle(

            "PhoenixCenter",

            parent=
                self.body_style,

            alignment=
                TA_CENTER,

        )


        self.right_style = ParagraphStyle(

            "PhoenixRight",

            parent=
                self.body_style,

            alignment=
                TA_RIGHT,

        )


    @staticmethod
    def _value(
        value,
        fallback="—"
    ):

        if (
            value is None
            or
            str(
                value
            ).strip() == ""
        ):

            return fallback


        return str(
            value
        )


    @staticmethod
    def _format_datetime(
        value
    ):

        if value is None:

            return "—"


        text = str(
            value
        ).strip()


        if not text:

            return "—"


        try:

            parsed = datetime.fromisoformat(
                text
            )

            return parsed.strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        except (
            TypeError,
            ValueError
        ):

            return text


    @staticmethod
    def _vehicle_type(
        value
    ):

        mapping = {

            "PERSON":
                "PERSONNE",

            "CAR":
                "VOITURE",

            "MOTORCYCLE":
                "MOTO",

            "MOTORBIKE":
                "MOTO",

            "BUS":
                "BUS",

            "TRUCK":
                "CAMION",

            "BICYCLE":
                "VÉLO",

        }


        key = str(
            value
            or ""
        ).strip().upper()


        return mapping.get(
            key,
            key
            or
            "—"
        )


    @staticmethod
    def _threat_label(
        value
    ):

        mapping = {

            "LOW":
                "FAIBLE",

            "MEDIUM":
                "MOYEN",

            "HIGH":
                "ÉLEVÉ",

            "CRITICAL":
                "CRITIQUE",

        }


        key = str(
            value
            or ""
        ).strip().upper()


        return mapping.get(
            key,
            key
            or
            "—"
        )


    @staticmethod
    def _scope_label(
        value
    ):

        mapping = {

            "LOCAL_SITE":
                "SITE LOCAL",

            "MULTI_SITE":
                "MULTI-SITES",

            "CENTRAL":
                "CENTRAL",

        }


        key = str(
            value
            or ""
        ).strip().upper()


        return mapping.get(
            key,
            key
            or
            "—"
        )


    @staticmethod
    def _storage_label(
        value
    ):

        mapping = {

            "PERSISTENT":
                "PERSISTANT",

            "SESSION":
                "SESSION",

        }


        key = str(
            value
            or ""
        ).strip().upper()


        return mapping.get(
            key,
            key
            or
            "—"
        )


    def _paragraph(
        self,
        value,
        style=None
    ):

        return Paragraph(

            escape(
                self._value(
                    value
                )
            ),

            style
            or
            self.body_style

        )


    def _label_value(
        self,
        label,
        value
    ):

        return Paragraph(

            (
                "<font color='#647984' "
                "size='6'>"
                f"<b>{escape(label)}</b>"
                "</font>"
                "<br/>"
                f"{escape(self._value(value))}"
            ),

            self.body_style

        )


    def _optimized_logo(
        self
    ):

        if not self.logo_path.exists():

            return None


        buffer = BytesIO()


        with PILImage.open(
            self.logo_path
        ) as image:

            image.thumbnail(
                (
                    320,
                    320
                ),
                PILImage.Resampling.LANCZOS
            )


            if image.mode not in {
                "RGB",
                "RGBA"
            }:

                image = image.convert(
                    "RGBA"
                )


            image.save(
                buffer,
                format="PNG",
                optimize=True
            )


        buffer.seek(
            0
        )


        return Image(

            buffer,

            width=
                20 * mm,

            height=
                20 * mm,

            kind=
                "proportional"

        )


    def _header(
        self,
        report
    ):

        logo = self._optimized_logo()


        brand_text = Paragraph(

            (
                "<font size='15'>"
                "<b>PHOENIX</b>"
                "</font>"
                "<br/>"
                "<font size='6' color='#617780'>"
                "V I S I O N&nbsp;&nbsp;A I"
                "</font>"
            ),

            ParagraphStyle(

                "PhoenixBrand",

                parent=
                    self.body_style,

                leading=
                    18,

                textColor=
                    colors.HexColor(
                        "#173744"
                    )

            )

        )


        if logo is not None:

            brand = Table(

                [
                    [
                        logo,
                        brand_text
                    ]
                ],

                colWidths=[
                    23 * mm,
                    57 * mm
                ]

            )

        else:

            brand = Table(

                [
                    [
                        brand_text
                    ]
                ],

                colWidths=[
                    80 * mm
                ]

            )


        brand.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        "MIDDLE"
                    ),

                    (
                        "LEFTPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        0
                    ),

                    (
                        "RIGHTPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        4
                    ),

                    (
                        "TOPPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        0
                    ),

                    (
                        "BOTTOMPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        0
                    ),
                ]
            )
        )


        company_style = ParagraphStyle(

            "PhoenixCompanyHeader",

            parent=
                self.body_style,

            fontName=
                "Helvetica-Bold",

            fontSize=
                6,

            leading=
                8,

            textColor=
                colors.HexColor(
                    "#637983"
                ),

            alignment=
                TA_RIGHT,

        )


        report_title_style = ParagraphStyle(

            "PhoenixReportHeader",

            parent=
                self.body_style,

            fontName=
                "Helvetica-Bold",

            fontSize=
                13,

            leading=
                16,

            textColor=
                colors.HexColor(
                    "#173744"
                ),

            alignment=
                TA_RIGHT,

        )


        report_subtitle_style = ParagraphStyle(

            "PhoenixReportSubtitle",

            parent=
                self.body_style,

            fontName=
                "Helvetica",

            fontSize=
                6,

            leading=
                8,

            textColor=
                colors.HexColor(
                    "#758992"
                ),

            alignment=
                TA_RIGHT,

        )


        classification = Table(

            [
                [
                    Paragraph(
                        "PHOENIX SECURITY TECHNOLOGIES",
                        company_style
                    )
                ],

                [
                    Paragraph(
                        "RAPPORT OPÉRATIONNEL",
                        report_title_style
                    )
                ],

                [
                    Paragraph(
                        (
                            "Document officiel généré "
                            "par Phoenix Vision AI"
                        ),
                        report_subtitle_style
                    )
                ],
            ],

            colWidths=[
                88 * mm
            ]

        )


        classification.setStyle(
            TableStyle(
                [
                    (
                        "ALIGN",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        "RIGHT"
                    ),

                    (
                        "VALIGN",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        "MIDDLE"
                    ),

                    (
                        "LEFTPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        0
                    ),

                    (
                        "RIGHTPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        0
                    ),

                    (
                        "TOPPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        1
                    ),

                    (
                        "BOTTOMPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        2
                    ),
                ]
            )
        )


        table = Table(

            [
                [
                    brand,
                    classification
                ]
            ],

            colWidths=[
                86 * mm,
                88 * mm
            ]

        )


        table.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        "MIDDLE"
                    ),

                    (
                        "LINEBELOW",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            0
                        ),
                        2,
                        colors.HexColor(
                            "#183847"
                        )
                    ),

                    (
                        "BOTTOMPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        9
                    ),

                    (
                        "LEFTPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        0
                    ),

                    (
                        "RIGHTPADDING",
                        (
                            0,
                            0
                        ),
                        (
                            -1,
                            -1
                        ),
                        0
                    ),
                ]
            )
        )


        return table


    def _metadata(
        self,
        report
    ):

        rows = [

            [
                self._label_value(
                    "RÉFÉRENCE PHOENIX",
                    report.get(
                        "reference"
                    )
                ),

                self._label_value(
                    "STATUT",
                    report.get(
                        "status"
                    )
                ),

                self._label_value(
                    "VERSION",
                    report.get(
                        "version"
                    )
                ),
            ],

            [
                self._label_value(
                    "PÉRIODE DU",
                    self._format_datetime(
                        report.get(
                            "period_start"
                        )
                    )
                ),

                self._label_value(
                    "AU",
                    self._format_datetime(
                        report.get(
                            "period_end"
                        )
                    )
                ),

                self._label_value(
                    "PÉRIMÈTRE",
                    self._scope_label(
                        report.get(
                            "scope"
                        )
                    )
                ),
            ],

            [
                self._label_value(
                    "GÉNÉRÉ PAR",
                    report.get(
                        "generated_by"
                    )
                ),

                self._label_value(
                    "RÔLE",
                    report.get(
                        "generated_role"
                    )
                ),

                self._label_value(
                    "DATE DE GÉNÉRATION",
                    self._format_datetime(
                        report.get(
                            "generated_at"
                        )
                    )
                ),
            ],

        ]


        table = Table(

            rows,

            colWidths=[
                72 * mm,
                51 * mm,
                51 * mm
            ],

        )


        table.setStyle(
            self._grid_style()
        )


        return table


    def _grid_style(
        self
    ):

        return TableStyle(
            [
                (
                    "GRID",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    .45,
                    colors.HexColor(
                        "#D3DDE1"
                    )
                ),

                (
                    "BACKGROUND",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    colors.HexColor(
                        "#FBFCFD"
                    )
                ),

                (
                    "VALIGN",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    "TOP"
                ),

                (
                    "LEFTPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    5
                ),

                (
                    "RIGHTPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    5
                ),

                (
                    "TOPPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    5
                ),

                (
                    "BOTTOMPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    5
                ),
            ]
        )


    def _section_title(
        self,
        title
    ):

        return Paragraph(

            escape(
                title
            ),

            self.section_style

        )


    def _summary(
        self,
        summary
    ):

        metrics = [

            (
                "VÉHICULES",
                summary.get(
                    "vehicles",
                    0
                )
            ),

            (
                "ÉVÉNEMENTS",
                summary.get(
                    "events",
                    0
                )
            ),

            (
                "ALERTES",
                summary.get(
                    "alerts",
                    0
                )
            ),

            (
                "PLAQUES / LAPI",
                summary.get(
                    "plates_detected",
                    0
                )
            ),

            (
                "SURVEILLANCES",
                summary.get(
                    "watchlist_active_in_period",
                    0
                )
            ),

            (
                "CORRESPONDANCES",
                summary.get(
                    "watchlist_matches",
                    0
                )
            ),

        ]


        cells = []


        for label, number in metrics:

            label_paragraph = Paragraph(

                escape(
                    label
                ),

                ParagraphStyle(

                    (
                        "MetricLabel_"
                        +
                        label
                    ),

                    parent=
                        self.body_style,

                    fontName=
                        "Helvetica-Bold",

                    fontSize=
                        5.5,

                    leading=
                        7,

                    alignment=
                        TA_CENTER,

                    textColor=
                        colors.HexColor(
                            "#657A84"
                        ),

                )

            )


            value_paragraph = Paragraph(

                (
                    "<b>"
                    +
                    escape(
                        str(
                            number
                        )
                    )
                    +
                    "</b>"
                ),

                ParagraphStyle(

                    (
                        "MetricValue_"
                        +
                        label
                    ),

                    parent=
                        self.body_style,

                    fontName=
                        "Helvetica-Bold",

                    fontSize=
                        16,

                    leading=
                        19,

                    alignment=
                        TA_CENTER,

                    textColor=
                        colors.HexColor(
                            "#183847"
                        ),

                )

            )


            cell = Table(

                [
                    [
                        label_paragraph
                    ],

                    [
                        value_paragraph
                    ],
                ],

                colWidths=[
                    29 * mm
                ],

                rowHeights=[
                    8 * mm,
                    10 * mm
                ]

            )


            cell.setStyle(
                TableStyle(
                    [
                        (
                            "ALIGN",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            "CENTER"
                        ),

                        (
                            "VALIGN",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            "MIDDLE"
                        ),

                        (
                            "LEFTPADDING",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            2
                        ),

                        (
                            "RIGHTPADDING",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            2
                        ),

                        (
                            "TOPPADDING",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            1
                        ),

                        (
                            "BOTTOMPADDING",
                            (
                                0,
                                0
                            ),
                            (
                                -1,
                                -1
                            ),
                            1
                        ),
                    ]
                )
            )


            cells.append(
                cell
            )


        table = Table(

            [
                cells
            ],

            colWidths=[
                29 * mm
            ] * 6,

            rowHeights=[
                20 * mm
            ]

        )


        table.setStyle(
            self._grid_style()
        )


        return table


    def _table(
        self,
        headers,
        rows,
        col_widths
    ):

        data = [

            [
                Paragraph(
                    f"<b>{escape(header)}</b>",
                    self.small_style
                )
                for header
                in headers
            ]

        ]


        if not rows:

            data.append(
                [
                    Paragraph(
                        (
                            "Aucune donnée enregistrée "
                            "pour cette période."
                        ),
                        self.small_style
                    )
                ]
                +
                [
                    ""
                ] * (
                    len(
                        headers
                    )
                    -
                    1
                )
            )

        else:

            for row in rows:

                data.append(
                    [
                        self._paragraph(
                            value,
                            self.small_style
                        )
                        for value
                        in row
                    ]
                )


        table = Table(

            data,

            colWidths=
                col_widths,

            repeatRows=
                1,

            hAlign=
                "LEFT"

        )


        style = TableStyle(
            [
                (
                    "BACKGROUND",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        0
                    ),
                    colors.HexColor(
                        "#EEF3F5"
                    )
                ),

                (
                    "TEXTCOLOR",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        0
                    ),
                    colors.HexColor(
                        "#4F6874"
                    )
                ),

                (
                    "GRID",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    .35,
                    colors.HexColor(
                        "#D2DCE1"
                    )
                ),

                (
                    "VALIGN",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    "TOP"
                ),

                (
                    "LEFTPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    4
                ),

                (
                    "RIGHTPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    4
                ),

                (
                    "TOPPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    4
                ),

                (
                    "BOTTOMPADDING",
                    (
                        0,
                        0
                    ),
                    (
                        -1,
                        -1
                    ),
                    4
                ),
            ]
        )


        if not rows:

            style.add(
                "SPAN",
                (
                    0,
                    1
                ),
                (
                    -1,
                    1
                )
            )


        table.setStyle(
            style
        )


        return table


    def _footer_callback(
        self,
        reference
    ):

        def footer(
            canvas,
            document
        ):

            canvas.saveState()


            canvas.setTitle(
                (
                    f"{reference} "
                    "— Phoenix Vision AI"
                )
            )

            canvas.setAuthor(
                self.COMPANY
            )

            canvas.setCreator(
                self.PRODUCT
            )

            canvas.setSubject(
                "Rapport opérationnel Phoenix"
            )


            canvas.setStrokeColor(
                colors.HexColor(
                    "#B9C6CC"
                )
            )

            canvas.setLineWidth(
                .4
            )

            canvas.line(
                16 * mm,
                10 * mm,
                194 * mm,
                10 * mm
            )


            canvas.setFont(
                "Helvetica",
                6.5
            )

            canvas.setFillColor(
                colors.HexColor(
                    "#607680"
                )
            )

            canvas.drawString(
                16 * mm,
                6.5 * mm,
                self.COMPANY
            )


            canvas.drawCentredString(
                105 * mm,
                6.5 * mm,
                reference
            )


            canvas.drawRightString(
                194 * mm,
                6.5 * mm,
                f"Page {document.page}"
            )


            canvas.restoreState()


        return footer


    def build(
        self,
        report,
        integrity,
        audit
    ):

        if not isinstance(
            report,
            dict
        ):

            raise ValueError(
                "Rapport invalide."
            )


        snapshot = (
            report.get(
                "snapshot"
            )
            or
            {}
        )


        summary = (
            snapshot.get(
                "summary"
            )
            or
            {}
        )


        sections = set(
            report.get(
                "sections"
            )
            or
            [
                "summary",
                "vehicles",
                "events",
                "alerts",
                "anpr",
                "watchlist"
            ]
        )


        buffer = BytesIO()


        document = SimpleDocTemplate(

            buffer,

            pagesize=
                A4,

            rightMargin=
                16 * mm,

            leftMargin=
                16 * mm,

            topMargin=
                13 * mm,

            bottomMargin=
                16 * mm,

            title=
                self._value(
                    report.get(
                        "reference"
                    )
                ),

            author=
                self.COMPANY

        )


        story = []


        story.append(
            self._header(
                report
            )
        )

        story.append(
            Spacer(
                1,
                6 * mm
            )
        )

        story.append(
            self._metadata(
                report
            )
        )


        if "summary" in sections:

            story.append(
                self._section_title(
                    "SYNTHÈSE OPÉRATIONNELLE"
                )
            )

            story.append(
                self._summary(
                    summary
                )
            )


        if "vehicles" in sections:

            history_rows = []

            for row in (
                snapshot.get(
                    "history",
                    {}
                ).get(
                    "recent",
                    []
                )
            ):

                history_rows.append(
                    [
                        self._value(
                            row.get(
                                "uuid"
                            )
                        )[:12],

                        self._vehicle_type(
                            row.get(
                                "label"
                            )
                        ),

                        (
                            row.get(
                                "plate"
                            )
                            or
                            "NON LUE"
                        ),

                        self._format_datetime(
                            (
                                row.get(
                                    "last_seen"
                                )
                                or
                                row.get(
                                    "created_at"
                                )
                            )
                        ),

                        row.get(
                            "last_camera"
                        ),

                        self._threat_label(
                            row.get(
                                "threat_level"
                            )
                        ),
                    ]
                )


            story.append(
                self._section_title(
                    "VÉHICULES OBSERVÉS"
                )
            )

            story.append(
                self._table(

                    [
                        "UUID",
                        "TYPE",
                        "PLAQUE",
                        "DERNIÈRE DÉTECTION",
                        "CAMÉRA",
                        "MENACE"
                    ],

                    history_rows,

                    [
                        28 * mm,
                        25 * mm,
                        24 * mm,
                        40 * mm,
                        27 * mm,
                        30 * mm
                    ]

                )
            )


        if "events" in sections:

            event_rows = []

            for row in (
                snapshot.get(
                    "events",
                    {}
                ).get(
                    "recent",
                    []
                )
            ):

                event_rows.append(
                    [
                        row.get(
                            "type"
                        ),

                        row.get(
                            "level"
                        ),

                        row.get(
                            "description"
                        ),

                        row.get(
                            "vehicle_uuid"
                        ),

                        row.get(
                            "timestamp"
                        ),
                    ]
                )


            story.append(
                self._section_title(
                    "ÉVÉNEMENTS"
                )
            )

            story.append(
                self._table(

                    [
                        "TYPE",
                        "NIVEAU",
                        "DESCRIPTION",
                        "VÉHICULE",
                        "DATE / HEURE"
                    ],

                    event_rows,

                    [
                        30 * mm,
                        22 * mm,
                        53 * mm,
                        34 * mm,
                        35 * mm
                    ]

                )
            )


        if "alerts" in sections:

            alert_rows = []

            for row in (
                snapshot.get(
                    "alerts",
                    {}
                ).get(
                    "recent",
                    []
                )
            ):

                alert_rows.append(
                    [
                        row.get(
                            "type"
                        ),

                        row.get(
                            "level"
                        ),

                        row.get(
                            "status"
                        ),

                        row.get(
                            "message"
                        ),

                        row.get(
                            "timestamp"
                        ),
                    ]
                )


            story.append(
                self._section_title(
                    "ALERTES"
                )
            )

            story.append(
                self._table(

                    [
                        "TYPE",
                        "NIVEAU",
                        "STATUT",
                        "MESSAGE",
                        "DATE / HEURE"
                    ],

                    alert_rows,

                    [
                        29 * mm,
                        20 * mm,
                        25 * mm,
                        64 * mm,
                        36 * mm
                    ]

                )
            )


        if "anpr" in sections:

            anpr_rows = []

            for row in (
                snapshot.get(
                    "anpr",
                    {}
                ).get(
                    "recent",
                    []
                )
            ):

                confidence = (
                    row.get(
                        "plate_confidence"
                    )
                )


                if confidence:

                    confidence = (
                        f"{float(confidence):.1f} %"
                    )


                anpr_rows.append(
                    [
                        row.get(
                            "plate"
                        ),

                        confidence,

                        row.get(
                            "plate_status"
                        ),

                        (
                            row.get(
                                "plate_last_seen"
                            )
                            or
                            row.get(
                                "last_seen"
                            )
                        ),

                        row.get(
                            "last_camera"
                        ),
                    ]
                )


            story.append(
                self._section_title(
                    "PLAQUES / LAPI"
                )
            )

            story.append(
                self._table(

                    [
                        "PLAQUE",
                        "CONFIANCE",
                        "STATUT",
                        "DERNIÈRE LECTURE",
                        "CAMÉRA"
                    ],

                    anpr_rows,

                    [
                        30 * mm,
                        28 * mm,
                        34 * mm,
                        48 * mm,
                        34 * mm
                    ]

                )
            )


        if "watchlist" in sections:

            watchlist_rows = []

            for row in (
                snapshot.get(
                    "watchlist",
                    {}
                ).get(
                    "recent",
                    []
                )
            ):

                watchlist_rows.append(
                    [
                        row.get(
                            "plate"
                        ),

                        row.get(
                            "category"
                        ),

                        row.get(
                            "priority"
                        ),

                        row.get(
                            "status"
                        ),

                        row.get(
                            "created_at"
                        ),

                        row.get(
                            "approved_by"
                        ),
                    ]
                )


            story.append(
                self._section_title(
                    "LISTE DE SURVEILLANCE"
                )
            )

            story.append(
                self._table(

                    [
                        "PLAQUE",
                        "CATÉGORIE",
                        "PRIORITÉ",
                        "STATUT",
                        "CRÉATION",
                        "VALIDÉ PAR"
                    ],

                    watchlist_rows,

                    [
                        27 * mm,
                        30 * mm,
                        24 * mm,
                        26 * mm,
                        41 * mm,
                        26 * mm
                    ]

                )
            )


        coverage_rows = []

        for name, info in (
            snapshot.get(
                "data_coverage",
                {}
            ).items()
        ):

            coverage_rows.append(
                [
                    info.get(
                        "label"
                    )
                    or
                    name,

                    self._storage_label(
                        info.get(
                            "storage"
                        )
                    ),

                    info.get(
                        "source"
                    ),
                ]
            )


        coverage_table = (
            self._table(

                [
                    "SOURCE",
                    "STOCKAGE",
                    "ORIGINE"
                ],

                coverage_rows,

                [
                    69 * mm,
                    39 * mm,
                    66 * mm
                ]

            )
        )


        story.append(
            KeepTogether(
                [
                    self._section_title(
                        "SOURCES ET COUVERTURE"
                    ),

                    coverage_table
                ]
            )
        )


        story.append(
            self._section_title(
                "INTÉGRITÉ DU DOCUMENT"
            )
        )


        integrity_table = Table(

            [
                [
                    self._label_value(
                        "SNAPSHOT",
                        (
                            "VALIDÉ"
                            if integrity.get(
                                "snapshot_valid"
                            )
                            else
                            "ÉCHEC"
                        )
                    ),

                    self._label_value(
                        "JOURNAL D'AUDIT",
                        (
                            "VALIDÉ"
                            if integrity.get(
                                "audit_valid"
                            )
                            else
                            "ÉCHEC"
                        )
                    ),
                ],

                [
                    self._label_value(
                        "SHA-256",
                        report.get(
                            "snapshot_hash"
                        )
                    ),

                    self._label_value(
                        "ÉVÉNEMENTS D'AUDIT",
                        integrity.get(
                            "events"
                        )
                    ),
                ],
            ],

            colWidths=[
                87 * mm,
                87 * mm
            ]

        )


        integrity_table.setStyle(
            self._grid_style()
        )


        story.append(
            integrity_table
        )


        story.append(
            self._section_title(
                "TRAÇABILITÉ"
            )
        )


        audit_rows = []

        for event in (
            audit
            or
            []
        ):

            audit_rows.append(
                [
                    event.get(
                        "action"
                    ),

                    (
                        self._value(
                            event.get(
                                "actor"
                            )
                        )
                        +
                        " · "
                        +
                        self._value(
                            event.get(
                                "actor_role"
                            )
                        )
                    ),

                    event.get(
                        "timestamp"
                    ),
                ]
            )


        story.append(
            self._table(

                [
                    "ACTION",
                    "ACTEUR",
                    "DATE / HEURE"
                ],

                audit_rows,

                [
                    55 * mm,
                    55 * mm,
                    64 * mm
                ]

            )
        )


        story.append(
            Spacer(
                1,
                7 * mm
            )
        )


        footer_text = Paragraph(

            (
                "<b>PHOENIX SECURITY TECHNOLOGIES</b>"
                "<br/>"
                "L'innovation au service de la protection."
                "<br/>"
                "Document généré par Phoenix Vision AI."
            ),

            self.subtitle_style

        )


        story.append(
            footer_text
        )


        reference = self._value(
            report.get(
                "reference"
            )
        )


        footer = self._footer_callback(
            reference
        )


        document.build(

            story,

            onFirstPage=
                footer,

            onLaterPages=
                footer

        )


        pdf_bytes = buffer.getvalue()

        buffer.close()


        return pdf_bytes


report_pdf_service = (
    ReportPdfService()
)
