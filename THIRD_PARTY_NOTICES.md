# Third-Party Notices

## Geographic Data

The bundled globe uses `world-atlas` 2.0.2's `countries-110m.json`, derived from Natural Earth 1:110m country boundaries. Natural Earth data is public domain. World Atlas is distributed under ISC; its license is included with the dependency. The UI displays attribution; map borders are generalized geographic reference, not a statement on sovereignty or precise event locations.

- https://www.naturalearthdata.com/about/terms-of-use/
- https://github.com/topojson/world-atlas

The fixed Abuja and Lagos coordinates are approximate city reference points, not live event locations. No live headlines or geocoded news are included.

## Interface Dependencies

React/React DOM, D3 Geo, TopoJSON Client, and Lucide provide UI, projection, geometry conversion, and icons. Exact versions are recorded in `ui/package-lock.json`; upstream license files remain in installed packages. Lucide uses the ISC license; D3 Geo uses ISC; TopoJSON Client uses ISC; React uses MIT. Verify all distribution notices when packaging a public release.

No Marvel/Iron Man artwork, voices, soundtrack, logos, or other movie assets are included. Interface geometry and styling were created for SUDO X. System fonts are used; no third-party font requests occur at runtime.
