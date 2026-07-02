"use client";

import { useEffect, useRef } from "react";
import maplibregl, { Map as MLMap, Marker } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Focus, MapPoint } from "@/lib/types";

const KIND_COLORS: Record<string, string> = {
  flight: "#38bdf8",
  earthquake: "#f87171",
  weather: "#a78bfa",
  place: "#34d399",
};

function markerElement(point: MapPoint): HTMLElement {
  const el = document.createElement("div");
  const color = KIND_COLORS[point.kind] ?? "#e2e8f0";
  if (point.kind === "flight") {
    const rot = (point.heading ?? 0) - 45;
    el.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" style="transform: rotate(${rot}deg)"><path fill="${color}" d="M21 3L3 10.5l7 2.5 2.5 7L21 3z"/></svg>`;
  } else {
    el.style.cssText = `width:12px;height:12px;border-radius:50%;background:${color};border:2px solid #0a0e14;box-shadow:0 0 8px ${color}`;
  }
  el.style.cursor = "pointer";
  return el;
}

export default function MapView({
  points,
  focus,
}: {
  points: MapPoint[];
  focus: Focus | null;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MLMap | null>(null);
  const markersRef = useRef<Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    mapRef.current = new maplibregl.Map({
      container: containerRef.current,
      style: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
      center: [0, 25],
      zoom: 1.6,
      attributionControl: { compact: true },
    });
    mapRef.current.addControl(new maplibregl.NavigationControl(), "top-right");
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = points.map((p) =>
      new maplibregl.Marker({ element: markerElement(p) })
        .setLngLat([p.lon, p.lat])
        .setPopup(new maplibregl.Popup({ offset: 12 }).setText(p.label))
        .addTo(map)
    );
    if (focus) {
      map.flyTo({ center: [focus.lon, focus.lat], zoom: focus.zoom, duration: 1600 });
    }
  }, [points, focus]);

  return <div ref={containerRef} className="h-full w-full" />;
}
