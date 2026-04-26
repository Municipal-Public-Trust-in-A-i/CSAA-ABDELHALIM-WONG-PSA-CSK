#!/usr/bin/env python3
"""Build MOTION-STRIKE-AUTHORITIES-CACHE-MANIFEST.json (authoritative list for 801/802)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def rel_exists(p: str) -> bool:
    return (ROOT / p).is_file()


def main() -> int:
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_master_json": [
            "801-MOTION-STRIKE-APR-22/PARSED/AUTHORITY-INDEX/MASTER-AUTHORITY-LIST.json",
            "802-MOTION-STRIKE-APR-22/PARSED/AUTHORITY-INDEX/MASTER-AUTHORITY-LIST.json",
        ],
        "gap_report": "gap-report-motion-strike.json",
        "note": (
            "CCP 435/436: leginfo.legislature.ca.gov. "
            "Case law: static.case.law single-opinion PDFs where available; "
            "McNeal (80 Cal.App.5th 841) from https://courts.ca.gov/opinions/documents/B313472.PDF; "
            "Today's IV (83 Cal.App.5th 1137) from https://storage.courtlistener.com/pdf/2022/10/05/todays_iv_inc._v._l.a._county_metropolitan_transportation_auth..pdf . "
            "F.E.V. 15 Cal.App.5th 463: same slip as 462 (copy). "
            "Coyne: canonical cite 35 Cal.2d 257; Case.law uses 36 Cal.2d 257 for the same opinion (both PDFs stored). "
            "law.justia.com returned HTTP 403 to curl in this environment; use a browser for mirrors if needed."
        ),
        "statutes": [
            {
                "citation": "C.C.P. § 435",
                "local_path": "statutes-cal/CCP-435.md",
                "source": "leginfo",
                "status": "cached" if rel_exists("statutes-cal/CCP-435.md") else "missing",
            },
            {
                "citation": "C.C.P. § 436",
                "local_path": "statutes-cal/CCP-436.md",
                "source": "leginfo",
                "status": "cached" if rel_exists("statutes-cal/CCP-436.md") else "missing",
            },
            {
                "citation": "Code of Civil Procedure § 430.70",
                "local_path": "statutes-cal/CCP-430.70.md",
                "source": "leginfo",
                "status": "cached" if rel_exists("statutes-cal/CCP-430.70.md") else "missing",
            },
            {
                "citation": "Civ. Code § 47(b)",
                "local_path": "statutes-cal/CIV-47.md",
                "source": "existing cache",
                "status": "cached" if rel_exists("statutes-cal/CIV-47.md") else "missing",
            },
            {
                "citation": "Civ. Code § 3294 / 3294(a)",
                "local_path": "statutes-cal/CIV-3294.md",
                "source": "existing cache",
                "status": "cached" if rel_exists("statutes-cal/CIV-3294.md") else "missing",
            },
        ],
        "cases_california": [
            {
                "citation": "1 Cal.3d 467",
                "local_path": "opinions-pdf/Demurrer-cal-3d-vol1-p467-Kulchar-v-Kulchar.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "11 Cal.4th 274",
                "local_path": "opinions-pdf/Motion-Strike-cal-4th-vol11-p274-Trope-v-Katz.pdf",
                "source": "static.case.law",
            },
            {
                "citation": "12 Cal.4th 631",
                "local_path": "opinions-pdf/Demurrer-cal-4th-vol12-p631-Lazar-v-Superior-Court.pdf",
                "source": "Case.law (Demurrer cache); duplicate file Lazar-v-Superior-Court-12-Cal-4th-631.pdf",
            },
            {
                "citation": "146 Cal.App.3d 470",
                "local_path": "opinions-pdf/Demurrer-cal-app-3d-vol146-p470-Omega-Video-Inc-v-Superior-Court.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "15 Cal.App.5th 462",
                "local_path": "opinions-pdf/Demurrer-cal-app-5th-vol15-p462-FEV-v-City-of-Anaheim-Justia.pdf",
                "source": "Case.law / Justia (Demurrer cache)",
            },
            {
                "citation": "15 Cal.App.5th 463",
                "local_path": "opinions-pdf/Motion-Strike-cal-app-5th-vol15-p463-FEV-v-City-of-Anaheim-same-slip-as-p462.pdf",
                "source": "Copy of 462 slip (801 MPA pincite)",
            },
            {
                "citation": "169 Cal.App.4th 976",
                "local_path": "opinions-pdf/Motion-Strike-cal-app-4th-vol169-p976-Food-Pro-International-Inc-v-Farmers-Insurance-Exchange.pdf",
                "source": "static.case.law",
            },
            {
                "citation": "17 Cal.App.4th 468",
                "local_path": "opinions-pdf/Motion-Strike-cal-app-4th-vol17-p468-Stewart-v-Truck-Insurance-Exchange.pdf",
                "source": "static.case.law",
            },
            {
                "citation": "227 Cal.App.4th 813",
                "local_path": "opinions-pdf/Demurrer-cal-app-4th-vol227-p813-Singh-v-Lipworth.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "265 Cal.App.2d 82",
                "local_path": "opinions-pdf/Demurrer-cal-app-2d-vol265-p82-Wouldridge-v-Burns.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "28 Cal.3d 908",
                "local_path": "opinions-pdf/Motion-Strike-cal-3d-vol28-p908-Department-of-Social-Services-v-Ronald-P.pdf",
                "source": "static.case.law",
            },
            {
                "citation": "35 Cal.2d 257",
                "local_path": "opinions-pdf/Motion-Strike-cal-2d-vol35-p257-Coyne-v-Krempels-same-opinion-CAP-uses-vol36.pdf",
                "source": "Copy of 36 Cal.2d 257 extract (reporter vol. note in manifest `note`)",
            },
            {
                "citation": "36 Cal.2d 257",
                "local_path": "opinions-pdf/Motion-Strike-cal-2d-vol36-p257-Coyne-v-Krempels.pdf",
                "source": "static.case.law",
            },
            {
                "citation": "38 Cal.3d 355",
                "local_path": "opinions-pdf/Motion-Strike-cal-3d-vol38-p355-Ribas-v-Clark.pdf",
                "source": "static.case.law",
            },
            {
                "citation": "49 Cal.App.3d 917",
                "local_path": "opinions-pdf/Demurrer-cal-app-3d-vol49-p917-Norton-v-Hines.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "58 Cal.App.2d 878",
                "local_path": "opinions-pdf/Demurrer-cal-app-2d-vol58-p878-Rico-v-Nasser-Bros-Realty-Co.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "59 Cal.2d 618",
                "local_path": "opinions-pdf/Demurrer-cal-2d-vol59-p618-Prentice-v-North-American-Title-Guaranty-Corp.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "71 Cal.App.4th 268",
                "local_path": "opinions-pdf/Demurrer-cal-app-4th-vol71-p268-Shaolian-v-Safeco-Insurance.pdf",
                "source": "Case.law (Demurrer cache)",
            },
            {
                "citation": "80 Cal.App.5th 841",
                "local_path": "opinions-pdf/Motion-Strike-cal-app-5th-vol80-p841-McNeal-v-Whittaker-B313472-courts-ca-gov.pdf",
                "source": "courts.ca.gov B313472",
            },
            {
                "citation": "83 Cal. App. 5th 1137",
                "local_path": "opinions-pdf/Motion-Strike-cal-app-5th-vol83-p1137-Todays-IV-v-LAMTA-courtlistener-storage.pdf",
                "source": "CourtListener storage (see note)",
            },
            {
                "citation": "96 Cal.App.4th 1017",
                "local_path": "opinions-pdf/Motion-Strike-cal-app-4th-vol96-p1017-American-Airlines-Inc-v-Sheppard-Mullin-Richter-Hampton.pdf",
                "source": "static.case.law",
            },
        ],
        "cases_federal": [
            {
                "citation": "98 U.S. 61",
                "local_path": "opinions-pdf/Demurrer-us-vol98-p61-States-v-Throckmorton.pdf",
                "source": "Case.law (Demurrer cache)",
            }
        ],
    }

    # add status
    for bucket in ("cases_california", "cases_federal"):
        for row in manifest.get(bucket, []):
            lp = row.get("local_path", "")
            row["status"] = "cached" if lp and rel_exists(lp) else "missing"

    out = ROOT / "MOTION-STRIKE-AUTHORITIES-CACHE-MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
