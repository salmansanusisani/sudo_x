import { useEffect, useState } from 'react'
import { geoGraticule10, geoOrthographic, geoPath } from 'd3-geo'
import { feature } from 'topojson-client'
import type { Topology, GeometryCollection } from 'topojson-specification'
import type { FeatureCollection, Geometry } from 'geojson'
import world from 'world-atlas/countries-110m.json'

const topology = world as unknown as Topology<{ countries: GeometryCollection }>
const countries = (feature(topology, topology.objects.countries) as FeatureCollection<Geometry>).features
const grid = geoGraticule10()

export function Globe({ focused, motion }: { focused: boolean; motion: boolean }) {
  const [zoom, setZoom] = useState(0)
  useEffect(() => {
    const target = focused ? 1 : 0
    if (!motion) { setZoom(target); return }
    let frame = 0
    let start = 0
    // Animate only on a scene change; the idle globe never burns a render loop.
    const from = focused ? 0 : 1
    function step(time: number) {
      if (!start) start = time
      const progress = Math.min((time - start) / 1400, 1)
      const ease = 1 - (1 - progress) ** 3
      setZoom(from + (target - from) * ease)
      if (progress < 1) frame = requestAnimationFrame(step)
    }
    frame = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frame)
  }, [focused, motion])
  const scale = 213 + zoom * 220
  const projection = geoOrthographic().translate([340, 270]).scale(scale).rotate([-14 + zoom * 6, -9]).clipAngle(90)
  const path = geoPath(projection)
  const cities: [string, number, number][] = [['Abuja', 7.3986, 9.0765], ['Lagos', 3.3792, 6.5244]]
  return <svg className="globe" viewBox="0 0 680 540" role="img" aria-label={focused ? 'Geographic map focused on Nigeria, with Abuja and Lagos marked. Offline reference, not live news.' : 'Offline reference globe centered on Africa'}>
    <defs>
      <radialGradient id="ocean"><stop offset="0" stopColor="#102c37"/><stop offset="0.7" stopColor="#0a1c29"/><stop offset="1" stopColor="#08131f"/></radialGradient>
      <radialGradient id="atmosphere"><stop offset="0.82" stopColor="#6dd9e5" stopOpacity="0"/><stop offset="0.94" stopColor="#6dd9e5" stopOpacity="0.08"/><stop offset="1" stopColor="#6dd9e5" stopOpacity="0"/></radialGradient>
      <clipPath id="mapClip"><rect width="680" height="540" rx="4"/></clipPath>
    </defs>
    <g clipPath="url(#mapClip)">
      {!focused && <g className="orbital-lines" fill="none" stroke="#36535f" strokeWidth="0.7">
        <ellipse cx="340" cy="270" rx="295" ry="98" transform="rotate(-25 340 270)" strokeDasharray="2 8"/>
        <ellipse cx="340" cy="270" rx="284" ry="236" transform="rotate(-25 340 270)" opacity="0.4"/>
        <circle cx="340" cy="270" r="237" strokeDasharray="1 11"/>
      </g>}
      <circle cx="340" cy="270" r={scale * 1.08} fill="url(#atmosphere)"/>
      <path d={path({ type: 'Sphere' }) || ''} fill="url(#ocean)" stroke="#416779" strokeWidth="0.8"/>
      <path d={path(grid) || ''} fill="none" stroke="#315264" strokeWidth="0.5" opacity="0.42"/>
      {countries.map(country => <path key={country.id} d={path(country) || ''}
        fill={String(country.id) === '566' ? '#68dfba' : '#183943'}
        stroke={String(country.id) === '566' ? '#beffdf' : '#42616a'} strokeWidth={String(country.id) === '566' ? 1 : 0.55}
        opacity={String(country.id) === '566' ? 0.95 : 0.85}/>) }
      {focused && cities.map(([name, lon, lat], index) => {
        const point = projection([lon, lat])
        if (!point) return null
        return <g key={name} transform={`translate(${point[0]},${point[1]})`}>
          <circle r="8" fill="none" stroke="#d5ffee" opacity="0.45"/><circle r="3" fill="#effff9"/>
          <path d={`M 10 0 h ${index ? -65 : 40}`} fill="none" stroke="#a6d7cf"/>
          <text x={index ? -64 : 56} y="4" textAnchor={index ? 'end' : 'start'} fill="#e2fff4" fontSize="13" fontFamily="monospace">{name.toUpperCase()}</text>
        </g>
      })}
    </g>
  </svg>
}
