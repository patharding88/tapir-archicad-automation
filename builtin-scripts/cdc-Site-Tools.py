# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
CDC Site Tools - Archicad Automation Script
===========================================

A comprehensive surveying and site planning tool for Archicad with three main components:
1. Boundary Tool - Create property boundaries and setback lines

Requirements:
- Python 3.x
- aclib module (from Tapir Archicad Automation)
- tkinter (for UI)
- math (for calculations)
- re (for string parsing)

This script is based on the requirements in SiteTools_Requirements.md and QDC/CDC rules in the cursor rules.
"""

import aclib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import re
import json
from typing import List, Tuple, Dict, Optional
import csv
import os

__version__ = '1.3.0'  # CDC Site Tools version

# --- Polyline Drawing Settings ---
SETBACK_LAYER = 'Setback Lines'
SETBACK_LINETYPE = 'Dashed'
SETBACK_PEN = 5
ROAD_LAYER = 'Road Lines'
ROAD_LINETYPE = 'Solid'
ROAD_PEN = 1

# --- Planning Scheme Presets (QDC MP1.1, MP1.2, etc.) ---
PLANNING_SCHEME_PRESETS = {
    "QDC MP1.1": {
        "front": 6.0, "side": 1.5, "rear": 3.0, "secondary": 2.0,
        "front_min": 3.0, "front_hab": 3.45, "garage": 3.0
    },
    "QDC MP1.2": {
        "front": 6.0, "side": 1.5, "rear": 3.0, "secondary": 2.0, "garage_front": 6.0,
        "front_min": 3.0, "front_hab": 3.45, "garage": 6.0
    },
}

# --- Site Presets (from deep lot table) ---
SITE_RECTANGLE_PRESETS = {
    # 32 Deep Lots
    '32m x 10m': (10.0, 32.0),
    '32m x 12.5m': (12.5, 32.0),
    '32m x 14.0m': (14.0, 32.0),
    '32m x 14.5m': (14.5, 32.0),
    '32m x 16.0m': (16.0, 32.0),
    '32m x 18.0m': (18.0, 32.0),
    # 30 Deep Lots
    '30m x 10m': (10.0, 30.0),
    '30m x 12.5m': (12.5, 30.0),
    '30m x 14.0m': (14.0, 30.0),
    '30m x 14.5m': (14.5, 30.0),
    '30m x 16.0m': (16.0, 30.0),
    '30m x 18.0m': (18.0, 30.0),
    # 28 Deep Lots
    '28m x 4.6m': (4.6, 28.0),
    '28m x 6.6m': (6.6, 28.0),
    '28m x 7.6m': (7.6, 28.0),
    '28m x 7.5m': (7.5, 28.0),
    '28m x 9.0m': (9.0, 28.0),
    '28m x 10.0m': (10.0, 28.0),
    '28m x 12.5m': (12.5, 28.0),
    '28m x 14.0m': (14.0, 28.0),
    '28m x 16.0m': (16.0, 28.0),
    '28m x 18.0m': (18.0, 28.0),
    # 25 Deep Lots
    '25m x 4.6m': (4.6, 25.0),
    '25m x 6.6m': (6.6, 25.0),
    '25m x 7.6m': (7.6, 25.0),
    '25m x 7.5m': (7.5, 25.0),
    '25m x 9.0m': (9.0, 25.0),
    '25m x 10.0m': (10.0, 25.0),
    '25m x 12.5m': (12.5, 25.0),
    '25m x 14.0m': (14.0, 25.0),
    '25m x 16.0m': (16.0, 25.0),
    '25m x 18.0m': (18.0, 25.0),
    # 21 Deep Lots
    '21m x 7.5m': (7.5, 21.0),
    '21m x 9.0m': (9.0, 21.0),
}

PLANNING_SCHEME_CSV = os.path.join('docs', 'planning-schemes', 'Planning Schemes (All).csv')
PLANNING_SCHEME_MD = os.path.join('docs', 'planning-schemes', 'planning-scheme-documents.md')

# --- Embedded Planning Scheme Markdown ---
PLANNING_SCHEME_MD_TEXT = '''
# Planning Scheme Documents Reference

Below is a list of all planning schemes (councils) and their associated documents, with numeric prefixes removed and sorted alphabetically.

---

## Brisbane City Council (BCC)

- WEBSITE — [Council Website](https://www.brisbane.qld.gov.au/)
- MAP — [Brisbane City ePlan](https://cityplan.brisbane.qld.gov.au/eplan) — (Unlikely to work for very new estates)
- PLAN — [BCC Dual Occupancy](https://cityplan.brisbane.qld.gov.au/eplan/rules/0/161/0/0/0/240)
- PLAN — [BCC Dwelling House Code](https://cityplan.brisbane.qld.gov.au/eplan/rules/0/162/0/0/0/240) — Lots over 450sqm
- PLAN — [BCC Small Lot Code](https://cityplan.brisbane.qld.gov.au/eplan/rules/0/163/0/0/0/240) — Lots under 450sqm
- DRIVEWAY — [BCC Driveway Fact Sheet (Website)](https://www.brisbane.qld.gov.au/laws-and-permits/laws-and-permits-for-residents/footpaths-and-driveways/driveway-permits/residential-driveway-permits) — Look 'Self Assessment' for small lot (Less than 450)
- DRIVEWAY — [BSD-2021 - Kerb Profiles](https://docs.brisbane.qld.gov.au/standard-drawings/20190726_-_bsd-2001_c_kerb-profiles.pdf)
- DRIVEWAY — [BSD-2022 - BCC Vehicle Crossing](https://docs.brisbane.qld.gov.au/standard-drawings/20200120_-_bsd-2022_e_vehicle-crossing_driveway_single-dwelling.pdf) — See fact sheet also for small lot driveway
- DRIVEWAY — [BSD-2023 - BCC Grid Crossing](https://docs.brisbane.qld.gov.au/standard-drawings/Minor%20Amendment%20S/bsd-2023_f_vehicle-crossing-driveway_grid-crossing-and-invert-modification.pdf) — Kerb Riser / Kerb Ramp / Grid Crossing Detail
- DRIVEWAY — [BSD-2024 - Grades (3.75m Crossover)](https://docs.brisbane.qld.gov.au/standard-drawings/20171201_bsd-2024_c_vehicle-crossing-driveway_grades_3.75m-verge.pdf) — See fact sheet also for small lot driveway
- DRIVEWAY — [BSD-2025 - Grades (4.25m Crossover)](https://docs.brisbane.qld.gov.au/standard-drawings/20171201_bsd-2025_c_vehicle-crossing-driveway_grades_4.25m-verge.pdf) — See fact sheet also for small lot driveway
- STORMWATER — [Kerb Adaptor Detail](https://docs.brisbane.qld.gov.au/standard-drawings/Minor-Amendment-N/8000/230602_bsd-8114_c_roofwater-drainage-connection_kerb-adaptor-installation.pdf)
- STORMWATER — [Surface Drainage](https://docs.brisbane.qld.gov.au/City%20Plan/Standard%20Drawings/8000%20-%20Stormwater%20drainage%20and%20Water%20Quality/bsd-8113_c_roof-and-surface-water-drainage-for-site-developments.pdf) — Rubble Pit is not a lawful point of discharge!
- TIPS — [Traditiona Character Guide](https://www.brisbane.qld.gov.au/sites/default/files/documents/2020-02/20200203-traditional-housing-design-guide.pdf)

---

## Goldcoast City Council (GCC)

- WEBSITE — [Council Website](https://www.goldcoast.qld.gov.au/Home)
- MAP — [City Plan Map](https://cityplan.goldcoast.qld.gov.au/eplan/property/0/0/210)
- PLAN — [Full City Plan](https://cityplan.goldcoast.qld.gov.au/eplan/rules/0/224/0/0/0/210)
- PLAN — [PD Online](https://cogc.cloud.infor.com/ePathway/ePthProd/web/GeneralEnquiry/EnquiryLists.aspx?ModuleCode=LAP) — For approvals already in progress. Use map instead
- PLAN — [Residential Zone Code](https://cityplan.goldcoast.qld.gov.au/eplan/rules/0/37/0/0/0/210) — Low 6.2.1, Med 6.2.2, High 6.2.3 Res.
- DRIVEWAY — [Driveway Checklist](https://www.goldcoast.qld.gov.au/Planning-building/Development-applications/DA-types/Driveways-vehicular-crossings/Standard-vehicular-crossing/Vehicular-crossing-checklist) — Select No for everything to view all requirements
- DRIVEWAY — [RSD-010 Longitudinal Driveway](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/standard-drawings-rsd-101-residential-driveways-sheet-2.pdf)
- DRIVEWAY — [RSD-100 Vehicle Crossing](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/standard-drawings-rsd-100-residential-driveways-sheet-1.pdf) — Dual occ, Dwelling and Multi dwelling required standard is NMP1.1
- DRIVEWAY — [Tree Removal notes](https://www.goldcoast.qld.gov.au/Planning-building/Development-applications/DA-types/Driveways-vehicular-crossings/Combined-non-standard-vehicular-crossing-tree-removal)
- TIPS — [Bushfire Guide](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/2/pdfs/brochures-amp-factsheets/bushfire-resilient-design-guideline.pdf)
- TIPS — [Flood Guide](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/flood-resilient-guide.pdf)
- TIPS — [Residential Fencing](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/guide-for-residential-fences.pdf)
- TIPS — [Sloping Sites Guide](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/2/pdfs/brochures-amp-factsheets/building-on-sloping-sites.pdf)

---

## Gympie Regional Council (GRC)

- PLAN — [Planning Scheme 4.0](https://www.gympie.qld.gov.au/downloads/file/5065/planning-scheme-v4-0) — 6.1 P70 Residential Living Zone Code
- WEBSITE — [Council Website](https://www.gympie.qld.gov.au/)
- MAP — [Interactive Mapping](https://maps.gympie.qld.gov.au/IntraMaps23A/?project=PublicWeb&module=Property)
- STANDARD — [Standard Drawings](https://www.gympie.qld.gov.au/downloads/file/4044/standard-drawing-index)
- DRIVEWAY — [Standard Drawings](https://www.gympie.qld.gov.au/downloads/file/4044/standard-drawing-index)
- DRIVEWAY — [Driveway Checklist](https://www.goldcoast.qld.gov.au/Planning-building/Development-applications/DA-types/Driveways-vehicular-crossings/Standard-vehicular-crossing/Vehicular-crossing-checklist) — Select No for everything to view all requirements
- DRIVEWAY — [RSD-010 Longitudinal Driveway](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/standard-drawings-rsd-101-residential-driveways-sheet-2.pdf)
- DRIVEWAY — [RSD-100 Vehicle Crossing](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/standard-drawings-rsd-100-residential-driveways-sheet-1.pdf) — Dual occ, Dwelling and Multi dwelling required standard is NMP1.1
- DRIVEWAY — [Tree Removal notes](https://www.goldcoast.qld.gov.au/Planning-building/Development-applications/DA-types/Driveways-vehicular-crossings/Combined-non-standard-vehicular-crossing-tree-removal)
- TIPS — [Bushfire Guide](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/2/pdfs/brochures-amp-factsheets/bushfire-resilient-design-guideline.pdf)
- TIPS — [Flood Guide](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/flood-resilient-guide.pdf)
- TIPS — [Residential Fencing](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/3/pdfs/brochures-amp-factsheets/guide-for-residential-fences.pdf)
- TIPS — [Sloping Sites Guide](https://www.goldcoast.qld.gov.au/files/sharedassets/public/v/2/pdfs/brochures-amp-factsheets/building-on-sloping-sites.pdf)

---

## Ipswich City Council (ICC)

- WEBSITE — [Council Website](https://www.ipswich.qld.gov.au/)
- MAP — [Development.i Interactive Mapping](https://developmenti.ipswich.qld.gov.au/)
- MAP — [Historic Flood Maps](https://developmenti.ipswich.qld.gov.au/) — Note: you should get new flood maps from Development.i Site Report
- PLAN — [Dwelling Code General Building Guide](https://www.ipswich.qld.gov.au/__data/assets/pdf_file/0003/35094/General-Building-Guidelines.pdf) — General building and setback guide for residential dwellings
- PLAN — [Dwelling Code Ref.12.6.1 & 12.6.2](https://www.ipswichplanning.com.au/__data/assets/pdf_file/0020/1955/ips_part_12_div_06_residential_code.pdf) — Refer to 12.6 From Page 82(8)-90 for Setbacks (Hint: MP1.1 & MP1.2)
- DRIVEWAY — [Driveway Fact Sheet](https://www.ipswich.qld.gov.au/__data/assets/pdf_file/0020/67151/Fact-Sheet-Driveway.pdf)
- DRIVEWAY — [SR.12 Crossover without kerb](https://www.ipswich.qld.gov.au/__data/assets/pdf_file/0014/8402/sd_r15.pdf)
- DRIVEWAY — [SR.12 Driveway Profile](https://www.ipswich.qld.gov.au/__data/assets/pdf_file/0007/8962/sd_r12.pdf)
- DRIVEWAY — [SR.16 Rural Driveway with culvert](https://www.ipswich.qld.gov.au/__data/assets/pdf_file/0019/8209/sd_r16.pdf)
- STORMWATER — [Soakage Pits](https://www.ipswich.qld.gov.au/__data/assets/pdf_file/0016/10807/soakage_pit_guideline_drawing.pdf)
- TIPS — [Retaining Walls](https://edoc.ipswich.qld.gov.au/objective/download.php?id=A4162018&ext=pdf&env=iccecm&plat=pdonline)

---

## Lockyer Valley Regional Council (LVRC)

- PLAN — [Dwelling Fact Sheet (Use planning scheme first)](https://www.lockyervalley.qld.gov.au/repository/libraries/id:2eccbxg5l17q9su8pzhy/hierarchy/our-services/development-services/documents/planning-factsheets/Dwelling%20Houses%20%20Secondary%20Dwellings%20Info%20Sheet.pdf) — Dwelling house & Secondary Dweiiling Fact Sheet
- PLAN — [Planning Scheme V1](https://eplan.lvrc.qld.gov.au/eplan/rules/0/32/0/0/0/69) — 9.3.3  Dwelling house code
- WEBSITE — [Council Website](https://www.lockyervalley.qld.gov.au/)
- MAP — [Interactive Mapping](https://eplan.lvrc.qld.gov.au/)
- STANDARD — [Standard Drawings](https://www.gympie.qld.gov.au/downloads/file/4044/standard-drawing-index)
- DRIVEWAY — [IPWEA RSD-100](https://www.ipwea-qnt.com/products-resources/new-standard-drawings)
- DRIVEWAY — [IPWEA RSD-101](https://www.ipwea-qnt.com/products-resources/new-standard-drawings)
- STORMWATER — [Fact Sheet (Only)](https://www.lockyervalley.qld.gov.au/repository/libraries/id:2eccbxg5l17q9su8pzhy/hierarchy/our-services/plumbing-and-drainage/documents/plumbing-applications/Stormwater%20Fact%20sheet.pdf)

---

## Logan City Council (LCC)

- WEBSITE — [Council Website](https://www.logan.qld.gov.au/)
- MAP — [Flood Mapping](https://flood.logan.qld.gov.au/)
- MAP — [Interactive Mapping](https://loganhub.com.au/interactive-mapping)
- MAP — [Property Report](https://loganhub.com.au/interactive-mapping)
- PLAN — [Planning Scheme](https://logan.isoplan.com.au/eplan/rules/0/137/0/0/0/192) — eScheme - Dwelling House Code
- STANDARD — [Stanard drawings LCC](https://logan.isoplan.com.au/eplan/rules/0/121/0/0/0/192)
- DRIVEWAY — [Driveway Fact Sheet](https://www.logan.qld.gov.au/downloads/file/1518/vehicular-driveway-crossover-fact-sheet-)
- DRIVEWAY — [Kerb Profiles](https://lcc-docs-planning.s3-ap-southeast-2.amazonaws.com/root/Logan+Planning+Scheme+2015/Standard+Drawings/Movement+Infrastructure/Kerb+and+Channel/IPWEA+RS-080+Kerb+and+channel+-+Profiles+and+dimensions.pdf) — Rural Vehicle Crossing
- DRIVEWAY — [RS-049](https://lcc-docs-planning.s3-ap-southeast-2.amazonaws.com/root/Logan+Planning+Scheme+2015/Standard+Drawings/Movement+Infrastructure/Crossovers/IPWEA+RS-049+Vehicle+crossings+-+Residential+driveways+-+Plan+1+of+2.pdf) — Low Density Vehicle Crossing 1/2
- DRIVEWAY — [RS-050](https://lcc-docs-planning.s3-ap-southeast-2.amazonaws.com/root/Logan+Planning+Scheme+2015/Standard+Drawings/Movement+Infrastructure/Crossovers/IPWEA+RS-050+Vehicle+crossings+-+Residential+driveways+-+Plan+2+of+2.pdf) — Low Density Vehicle Crossing 2/2
- DRIVEWAY — [RS-056](https://lcc-docs-planning.s3-ap-southeast-2.amazonaws.com/root/Logan+Planning+Scheme+2015/Standard+Drawings/Movement+Infrastructure/Crossovers/IPWEA+RS-056+Vehicle+crossings+-+Rural+driveway.pdf) — Rural Vehicle Crossing
- STORMWATER — [Kerb Outlets](https://lcc-docs-planning.s3-ap-southeast-2.amazonaws.com/root/Logan+Planning+Scheme+2015/Standard+Drawings/Movement+Infrastructure/Kerb+and+Channel/IPWEA+RS-081+Kerb+and+channel+-+Residential+drainage+connections.pdf)
- STORMWATER — [Rubble Pits on rural only](https://lcc-docs-planning.s3-ap-southeast-2.amazonaws.com/root/Logan+Planning+Scheme+2015/Standard+Drawings/Movement+Infrastructure/Kerb+and+Channel/IPWEA+RS-081+Kerb+and+channel+-+Residential+drainage+connections.pdf) — Dwelling fact sheet notes Rubble Pits are only allowed on rural lots
- TIPS — [Dwellings Fact Sheet](https://www.logan.qld.gov.au/downloads/file/278/fact-sheet-domestic-housing)

---

## Moreton Bay Regional Council (MBRC)

- WEBSITE — [Council Website](https://www.moretonbay.qld.gov.au/)
- MAP — [Flood check](https://www.moretonbay.qld.gov.au/Services/Property-Ownership/Flooding/Flood-Check) — E-Mapping for flood check property report
- MAP — [My Property Lookup](https://www.moretonbay.qld.gov.au/Services/Building-Development/Planning-Schemes/My-Property-Look-Up) — (Unlikely to work for very new estates)
- PLAN — [E-SCHEME - Version 7](https://consult.moretonbay.qld.gov.au/kpse/event/45F72852-752D-445F-B1F2-05075914CC34/section/s1360106863373) — Contains all planning SCHEMES in this table eg. Sections 03 and 04
- SCHEME — [9.4.3 Site earthworks code](https://www.moretonbay.qld.gov.au/files/assets/public/v/2/services/building-development/mbrc-plan/v7/mbrc-planning-scheme-part-9.4.3.pdf)
- SCHEME — [Flood, Overland, Coastal](https://www.moretonbay.qld.gov.au/files/assets/public/v/1/services/building-development/mbrc-plan/psp/v6/flood_hazard_coastal_hazard_overland.pdf) — Planning scheme for Flood, Overlans Flow and Coastal Areas
- SCHEME — [Landslide](https://www.moretonbay.qld.gov.au/files/assets/public/v/1/services/building-development/mbrc-plan/psp/v6/landslide_hazard.pdf) — Landslide Hazard Areas
- SETBACKS — [9.3 Dwelling House Codes](https://www.moretonbay.qld.gov.au/files/assets/public/v/2/services/building-development/mbrc-plan/v7/mbrc-planning-scheme-part-9.3.1.pdf)
- DRIVEWAY — [Driveway Fact Sheet](https://www.moretonbay.qld.gov.au/files/assets/public/v/1/services/building-development/mbrc-plan/psp/v6/integrated_design_appendix_a.pdf) — Refer to 14.1 Driveway crossover and driveway
- DRIVEWAY — [Driveway Info-Site](https://www.moretonbay.qld.gov.au/Services/Building-Development/Building/Residential-Driveway)
- DRIVEWAY — [RS-049](https://www.moretonbay.qld.gov.au/files/assets/public/v/2/services/building-development/standard-drawings/standard-drawing-rs-049.pdf) — Low Density Vehicle Crossing 1/2
- DRIVEWAY — [RS-050](https://www.moretonbay.qld.gov.au/files/assets/public/v/2/services/building-development/standard-drawings/standard-drawing-rs-050.pdf) — Low Density Vehicle Crossing 2/2
- DRIVEWAY — [RS-056](https://www.moretonbay.qld.gov.au/files/assets/public/v/1/services/building-development/standard-drawings/standard-drawing-rs-056.pdf) — Rural Vehicle Crossing
- STORMWATER — [SW Fact sheet](https://www.moretonbay.qld.gov.au/files/assets/public/v/1/services/building-development/building-plumbing/stormwater-for-domestic-properties-fact-sheet.pdf) — SW & Rubble Pits for Domestic Buildings
- POOL — [Pool Backwash Fact Sheet](https://www.moretonbay.qld.gov.au/files/assets/public/v/1/services/building-development/building-plumbing/pool-backwash-in-unsewered-areas-fact-sheet.pdf) — Detail of pool backwash discharge pit in non-sewered areas
- POOL — [Pool Backwash Fact Sheet 2](https://www.moretonbay.qld.gov.au/files/assets/public/v/1/services/building-development/building-plumbing/pool-backwash-in-sewered-areas-fact-sheet.pdf) — Detail of pool backwash connection in sewered areas

---

## Noosa Shire Council (NSC)

- WEBSITE — [Council Website](https://www.noosa.qld.gov.au/)
- MAP — [Interactive Mapping](https://noo.spatial.t1cloud.com/spatial/intramaps/?project=Public&module=Noosa%20Plan%202020&configId=64251f07-9411-4a61-930e-2bd9b45d8fff&startToken=bb111758-3a9c-4e51-9f54-a20dc272b2ab)
- PLAN — [Dwelling Fact Sheet](https://www.noosa.qld.gov.au/downloads/file/4138/fact-sheet-2-dwelling-house)
- PLAN — [Planning Scheme (Full)](https://noo-prod-icon.saas.t1cloud.com/Pages/Plan/Book.aspx?exhibit=Current)
- PLAN — [Low Dens. House Code](https://noo-prod-icon.saas.t1cloud.com/Pages/Plan/Book.aspx?exhibit=Current)
- STANDARD — [Standard Drawings](https://www.noosa.qld.gov.au/planning-development/development-tools-guidelines/standard-drawings)
- DRIVEWAY — [Driveway Fact Sheet](https://www.noosa.qld.gov.au/downloads/file/3537/vehicle-crossover-fact-sheet-pack)
- DRIVEWAY — [RS-049 Driveway 1 of 2](https://www.noosa.qld.gov.au/downloads/file/1722/sd-roads-rs-049)
- DRIVEWAY — [RS-050 Driveway 2 of 2](https://www.noosa.qld.gov.au/downloads/file/1731/sd-roads-rs-050)
- DRIVEWAY — [RS-056 Rural Driveway](https://www.noosa.qld.gov.au/downloads/file/1726/sd-roads-rs-056)
- DRIVEWAY — [RS-056.1 Rural Driveway Alt.](https://www.noosa.qld.gov.au/downloads/file/2151/sd-roads-rs056-and-rs056-1-concrete-alternative)
- DRIVEWAY — [RS-80 Kerb Profiles](https://www.noosa.qld.gov.au/downloads/file/1734/ipwea-rs-080)
- STORMWATER — [Stormwater Guidelines](https://www.noosa.qld.gov.au/downloads/file/1478/stormwater-guidelines)
- TIPS — [Coastal Hazards](https://www.noosa.qld.gov.au/planning-development/the-noosa-plan/coastal-hazards-mapping)
- TIPS — [Pools & Spas](https://www.noosa.qld.gov.au/downloads/file/1487/swimming-pools-and-spas-information-sheet)
- TIPS — [QCoast2100 Guide](https://www.qcoast2100.com.au/downloads/file/55/minimum-standards-and-guideline)

---

## Redland City Council (RCC)

- WEBSITE — [Council Website](https://www.redland.qld.gov.au/)
- MAP — [Development.i Interactive Mapping](https://developmenti.redland.qld.gov.au/)
- MAP — [eMap](https://redlandcity.maps.arcgis.com/apps/webappviewer/index.html?id=b3e7c450b99c4aa281ce24a9c747728f)
- MAP — [Flood Mapping](https://www.redland.qld.gov.au/info/20016/planning_building_and_development/1225/creek_flood_mapping)
- PLAN — [Planning Scheme (Full)](https://www.redland.qld.gov.au/info/20292/redland_city_plan/914/redland_city_plan_documents)
- PLAN — [Planning Scheme Document](https://www.redland.qld.gov.au/download/downloads/id/6124/redland_city_plan_-_version_12.pdf)
- PLAN — [Storm Tide Map 1 of 2](https://www.redland.qld.gov.au/download/downloads/id/2983/overlay_map_flood_prone_ml_om-011.pdf)
- PLAN — [Storm Tide Map 2 of 2](https://www.redland.qld.gov.au/download/downloads/id/2979/overlay_map_flood_prone_isl_om-012.pdf)
- STANDARDS — [BOI/BOS/BOA](https://www.redland.qld.gov.au/download/downloads/id/3005/fact_sheet_-_build_over_or_near_relevant_infrastructure.pdf)
- DRIVEWAY — [R-RCC-1 Driveway Crossover](https://www.redland.qld.gov.au/download/downloads/id/3085/reference_drawing_r-rcc-1_-_domestic_driveway_crossover_for_kerb_and_channel.pdf)
- DRIVEWAY — [R-RCC-1 Driveway Wing Drawings](https://www.redland.qld.gov.au/download/downloads/id/3083/reference_drawing_-_domestic_driveway_wing_drawing.pdf)
- DRIVEWAY — [R-RCC-17 Driveway with swale](https://www.redland.qld.gov.au/download/downloads/id/3086/reference_drawing_r-rsc-17_-_domestic_driveway_crossover_for_drainage_swale_type_a_streets_only.pdf)
- DRIVEWAY — [RS-056 Driveway Rural](https://www.redland.qld.gov.au/download/downloads/id/3261/ipwea_standard_drawing_rs-056_-_rural_driveways_pipe_crossings.pdf)
- STORMWATER — [Stormwater Fact Sheet](https://www.redland.qld.gov.au/download/downloads/id/2878/stormwater_and_roofwater_drainage_fact_sheet.pdf) — Rubble pit yes, no spec provided. May req. Hydraulics
- TIPS — [Multi Dwelling Design Guide](https://www.redland.qld.gov.au/download/downloads/id/3030/multiple_dwelling_design_guide.pdf)
- TIPS — [Multi Dwelling Fact Sheet](https://www.redland.qld.gov.au/download/downloads/id/3012/fact_sheet_-_multiple_dwelling_design_guide.pdf)
- TIPS — [Res Zoning Overview](https://www.redland.qld.gov.au/download/downloads/id/3001/fact_sheet_-_residential_zones.pdf)
- TIPS — [Storm Tide Information Page](https://www.redland.qld.gov.au/info/20292/redland_city_plan/915/storm_tide_mapping_information)

---

## Scenic Rim Regional Council (SRRC)

- WEBSITE — [Council Website](https://www.somerset.qld.gov.au/)
- MAP — [eServices Mapping](https://eservices.somerset.qld.gov.au/mapping.aspx)
- MAP — [Property Enquiry](https://www.somerset.qld.gov.au/our-services/property-enquiry)
- SCHEME — [SRC Planning Scheme](https://www.somerset.qld.gov.au/downloads/file/2526/somerset-region-planning-scheme-version-4-2)
- DRIVEWAY — [SRC-ROAD-012](https://www.somerset.qld.gov.au/downloads/file/736/src-road-012-residential-driveway-invert-and-slab-or-tracks) — RESIDENTIAL DRIVEWAY INVERT AND SLAB OR TRACKS
- DRIVEWAY — [SRC-ROAD-015 No Kerb](https://www.somerset.qld.gov.au/downloads/file/739/src-road-015b-driveway-invert-crossing-for-areas-without-kerb-and-channel) — RESIDENTIAL DRIVEWAY INVERT CROSSING NO KERB
- DRIVEWAY — [SRC-ROAD-016 Rural with Culvert](https://www.somerset.qld.gov.au/downloads/file/740/src-road-016b-rural-road-driveway-with-pipe-crossing)
- STORMWATER — [Standard Roofwater Outlets](https://www.somerset.qld.gov.au/downloads/file/741/src-road-017-kerb-and-channel-roofwater-kerb-adapter-detail)
- TIPS — [Dual Occupancy Fact Sheet](https://www.scenicrim.qld.gov.au/downloads/file/6073/dual-occupancy-30june2023)
- TIPS — [Dwelling house and Secondary Dwelling Fact Sheet](https://www.scenicrim.qld.gov.au/downloads/file/6078/dwelling-houses-and-secondary-dwellings-30june2023)
- TIPS — [Sheds (Class 10a)](https://www.scenicrim.qld.gov.au/downloads/file/6074/domestic-shed-class-1a-structure-30june2023)

---

## Somerset Regional Council (SRC)

- WEBSITE — [Council Website](https://www.somerset.qld.gov.au/)
- MAP — [eServices Mapping](https://eservices.somerset.qld.gov.au/mapping.aspx)
- MAP — [Property Enquiry](https://www.somerset.qld.gov.au/our-services/property-enquiry)
- SCHEME — [SRC Planning Scheme](https://www.somerset.qld.gov.au/downloads/file/2526/somerset-region-planning-scheme-version-4-2)
- DRIVEWAY — [SRC-ROAD-012](https://www.somerset.qld.gov.au/downloads/file/736/src-road-012-residential-driveway-invert-and-slab-or-tracks) — RESIDENTIAL DRIVEWAY INVERT AND SLAB OR TRACKS
- DRIVEWAY — [SRC-ROAD-015 No Kerb](https://www.somerset.qld.gov.au/downloads/file/739/src-road-015b-driveway-invert-crossing-for-areas-without-kerb-and-channel) — RESIDENTIAL DRIVEWAY INVERT CROSSING NO KERB
- DRIVEWAY — [SRC-ROAD-016 Rural with Culvert](https://www.somerset.qld.gov.au/downloads/file/740/src-road-016b-rural-road-driveway-with-pipe-crossing)
- STORMWATER — [No ref. to Rubble Pit](#) — Unable to find reference to rubble pit.
- STORMWATER — [Standard Roofwater Outlets](https://www.somerset.qld.gov.au/downloads/file/741/src-road-017-kerb-and-channel-roofwater-kerb-adapter-detail)

---

## Sunshine Coast Council (SCC)

- WEBSITE — [Council Website](https://www.sunshinecoast.qld.gov.au/development)
- MAP — [Development.i Interactive Mapping](https://developmenti.sunshinecoast.qld.gov.au/Home/) — PD Online for Sunshine Coast
- MAP — [Flood Mapping](https://scrc.maps.arcgis.com/apps/webappviewer/index.html?id=c4259d59fa3e41d38eb5b739020bc2b0&utm_source=sunshine%2Bcoast%2Bcouncil&utm_medium=website) — Note: you should get new flood maps from Development.i Site Report
- PLAN — [Development codes (All)](https://www.sunshinecoast.qld.gov.au/development/planning-documents/sunshine-coast-planning-scheme-2014/view-the-sunshine-coast-planning-scheme-2014-text/part-9-development-codes)
- PLAN — [Dual Occupancy Code](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/Record/22407390/File/document)
- PLAN — [Dwelling House Code](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/Record/22407391/File/document)
- STANDARDS — [Standard details & drawings](https://www.sunshinecoast.qld.gov.au/development/development-tools-and-guidelines/infrastructure-guidelines-and-standards/standard-engineering-drawings/standard-drawings-index-roads-streets)
- DRIVEWAY — [Crossover Checklist](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/RecordHtml/20057629) — Provides offsets for assets
- DRIVEWAY — [Driveway Fact Sheet](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/RecordHtml/20057632)
- DRIVEWAY — [Driveway Fact Sheet 2](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/RecordHtml/20057630)
- DRIVEWAY — [RS-049](https://assets-au-scc.kc-usercontent.com/330b87ea-148b-3ecf-9857-698f2086fe8d/94d72e1f-412f-41ba-acb6-99b79cefe2ae/26D80B2C-F429-4055-B61B-6110FFA16B22?utm_source=sunshine%2Bcoast%2Bcouncil&utm_medium=website)
- DRIVEWAY — [RS-056](https://assets-au-scc.kc-usercontent.com/330b87ea-148b-3ecf-9857-698f2086fe8d/d13d565e-7ffa-4437-b0d4-79ee7aa41661/84C6CFDF-5D95-4A72-8F2E-FF25E26124A2?utm_source=sunshine%2Bcoast%2Bcouncil&utm_medium=website) — Rural Crossovers
- STORMWATER — [Stormwater Fact Sheet](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/RecordHtml/20056342) — Mentions points of discharge and rubble pits
- TIPS — [Dual occupancy fact sheet](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/Record/21571396/File/document)
- TIPS — [Plannig shceme area](https://assets-au-scc.kc-usercontent.com/330b87ea-148b-3ecf-9857-698f2086fe8d/ec4dd18c-d7f2-4a2b-8bf7-ba3159f9049b/1DDC7A96-30E8-4D0E-A330-9CE4D423D950?utm_source=sunshine%2Bcoast%2Bcouncil&utm_medium=website)
- TIPS — [Secondary dwelling fact sheet](https://publicdocs.scc.qld.gov.au/hpecmwebdrawer/Record/21571402/File/document)
- TIPS — [Shed Fact Sheet](https://www.sunshinecoast.qld.gov.au/development/building/sheds)

---
'''

# --- Helper to parse planning-scheme-documents.md ---
def parse_planning_scheme_markdown(md_text):
    schemes = {}
    current_scheme = None
    # Updated regex to match '- TYPE — [Name](url) — Desc'
    link_pattern = re.compile(r"^- ([A-Z ]+) — \[(.*?)\]\((.*?)\)(?: — (.*))?")
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith('## '):
            current_scheme = line[3:].strip()
            schemes[current_scheme] = []
        elif line.startswith('- ') and current_scheme:
            m = link_pattern.match(line)
            if m:
                doc_type, name, url, desc = m.group(1), m.group(2), m.group(3), m.group(4) or ''
                # Optionally, show type in the name, or keep as a separate field
                schemes[current_scheme].append((f"{doc_type} — {name}", url, desc))
    return schemes

# --- Main Application Class ---
class CDCSiteToolsApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CDC Site Tools - Archicad Automation")
        self.master.geometry("900x700")
        # Parse planning scheme markdown for council schemes and links
        self.scheme_links_by_council = self.load_planning_scheme_links()
        self.md_schemes = parse_planning_scheme_markdown(PLANNING_SCHEME_MD_TEXT)
        self.md_scheme_names = sorted(self.md_schemes.keys())
        self.setup_ui()

    def load_planning_scheme_links(self):
        links = {}
        self.council_display_to_code = {}
        try:
            with open(PLANNING_SCHEME_CSV, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    council_code = row['CODE'].strip()
                    # Remove numeric prefix for display
                    if '.' in council_code:
                        display = council_code.split('.', 1)[1].strip()
                    else:
                        display = council_code
                    name = row['Document Name'].strip()
                    url = row['URL'].strip()
                    desc = row['Full Description'].strip()
                    if not url:
                        continue
                    if council_code not in links:
                        links[council_code] = []
                    links[council_code].append((name, url, desc))
                    # Only add to display map if not QDC/NOTES/Mapping
                    if ('QDC' not in council_code and 'NOTES' not in council_code and 'Mapping' not in council_code):
                        self.council_display_to_code[display] = council_code
        except Exception as e:
            print(f"Error loading planning scheme CSV: {e}")
        # Sort council display names alphabetically
        self.sorted_council_names = sorted(self.council_display_to_code.keys())
        return links

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True)
        self.setup_boundary_tool_tab()
        version_label = ttk.Label(self.master, text=f"CDC Site Tools v{__version__}", anchor='e')
        version_label.pack(side='bottom', fill='x', padx=5, pady=2)

    # --- Boundary Tool Tab ---
    def setup_boundary_tool_tab(self):
        self.boundary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.boundary_tab, text="Boundary Tool")

        # Planning Scheme Preset Dropdown
        preset_frame = ttk.Frame(self.boundary_tab)
        preset_frame.pack(fill='x', pady=5)
        ttk.Label(preset_frame, text="Planning Scheme:").pack(side='left', padx=5)
        self.preset_var = tk.StringVar(value="QDC MP1.1")
        # Combine QDC presets and markdown schemes
        self.qdc_presets = list(PLANNING_SCHEME_PRESETS.keys())
        self.all_presets = self.qdc_presets + self.md_scheme_names
        preset_menu = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=self.all_presets,
            state="readonly"
        )
        preset_menu.pack(side='left', padx=5)
        preset_menu.bind('<<ComboboxSelected>>', self.on_preset_selected)
        preset_menu.bind('<<ComboboxSelected>>', self.update_scheme_urls)

        # Setback Fields
        setback_frame = ttk.LabelFrame(self.boundary_tab, text="Setbacks (meters)")
        setback_frame.pack(fill='x', padx=10, pady=5)
        self.setback_vars = {}
        # Standard setbacks
        for i, key in enumerate(["front", "side", "rear", "secondary"]):
            ttk.Label(setback_frame, text=f"{key.title()} Setback:").grid(row=0, column=i*2, sticky='e', padx=5)
            var = tk.DoubleVar(value=PLANNING_SCHEME_PRESETS[self.preset_var.get()][key])
            self.setback_vars[key] = var
            ttk.Entry(setback_frame, textvariable=var, width=6).grid(row=0, column=i*2+1, padx=2)
        # New: Front minimum, habitable, garage
        ttk.Label(setback_frame, text="Front Setback (Min):").grid(row=1, column=0, sticky='e', padx=5)
        self.setback_vars['front_min'] = tk.DoubleVar(value=PLANNING_SCHEME_PRESETS[self.preset_var.get()].get('front_min', 3.0))
        ttk.Entry(setback_frame, textvariable=self.setback_vars['front_min'], width=6).grid(row=1, column=1, padx=2)
        ttk.Label(setback_frame, text="Front Setback (Habitable):").grid(row=1, column=2, sticky='e', padx=5)
        self.setback_vars['front_hab'] = tk.DoubleVar(value=PLANNING_SCHEME_PRESETS[self.preset_var.get()].get('front_hab', 3.45))
        ttk.Entry(setback_frame, textvariable=self.setback_vars['front_hab'], width=6).grid(row=1, column=3, padx=2)
        ttk.Label(setback_frame, text="Garage Setback:").grid(row=1, column=4, sticky='e', padx=5)
        self.setback_vars['garage'] = tk.DoubleVar(value=PLANNING_SCHEME_PRESETS[self.preset_var.get()].get('garage', 3.0))
        ttk.Entry(setback_frame, textvariable=self.setback_vars['garage'], width=6).grid(row=1, column=5, padx=2)

        # Chain Link Conversion
        self.chain_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.boundary_tab, text="Convert from Chain Links (1 chain = 20.1168m)", variable=self.chain_var).pack(anchor='w', padx=10, pady=2)

        # Site Preset Dropdown (move here, above boundary data table)
        site_preset_frame = ttk.Frame(self.boundary_tab)
        site_preset_frame.pack(fill='x', padx=10, pady=2)
        ttk.Label(site_preset_frame, text="Site Preset:").pack(side='left', padx=2)
        self.site_preset_var = tk.StringVar(value=list(SITE_RECTANGLE_PRESETS.keys())[0])
        site_preset_menu = ttk.Combobox(site_preset_frame, textvariable=self.site_preset_var, values=list(SITE_RECTANGLE_PRESETS.keys()), state="readonly", width=28)
        site_preset_menu.pack(side='left', padx=2)
        ttk.Button(site_preset_frame, text="Apply Site Preset", command=self.apply_site_preset).pack(side='left', padx=2)

        # --- Horizontal Frame for Boundary Data and Planning Scheme Documents ---
        horz_frame = ttk.Frame(self.boundary_tab)
        horz_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Boundary Data Table (7 rows by default)
        boundary_data_frame = ttk.LabelFrame(horz_frame, text="Boundary Data (Type, Distance, Bearing, Flip 180°)")
        boundary_data_frame.pack(side='left', fill='y', expand=False, padx=(0, 10))
        self.boundary_rows = []
        self.boundary_table = tk.Frame(boundary_data_frame)
        self.boundary_table.pack(fill='x')
        for _ in range(7):
            self.add_boundary_row()
        add_row_btn = ttk.Button(boundary_data_frame, text="+ Add Row", command=self.add_boundary_row)
        add_row_btn.pack(anchor='w', pady=2)

        # Planning Scheme Documents (right side, in a scrolled text widget)
        docs_frame = ttk.LabelFrame(horz_frame, text="Planning Scheme Documents")
        docs_frame.pack(side='left', fill='both', expand=True)
        self.scheme_docs_text = scrolledtext.ScrolledText(docs_frame, height=16, wrap='word', state='normal')
        self.scheme_docs_text.pack(fill='both', expand=True, padx=2, pady=2)
        self.scheme_docs_text.config(state='disabled')
        self.update_scheme_urls()

        # Draw/Action Buttons
        action_frame = ttk.Frame(self.boundary_tab)
        action_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(action_frame, text="Draw Boundaries and Setbacks", command=self.draw_boundaries_and_setbacks).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Clear All", command=self.clear_all).pack(side='left', padx=5)

        # Results Display
        self.results_text = scrolledtext.ScrolledText(self.boundary_tab, height=8)
        self.results_text.pack(fill='both', expand=True, padx=10, pady=5)

    def on_preset_selected(self, event=None):
        preset = self.preset_var.get()
        if preset in PLANNING_SCHEME_PRESETS:
            for key in self.setback_vars:
                if key in PLANNING_SCHEME_PRESETS[preset]:
                    self.setback_vars[key].set(PLANNING_SCHEME_PRESETS[preset][key])
        else:
            # Set all offsets to 0 for council schemes
            for key in self.setback_vars:
                self.setback_vars[key].set(0)

    def add_boundary_row(self):
        row = len(self.boundary_rows)
        row_vars = {
            'type': tk.StringVar(value='Side'),
            'bearing': tk.StringVar(value=''),
            'distance': tk.DoubleVar(value=0.0),
            'flip': tk.BooleanVar(value=False)
        }
        frame = tk.Frame(self.boundary_table)
        frame.grid(row=row, column=0, sticky='ew')
        ttk.Combobox(frame, textvariable=row_vars['type'], values=['Side', 'Rear', 'Frontage', 'Secondary'], width=8, state='readonly').grid(row=0, column=0)
        ttk.Entry(frame, textvariable=row_vars['distance'], width=8).grid(row=0, column=1)
        ttk.Entry(frame, textvariable=row_vars['bearing'], width=12).grid(row=0, column=2)
        ttk.Checkbutton(frame, variable=row_vars['flip']).grid(row=0, column=3)
        self.boundary_rows.append(row_vars)

    def clear_all(self):
        for widget in self.boundary_table.winfo_children():
            widget.destroy()
        self.boundary_rows.clear()
        for _ in range(7):
            self.add_boundary_row()
        self.results_text.delete(1.0, tk.END)

    def draw_boundaries_and_setbacks(self):
        # Collect boundary segments and types (clockwise order)
        segments = []
        x, y = 0.0, 0.0
        for idx, row in enumerate(self.boundary_rows):
            try:
                bearing = row['bearing'].get().strip()
                distance = row['distance'].get()
                btype = row['type'].get().lower()
                flip = row['flip'].get()
                # Validate distance
                if isinstance(distance, float):
                    if distance <= 0:
                        continue
                else:
                    self.results_text.insert(tk.END, f"Row {idx+1}: Distance is not a valid number.\n")
                    continue
                if self.chain_var.get():
                    distance *= 20.1168
                if not bearing:
                    continue
                # Parse bearing
                parts = bearing.split()
                if len(parts) == 3:
                    try:
                        deg, mins, secs = map(float, parts)
                    except Exception:
                        self.results_text.insert(tk.END, f"Row {idx+1}: Bearing parts must be numbers: '{bearing}'\n")
                        continue
                    theta = deg + mins/60 + secs/3600
                elif len(parts) == 1:
                    try:
                        theta = float(parts[0])
                    except Exception:
                        self.results_text.insert(tk.END, f"Row {idx+1}: Bearing must be a number or 3-part D M S: '{bearing}'\n")
                        continue
                else:
                    self.results_text.insert(tk.END, f"Row {idx+1}: Invalid bearing format: '{bearing}'\n")
                    continue
                if flip:
                    theta = (theta + 180) % 360
                theta_rad = math.radians(theta)
                dx = distance * math.sin(theta_rad)
                dy = distance * math.cos(theta_rad)
                x2 = x + dx
                y2 = y + dy
                segments.append({
                    'type': btype, 'start': (x, y), 'end': (x2, y2), 'idx': idx, 'distance': distance, 'bearing': theta
                })
                x, y = x2, y2
            except Exception as e:
                self.results_text.insert(tk.END, f"Row {idx+1}: Unexpected error: {e}\n")
        if len(segments) < 1:
            self.results_text.insert(tk.END, "Not enough segments to draw boundaries.\n")
            return
        # Draw each boundary segment as its own polyline
        for seg in segments:
            start = seg['start']
            end = seg['end']
            # Skip zero-length or invalid segments
            if (start[0] == end[0] and start[1] == end[1]):
                self.results_text.insert(tk.END, f"Skipping zero-length segment {seg['idx']+1}.\n")
                continue
            polyline_data = {
                'coordinates': [
                    {'x': start[0], 'y': start[1]},
                    {'x': end[0], 'y': end[1]}
                ]
            }
            self.results_text.insert(tk.END, f"Sending boundary polyline data: {polyline_data}\n")
            resp = aclib.RunTapirCommand('CreatePolylines', {
                'polylinesData': [polyline_data]
            })
            self.results_text.insert(tk.END, f"Boundary segment {seg['idx']+1} created. Response: {resp}\n")
        # If last segment's end does not match first segment's start, draw a closing polyline
        if len(segments) > 1:
            first_start = segments[0]['start']
            last_end = segments[-1]['end']
            tol = 1e-6
            if abs(first_start[0] - last_end[0]) > tol or abs(first_start[1] - last_end[1]) > tol:
                closing_data = {
                    'coordinates': [
                        {'x': last_end[0], 'y': last_end[1]},
                        {'x': first_start[0], 'y': first_start[1]}
                    ]
                }
                self.results_text.insert(tk.END, f"Sending closing polyline data: {closing_data}\n")
                resp = aclib.RunTapirCommand('CreatePolylines', {
                    'polylinesData': [closing_data]
                })
                self.results_text.insert(tk.END, f"Closing polyline created from last end to first start. Response: {resp}\n")
        # Now, for each segment, create offset setback and text as before
        try:
            for seg in segments:
                btype = seg['type']
                start = seg['start']
                end = seg['end']
                # Get setback distance for this type
                if btype == 'frontage' or btype == 'front':
                    # Draw all three front setbacks for frontage
                    for fkey, label in zip(['front_min', 'front_hab', 'garage'], ['Front Min', 'Front Habitable', 'Garage']):
                        offset = -abs(self.setback_vars[fkey].get())
                        dx = end[0] - start[0]
                        dy = end[1] - start[1]
                        length = math.hypot(dx, dy)
                        if length == 0:
                            self.results_text.insert(tk.END, f"Skipping zero-length setback for segment {seg['idx']+1} ({label}).\n")
                            continue
                        nx = -dy / length
                        ny = dx / length
                        offset_start = (start[0] + offset * nx, start[1] + offset * ny)
                        offset_end = (end[0] + offset * nx, end[1] + offset * ny)
                        setback_data = {
                            'coordinates': [
                                {'x': offset_start[0], 'y': offset_start[1]},
                                {'x': offset_end[0], 'y': offset_end[1]}
                            ]
                        }
                        self.results_text.insert(tk.END, f"Sending {label} setback polyline data: {setback_data}\n")
                        resp_setback = aclib.RunTapirCommand('CreatePolylines', {
                            'polylinesData': [setback_data]
                        })
                        self.results_text.insert(tk.END, f"{label} setback line created. Response: {resp_setback}\n")
                    # Road line logic (as before, for front/secondary)
                    road_offset = 4.25
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    length = math.hypot(dx, dy)
                    nx = -dy / length
                    ny = dx / length
                    road_start = (start[0] + road_offset * nx, start[1] + road_offset * ny)
                    road_end = (end[0] + road_offset * nx, end[1] + road_offset * ny)
                    road_data = {
                        'coordinates': [
                            {'x': road_start[0], 'y': road_start[1]},
                            {'x': road_end[0], 'y': road_end[1]}
                        ]
                    }
                    self.results_text.insert(tk.END, f"Sending road polyline data: {road_data}\n")
                    resp_road = aclib.RunTapirCommand('CreatePolylines', {
                        'polylinesData': [road_data]
                    })
                    self.results_text.insert(tk.END, f"Frontage road line created at 4.25m outward. Response: {resp_road}\n")
                elif btype == 'secondary':
                    key = 'secondary'
                    offset = -abs(self.setback_vars[key].get()) if key in self.setback_vars else 0.0
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    length = math.hypot(dx, dy)
                    if length == 0:
                        self.results_text.insert(tk.END, f"Skipping zero-length setback for segment {seg['idx']+1}.\n")
                        continue
                    nx = -dy / length
                    ny = dx / length
                    offset_start = (start[0] + offset * nx, start[1] + offset * ny)
                    offset_end = (end[0] + offset * nx, end[1] + offset * ny)
                    setback_data = {
                        'coordinates': [
                            {'x': offset_start[0], 'y': offset_start[1]},
                            {'x': offset_end[0], 'y': offset_end[1]}
                        ]
                    }
                    self.results_text.insert(tk.END, f"Sending setback polyline data: {setback_data}\n")
                    resp_setback = aclib.RunTapirCommand('CreatePolylines', {
                        'polylinesData': [setback_data]
                    })
                    self.results_text.insert(tk.END, f"Secondary setback line created. Response: {resp_setback}\n")
                    # Road line for secondary
                    road_offset = 4.25
                    nx = -dy / length
                    ny = dx / length
                    road_start = (start[0] + road_offset * nx, start[1] + road_offset * ny)
                    road_end = (end[0] + road_offset * nx, end[1] + road_offset * ny)
                    road_data = {
                        'coordinates': [
                            {'x': road_start[0], 'y': road_start[1]},
                            {'x': road_end[0], 'y': road_end[1]}
                        ]
                    }
                    self.results_text.insert(tk.END, f"Sending road polyline data: {road_data}\n")
                    resp_road = aclib.RunTapirCommand('CreatePolylines', {
                        'polylinesData': [road_data]
                    })
                    self.results_text.insert(tk.END, f"Secondary road line created at 4.25m outward. Response: {resp_road}\n")
                else:
                    key = btype
                    offset = -abs(self.setback_vars[key].get()) if key in self.setback_vars else 0.0
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    length = math.hypot(dx, dy)
                    if length == 0:
                        self.results_text.insert(tk.END, f"Skipping zero-length setback for segment {seg['idx']+1}.\n")
                        continue
                    nx = -dy / length
                    ny = dx / length
                    offset_start = (start[0] + offset * nx, start[1] + offset * ny)
                    offset_end = (end[0] + offset * nx, end[1] + offset * ny)
                    setback_data = {
                        'coordinates': [
                            {'x': offset_start[0], 'y': offset_start[1]},
                            {'x': offset_end[0], 'y': offset_end[1]}
                        ]
                    }
                    self.results_text.insert(tk.END, f"Sending setback polyline data: {setback_data}\n")
                    resp_setback = aclib.RunTapirCommand('CreatePolylines', {
                        'polylinesData': [setback_data]
                    })
                    self.results_text.insert(tk.END, f"{key.title()} setback line created. Response: {resp_setback}\n")
                # Text label creation not supported
                self.results_text.insert(tk.END, f"Text label not created: Tapir/Archicad API does not support text creation.\n")
        except Exception as e:
            self.results_text.insert(tk.END, f"Archicad error: {e}\n")

    def apply_site_preset(self):
        # Fill the boundary table with the selected site preset
        preset = self.site_preset_var.get()
        if preset not in SITE_RECTANGLE_PRESETS:
            self.results_text.insert(tk.END, f"Preset '{preset}' not found.\n")
            return
        width, depth = SITE_RECTANGLE_PRESETS[preset]
        # Clear and fill as rectangle: Side, Rear, Side, Frontage (clockwise, start with side to the left)
        for widget in self.boundary_table.winfo_children():
            widget.destroy()
        self.boundary_rows.clear()
        # Side (depth, 270°)
        self.add_boundary_row()
        self.boundary_rows[-1]['type'].set('Side')
        self.boundary_rows[-1]['distance'].set(depth)
        self.boundary_rows[-1]['bearing'].set('270')
        # Rear (width, 0°)
        self.add_boundary_row()
        self.boundary_rows[-1]['type'].set('Rear')
        self.boundary_rows[-1]['distance'].set(width)
        self.boundary_rows[-1]['bearing'].set('0')
        # Side (depth, 90°)
        self.add_boundary_row()
        self.boundary_rows[-1]['type'].set('Side')
        self.boundary_rows[-1]['distance'].set(depth)
        self.boundary_rows[-1]['bearing'].set('90')
        # Frontage (width, 180°)
        self.add_boundary_row()
        self.boundary_rows[-1]['type'].set('Frontage')
        self.boundary_rows[-1]['distance'].set(width)
        self.boundary_rows[-1]['bearing'].set('180')
        # Fill up to 7 rows
        for _ in range(3):
            self.add_boundary_row()
        self.results_text.insert(tk.END, f"Applied site preset: {preset} ({width} x {depth})\n")

    def update_scheme_urls(self, event=None):
        # Clear the text widget
        self.scheme_docs_text.config(state='normal')
        self.scheme_docs_text.delete('1.0', tk.END)
        scheme = self.preset_var.get()
        # QDC schemes: show a default set (e.g. QLD Mapping)
        if scheme in PLANNING_SCHEME_PRESETS:
            council_code = '01. QLD Mapping'
            links = self.scheme_links_by_council.get(council_code, [])
        else:
            # Use markdown schemes
            links = self.md_schemes.get(scheme, [])
        if not links:
            self.scheme_docs_text.insert(tk.END, "No documents found.\n")
            self.scheme_docs_text.config(state='disabled')
            return
        # Insert each link and description on one line, make links clickable
        self.scheme_docs_text.tag_configure('link', foreground='blue', underline=True)
        self.scheme_docs_text.tag_configure('desc', foreground='#555', font=(None, 8))
        for idx, (name, url, desc) in enumerate(links):
            start_idx = self.scheme_docs_text.index(tk.END)
            self.scheme_docs_text.insert(tk.END, name, ('link', f'link{idx}'))
            if desc:
                self.scheme_docs_text.insert(tk.END, f"  {desc}", 'desc')
            self.scheme_docs_text.insert(tk.END, "\n")
            # Bind link click
            def callback(event, u=url):
                import webbrowser
                webbrowser.open(u)
            self.scheme_docs_text.tag_bind(f'link{idx}', '<Button-1>', callback)
        self.scheme_docs_text.config(state='disabled')

# --- Main Entrypoint ---
def main():
    root = tk.Tk()
    app = CDCSiteToolsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
