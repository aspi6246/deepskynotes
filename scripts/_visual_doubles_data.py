"""Shared pair data for the Visual Double Open Clusters observing list.

Keep this in sync with observing-lists/visual-double-open-clusters.html.
When a pair is added or edited on the site, mirror the change here so
the PDF / Excel downloads and the fetched thumbnails stay in step.
"""

# Each pair is a dict with:
#   slug       - filename-safe id, used for the thumbnail JPEG name
#   pair       - (name_a, name_b)
#   const      - constellation (full name)
#   coords_a   - (ra_deg, dec_deg) in decimal degrees, J2000
#   coords_b   - (ra_deg, dec_deg)
#   ra_hms_a   - human RA "16h 27.8m" (as shown in the article)
#   dec_dms_a  - human Dec "-49 09'" (unicode minus/prime rendered elsewhere)
#   ra_hms_b, dec_dms_b - same for cluster B
#   mag_a, mag_b - V magnitude, or None if none catalogued
#   catalogue_slug_a, catalogue_slug_b - filename in catalogue/objects/ (None if no page)
#   thumb_fov_deg - FOV to request from DSS, in degrees
#   thumb_center - (ra_deg, dec_deg) midpoint used for the DSS pull
#   note - single-paragraph observing note (plain text; downloads use as-is)

PAIRS = [
    {
        "slug": "ngc-3572-ngc-3590",
        "pair": ("NGC 3572", "NGC 3590"),
        "const": "Carina",
        "coords_a": (167.603, -60.252),
        "coords_b": (168.253, -60.792),
        "ra_hms_a": "11h 10.4m", "dec_dms_a": "-60° 15'",
        "ra_hms_b": "11h 13.0m", "dec_dms_b": "-60° 47'",
        "mag_a": 6.6, "mag_b": 8.2,
        "catalogue_slug_a": "ngc-3572", "catalogue_slug_b": "ngc-3590",
        "thumb_fov_deg": 1.5,
        "thumb_center": (167.928, -60.522),
        "note": (
            "In the 35 mm Panoptic both clusters share the field with a "
            "loose clump of stars between them - the impression is of "
            "three interacting clusters, and it is genuinely hard to "
            "tell where one ends and the next begins. Two bright patches "
            "of nebulosity (NGC 3579/3603) sit in the same view. (Apr 2026)"
        ),
    },
    {
        "slug": "ic-2714-mel-105",
        "pair": ("IC 2714", "Mel 105"),
        "const": "Carina",
        "coords_a": (169.370, -62.738),
        "coords_b": (169.933, -63.488),
        "ra_hms_a": "11h 17.5m", "dec_dms_a": "-62° 44'",
        "ra_hms_b": "11h 19.7m", "dec_dms_b": "-63° 29'",
        "mag_a": 8.2, "mag_b": 8.5,
        "catalogue_slug_a": "ic-2714", "catalogue_slug_b": "mel-105",
        "thumb_fov_deg": 1.5,
        "thumb_center": (169.652, -63.113),
        "note": (
            "Halfway along the line from IC 2602 to lambda Centauri. In "
            "the 35 mm Panoptic both clusters fit in the same field for "
            "a lovely contrast: IC 2714 a large, relatively dense disk "
            "of 60+ stars spread across ~15', Mel 105 packed into just "
            "~5' with only a few members resolved at low power. "
            "Highlighted as a pair by O'Meara in "
            "'Deep-Sky Companions: Southern Gems'. (Apr 2026)"
        ),
    },
    {
        "slug": "ic-2602-mel-101",
        "pair": ("IC 2602", "Mel 101"),
        "const": "Carina",
        "coords_a": (160.749, -64.405),
        "coords_b": (160.557, -65.105),
        "ra_hms_a": "10h 43.0m", "dec_dms_a": "-64° 24'",
        "ra_hms_b": "10h 42.2m", "dec_dms_b": "-65° 06'",
        "mag_a": 1.9, "mag_b": 8.0,
        "catalogue_slug_a": "ic-2602", "catalogue_slug_b": "mel-101",
        "thumb_fov_deg": 2.5,
        "thumb_center": (160.653, -64.755),
        "note": (
            "A slightly asymmetric pair. IC 2602 (the Southern Pleiades) "
            "is too large for any eyepiece - best appreciated in "
            "binoculars or the finderscope - but nearby Mel 101 tucks "
            "into the edge of its field as a modest cluster of 30-40 "
            "stars forming a clear 'figure-8' shape. Comfortably squeezed "
            "into a single field with a small refractor. Not physically "
            "associated: Mel 101 lies ~14x more distant than IC 2602. "
            "(Apr / Jul 2026)"
        ),
    },
    {
        "slug": "ngc-6200-ngc-6204",
        "pair": ("NGC 6200", "NGC 6204"),
        "const": "Ara",
        "coords_a": (251.027, -47.469),
        "coords_b": (251.542, -47.019),
        "ra_hms_a": "16h 44.1m", "dec_dms_a": "-47° 28'",
        "ra_hms_b": "16h 46.2m", "dec_dms_b": "-47° 01'",
        "mag_a": 7.4, "mag_b": 8.2,
        "catalogue_slug_a": "ngc-6200", "catalogue_slug_b": "ngc-6204",
        "thumb_fov_deg": 1.2,
        "thumb_center": (251.284, -47.244),
        "note": (
            "With NGC 6193 centred in the finder, this pair drops "
            "together into one 35 mm field - a great contrasting pair. "
            "NGC 6200 is the tight, densely packed one: 30+ stars, with "
            "a chain of four brighter stars tapering off the top. "
            "NGC 6204 sits on the other side as a small, dense knot "
            "with a triplet of bright stars hanging off one edge. "
            "Observed in the Club 17.5\"; would fit the 12\" field too. "
            "(Sep 2025 & Jul 2026)"
        ),
    },
    {
        "slug": "ngc-6134-hogg-19",
        "pair": ("NGC 6134", "Hogg 19"),
        "const": "Norma",
        "coords_a": (246.950, -49.151),
        "coords_b": (247.238, -49.110),
        "ra_hms_a": "16h 27.8m", "dec_dms_a": "-49° 09'",
        "ra_hms_b": "16h 29.0m", "dec_dms_b": "-49° 07'",
        "mag_a": 7.2, "mag_b": None,
        "catalogue_slug_a": "ngc-6134", "catalogue_slug_b": None,
        "thumb_fov_deg": 0.8,
        "thumb_center": (247.094, -49.131),
        "note": (
            "NGC 6134 is a dense circular disk of 60+ stars across "
            "~10', easy to pick out from the rich Norma star fields "
            "even against a nebulous background. A second, smaller "
            "knot of stars off to one side is the sparse open cluster "
            "Hogg 19, sitting about a quarter of a degree away. "
            "Observed in the Club 17.5\"; would fit the 12\" field too. "
            "Hogg 19 has no catalogued V magnitude. (Jul 2026)"
        ),
    },
]
