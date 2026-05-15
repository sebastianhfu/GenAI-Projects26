# Dokumentation — Projekt 3 (Educational Video Generation System)

## Projektbeschreibung

Dieses Projekt plant ein System zur automatisierten Erstellung von didaktischen Erklärvideos im Stil einer PowerPoint-Präsentation mit Moderator. Die Idee ist, dass ein Nutzer ein Thema eingibt und das System daraus ein vollständiges Video erzeugt, in dem ein Avatar-basierter Moderator Folien-Inhalte erklärt.

> **Hinweis:** Diese Seite beschreibt ausschließlich den Planungsstand. Keine Implementierung, kein Training und keine Generierung wurden durchgeführt.

---

## Geplante Systemarchitektur

Die Architektur ist als verteiltes System konzipiert, bei dem Hermes als Orchestrierungsagent fungiert und mehrere externe Dienste koordiniert.

### Datenfluss (geplant)

```
┌─────────────────┐
│   Benutzer      │  Gibt Thema ein (z. B. "Was ist ein neuronales Netz?")
└────────┬────────┘
         ▼
┌─────────────────┐
│  Hermes Agent   │  Erzeugt Gliederung, Folien-Text und Sprechscript
└────────┬────────┘
         ▼
┌─────────────────┐     ┌──────────────────────┐
│  Voice-Server   │◄────│ Audio-Datei (gesprochenes Script)
│  (extern)       │     │ Format noch zu klären: WAV? MP3? AAC?
└────────┬────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────────┐
│  Avatar-Server  │◄────│ Video des sprechenden Avatars
│  (extern)       │     │ Format noch zu klären: MP4? WebM? Rohes Bildsequenz?
└────────┬────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────┐
│  Kompositions-  │  Fügt Folien, Avatar-Video und Audio zu einem
│  Pipeline       │  finalen Erklärvideo zusammen (geplant, nicht implementiert)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Finales Video  │  Ausgabe: synchronisiertes Präsentationsvideo
└─────────────────┘
```

### Bisher verfügbar

- Hermes Agent als Orchestrierungssystem (läuft)
- Grundlegende Konzeptidee und diese Planungsdokumentation

### Noch nicht verfügbar / Zukünftig

- Voice-Server: Muss noch bereitgestellt und angebunden werden
- Avatar-Server: Muss noch bereitgestellt und angebunden werden
- Kompositions-Pipeline: Noch nicht implementiert
- Slide-Rendering-Engine: Noch nicht ausgewählt (Manim, Reveal.js, Pandoc-beamer, etc.)

---

## Integration der externen Dienste (Planung)

Da Avatar- und Voice-Systeme auf separaten Servern laufen sollen, müssen Schnittstellen geplant werden. Folgende Kommunikationsansätze sind denkbar:

| Ansatz | Beschreibung | Offene Fragen |
|--------|--------------|---------------|
| **REST API** | Synchrone HTTP-Anfrage mit Audio/Video als Response | Maximale Dateigröße? Timeout bei langer Generierung? |
| **WebSocket API** | Stream-basierte Übertragung für Echtzeit-Feedback | Unterstützen die Server Streaming? |
| **Job-Queue** | Async-Modell: Auftrag einreichen → Status pollen → Ergebnis abholen | Welcher Queue-Mechanismus? Redis? RabbitMQ? Eigenes System? |
| **Polling für Job-Status** | Kombination mit REST: POST zum Starten, GET für Status, GET für Ergebnis | Wie lange wird ein Job gespeichert? Retry-Logik? |
| **Shared Storage** | Generierte Dateien werden in einem gemeinsamen Speicher abgelegt (NFS, S3, SMB) | Wer kümmert sich um Bereinigung alter Dateien? |
| **File Upload/Download Endpoints** | Explizite Upload-/Download-URLs pro Job | Authentifizierung pro Endpunkt? Expiry der URLs? |

### Empfohlene Richtung (vorläufig)

Ein **Job-Queue-Modell mit REST-Polling** scheint für Generierungsaufgaben am robustesten, da Avatar- und Voice-Generierung nicht instantan sind. Die genaue Wahl hängt jedoch von den Fähigkeiten der externen Server ab.

---

## Offene technische Fragen

Die folgenden Punkte müssen geklärt werden, bevor eine Implementierung beginnen kann:

### Voice-Server

