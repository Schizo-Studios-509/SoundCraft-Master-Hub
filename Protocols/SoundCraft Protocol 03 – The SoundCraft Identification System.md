# SoundCraft Protocol 03 – The SoundCraft Identification System

**Purpose:**  
To define the naming and cataloging scheme for all certified SoundCraft Compositions.

—

## 1. ID Format

SC-YYYY-XX-NNN

| Field | Description |
|———|-————|
| **SC** | System prefix (SoundCraft) |
| **YYYY** | Year of registration (UTC) |
| **XX** | Two- or three-letter composition code |
| **NNN** | Sequential release number |

**Example:** `SC-2025-FL-031` → *The Forging of Light*, 31st registered composition.

—

## 2. Embedding Locations
- WAV metadata (iXML + ID3v2)  
- JSON metadata file  
- README.md documentation  
- Optional ultrasonic watermark (≈ 19.2 kHz, –60 dB)

—

## 3. Registry Purpose
Provides unique, auditable identity, version control, and brand authentication.

—

**Protocol Version:** 1.0 (2025)