1. Welche API bietet der Voice-Server? (REST, gRPC, WebSocket?)
2. Welche Authentifizierung wird erwartet? (API-Key, OAuth, Token?)
3. Welches Eingabeformat benötigt der Server? (Reiner Text? SSML? Mit Prosodie-Markup?)
4. Welche Ausgabeformate liefert der Server? (WAV, MP3, OGG, FLAC? Welche Bitrate?)
5. Gibt es eine Längenbegrenzung pro Anfrage? (Zeichen, Wörter, Sekunden?)
6. Ist Batch-Verarbeitung möglich oder nur einzelne Sätze?

### Avatar-Server

1. Welche API bietet der Avatar-Server?
2. Benötigt der Server nur eine Audio-Datei als Eingabe (Audio-driven lip-sync), oder auch:
   - Ein Prompt / Steuer-Text?
   - Ein Referenzbild des Avatars?
   - Ein Gesichts-Mesh / 3D-Modell?
   - Ein Video als Stil-Referenz?
3. Welche Ausgabeformate liefert der Server? (MP4, WebM, Bildsequenz als ZIP?)
4. Welche Auflösung und Bildrate sind erreichbar?
5. Wie lange dauert die Generierung pro Minute Audio? (Wichtig für Timeout-Planung)
6. Werden mehrere Avatars / Personen unterstützt, oder nur ein spezifischer?

### Datenfluss & Infrastruktur

7. Wie werden generierte Assets zwischen den Servern übertragen? (Base64 in JSON? URL? Shared Storage?)
8. Wo wird das finale Video gerendert? (Lokal auf Hermes-Maschine? Auf einem dedizierten Render-Server?)
9. Welche Latenz ist für ein interaktives Erlebnis akzeptabel? (Minutes? Stunden?)
10. Wie werden Fehler in der Pipeline behandelt? (Retry? Fallback auf Standard-Voice / Standard-Avatar?)
11. Gibt es Speicherplatz- oder Bandbreiten-Einschränkungen zwischen den Servern?

### Rechtliche und ethische Fragen

12. Welche Einwilligungsdokumentation liegt für den verwendeten Avatar (Prof. Uwe Hahne) vor?
13. Welche Lizenzbedingungen gelten für die generierten Videos? (Eigene? Der externen Dienste?)
14. Welche Hinweise müssen in generierten Videos enthalten sein? ("KI-generiert", "Voice-Clone", etc.)
15. Gibt es Einschränkungen bei der öffentlichen Veröffentlichung solcher Videos?

### Folien & Inhalt

16. Welches Tool soll Folien rendern? (Manim für mathematische Animationen? Reveal.js für Web-Slides? Pandoc für statische PDFs?)
17. Wie werden Folien-Inhalte mit Audio-Script synchronisiert? (Zeitstempel? Kapitel-Marker?)
18. Soll der Avatar nur im Vordergrund stehen, oder auch Folien im Hintergrund sichtbar sein?

---

## Mögliche Präsentationsthemen

Für ein späteres Prototyping sollten die Themen kurz genug für ein Demo-Video sein (ca. 1–3 Minuten), aber technisch substanziell genug, um den Nutzen des Systems zu zeigen.

### Kategorien

- Grundlegende Informatik-Konzepte
- Grundlagen der Künstlichen Intelligenz
- Medieninformatik / Computer Graphics
- Mensch-Computer-Interaktion
- Datenschutz und Ethik
- Einführende Programmierkonzepte

### Konkrete Themenvorschläge

| Nr. | Thema | Schätzung: Passend für Kurzvideo? |
|-----|-------|-----------------------------------|
| 1 | Was ist ein neuronales Netz? | ✅ Sehr gut — visuell erklärbar |
| 2 | Wie funktioniert Bildklassifikation? | ✅ Gut — Beispielbilder unterstützen |
| 3 | Was ist eine REST API? | ✅ Gut — Request/Response-Diagramme |
| 4 | Wie rendert ein Computer 3D-Grafik? | ✅ Gut — Pipeline-Schritte visualisierbar |
| 5 | Was ist Datenschutz? | ✅ Gut — Alltagsbeispiele |
| 6 | Wie funktioniert Voice-Cloning? | ✅ Meta — das System erklärt sich selbst |
| 7 | Was ist ein Chatbot? | ✅ Gut — Dialog-Verläufe zeigen |
| 8 | Wie funktioniert ein Empfehlungssystem? | ✅ Gut — Matrix-Darstellung |
| 9 | Überwachtes vs. unüberwachtes Lernen | ✅ Gut — Gegenüberstellung |
| 10 | Wie funktioniert eine Suchmaschine? | ✅ Gut — Index-Crawling-Ranking |
| 11 | Was ist ein Transformer? | ⚠️ Etwas abstrakt, aber mit Animation machbar |
| 12 | Wie funktioniert eine Hash-Funktion? | ✅ Gut — Schritt-für-Schritt-Demo |
| 13 | Was ist ein Version Control System (Git)? | ✅ Gut — Branch-/Merge-Visualisierung |
| 14 | Was ist ein Docker-Container? | ✅ Gut — Container vs. VM vergleichen |
| 15 | Wie funktioniert Public-Key-Kryptographie? | ⚠️ Abstrakt, aber mit Folien erklärbar |

> **Empfohlene Prototyp-Themen:** Nr. 1, 3, 6 oder 10 — diese sind kurz, visuell unterstützbar und für ein breites Publikum verständlich.

---

## Vorgeschlagene Entwicklungsphasen

### Phase 1 — Konzept und Anforderungen

**Ziel:** Klare Rahmenbedingungen definieren, bevor technische Arbeit beginnt.

- [ ] Ziel-Videoformat festlegen (Auflösung, Bildrate, Länge, Zielplattform)
- [ ] Externe Dienste identifizieren und deren Verfügbarkeit prüfen
- [ ] Eingabe- und Ausgabe-Formate definieren (was gibt der Nutzer rein, was kommt raus?)
- [ ] Ein Prototyp-Thema aus der obigen Liste wählen
- [ ] Rechtliche Einwilligungen für Avatar und Voice prüfen

**Ergebnis:** Requirements-Dokument, ausgewähltes Thema, bestätigte Dienst-Verfügbarkeit.

### Phase 2 — Schnittstellenplanung

**Ziel:** API-Verträge und Datenflüsse zwischen Hermes, Voice-Server und Avatar-Server definieren.

- [ ] API-Spezifikation für Voice-Server erstellen (Request/Response-Schema, Auth, Fehlercodes)
- [ ] API-Spezifikation für Avatar-Server erstellen
- [ ] Dateiübertragungsmethode festlegen (Upload-URL, Shared Storage, Base64, etc.)
- [ ] Erwartete Response-Formate dokumentieren (Audio: WAV/MP3? Video: MP4/WebM? Metadaten?)
- [ ] Job-Status-Polling-Schema definieren (wie oft pollen? Welche Status-Codes?)

**Ergebnis:** API-Dokumentation, OpenAPI/Swagger-Spec (optional), Test-Cases für jede Schnittstelle.

### Phase 3 — Prototyp-Pipeline-Design

**Ziel:** Den vollständigen Ablauf vom Thema bis zum Roh-Video planen, ohne die echten Server aufzurufen.

- [ ] Slide-Generation planen: Wie wandelt Hermes ein Thema in strukturierte Folien um?
- [ ] Narrations-Generierung planen: Wie wird aus Folien ein flüssiges Sprechscript?
- [ ] Synchronisation planen: Wie werden Folien, Audio-Timing und Avatar-Video aufeinander abgestimmt?
- [ ] Fallback-Strategien definieren: Was passiert, wenn ein Server ausfällt oder zu langsam ist?

**Ergebnis:** Architektur-Dokument, Sequenzdiagramm, Fehlerbehandlungskonzept.

### Phase 4 — Zukünftige Implementierung

**Ziel:** Die geplante Pipeline mit echten Diensten umsetzen.

> **Hinweis:** Diese Phase setzt voraus, dass Phase 1–3 abgeschlossen sind und die externen Server betriebsbereit sind.

- [ ] Implementierung der Voice-Server-Integration
- [ ] Implementierung der Avatar-Server-Integration
- [ ] Implementierung der Video-Kompositions-Pipeline (Folien + Avatar + Audio)
- [ ] Testing mit echten generierten Assets
- [ ] Iteration und Feinschliff basierend auf Testergebnissen

**Ergebnis:** Lauffähiger Prototyp, der ein Demo-Video für das in Phase 1 gewählte Thema erzeugt.

---

## Lessons Learned

> *Wird ergänzt, sobald Phase 1–3 abgeschlossen sind und erste Erkenntnisse vorliegen.*

## Ergebnisse

!!! note "Work in Progress"
    Ergebnisse werden hier dokumentiert, sobald das Projekt abgeschlossen ist.
    Aktuell liegt nur die Planungsdokumentation vor.
